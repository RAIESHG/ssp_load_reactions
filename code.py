import pandas as pd
import streamlit as st
import traceback
import sys

# Configure page
st.set_page_config(page_title="Support Reaction Analyzer", layout="wide")
st.title("Support Reaction Analysis Tool")

# Add debugging information
if st.checkbox("Show debug information"):
    st.write("Python version:", sys.version)
    st.write("Pandas version:", pd.__version__)
    st.write("Streamlit version:", st.__version__)

uploaded_file = st.file_uploader("Upload your Excel file:", type="xlsx")

if uploaded_file:
    try:
        # Let user select sheet if multiple sheets exist
        xl_file = pd.ExcelFile(uploaded_file)
        if len(xl_file.sheet_names) > 1:
            sheet_name = st.selectbox("Select sheet:", xl_file.sheet_names)
        else:
            sheet_name = xl_file.sheet_names[0]
        
        st.info(f"Reading sheet: {sheet_name}")
        df_raw = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)
        st.info(f"Raw data shape: {df_raw.shape}")

        # More flexible header detection for reactions
        keywords_reactions = ['Node', 'L/C', 'FX', 'FY', 'FZ']
        header_row_rxn = None
        
        # Try to find header row with required columns
        for idx, row in df_raw.iterrows():
            row_str = row.astype(str).str.upper().values
            if all(any(keyword.upper() in cell for cell in row_str) for keyword in keywords_reactions):
                header_row_rxn = idx
                break
        
        # If not found, try with just some keywords
        if header_row_rxn is None:
            for idx, row in df_raw.iterrows():
                row_str = row.astype(str).str.upper().values
                if any('NODE' in cell for cell in row_str) and any('FX' in cell for cell in row_str):
                    header_row_rxn = idx
                    break

        # Detect header row for load cases
        keywords_lc = ['L/C', 'Type', 'Name']
        header_row_lc = None
        
        for idx, row in df_raw.iterrows():
            row_str = row.astype(str).str.upper().values
            if all(any(keyword.upper() in cell for cell in row_str) for keyword in keywords_lc):
                header_row_lc = idx
                break
        
        # If not found, try with just L/C and Name
        if header_row_lc is None:
            for idx, row in df_raw.iterrows():
                row_str = row.astype(str).str.upper().values
                if any('L/C' in cell for cell in row_str) and any('NAME' in cell for cell in row_str):
                    header_row_lc = idx
                    break

        if header_row_rxn is not None:
            st.success(f"✅ Reactions data found in row {header_row_rxn + 1}")
            
            df_reactions = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_row_rxn)
            df_reactions = df_reactions.iloc[1:].copy()
            
            # Handle different column names
            node_col = None
            lc_col = None
            fx_col = None
            fy_col = None
            fz_col = None
            
            for col in df_reactions.columns:
                col_str = str(col).upper()
                if 'NODE' in col_str:
                    node_col = col
                elif 'L/C' in col_str or 'LOAD' in col_str:
                    lc_col = col
                elif 'FX' in col_str:
                    fx_col = col
                elif 'FY' in col_str:
                    fy_col = col
                elif 'FZ' in col_str:
                    fz_col = col
            
            if node_col and lc_col and fx_col and fy_col and fz_col:
                df_reactions['Node'] = df_reactions[node_col].ffill().astype(int)
                df_reactions['L/C'] = pd.to_numeric(df_reactions[lc_col], errors='coerce')
                df_reactions['FX'] = pd.to_numeric(df_reactions[fx_col], errors='coerce')
                df_reactions['FY'] = pd.to_numeric(df_reactions[fy_col], errors='coerce')
                df_reactions['FZ'] = pd.to_numeric(df_reactions[fz_col], errors='coerce')
                df_reactions.dropna(subset=['L/C'], inplace=True)
                df_reactions['L/C'] = df_reactions['L/C'].astype(int)
                
                if st.checkbox("Show processed reactions data"):
                    st.write("Processed reactions data:")
                    st.dataframe(df_reactions.head())
            else:
                st.error("Required columns not found. Please ensure your file has Node, L/C, FX, FY, and FZ columns.")
                st.error(f"Found columns: {list(df_reactions.columns)}")
                st.stop()
        else:
            st.error("Reactions data not found. Please check your file format.")
            st.error("Available columns in raw data:")
            st.write(df_raw.head())
            st.stop()

        if header_row_lc is not None:
            st.success(f"✅ Load cases data found in row {header_row_lc + 1}")
            
            df_load_cases = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_row_lc)
            
            # Handle different column names for load cases
            lc_col_lc = None
            name_col = None
            
            for col in df_load_cases.columns:
                col_str = str(col).upper()
                if 'L/C' in col_str or 'LOAD' in col_str:
                    lc_col_lc = col
                elif 'NAME' in col_str:
                    name_col = col
            
            if lc_col_lc and name_col:
                df_load_cases['L/C'] = pd.to_numeric(df_load_cases[lc_col_lc], errors='coerce')
                df_load_cases.dropna(subset=['L/C'], inplace=True)
                df_load_cases['L/C'] = df_load_cases['L/C'].astype(int)
                df_load_cases.dropna(subset=[name_col], inplace=True)
                lc_name_map = dict(zip(df_load_cases['L/C'], df_load_cases[name_col]))
            else:
                st.warning("Load cases data not found or incomplete. Using default load case names.")
                lc_name_map = {}
        else:
            st.warning("Load cases data not found. Using default load case names.")
            lc_name_map = {}

        st.subheader("Define Support Groups")
        support_groups = {}
        with st.form("support_group_form"):
            names = st.text_area("Enter support names and nodes (format: P1:1,2,3; P2:4,5,6)")
            submitted = st.form_submit_button("Analyze")
            if submitted:
                try:
                    entries = names.split(';')
                    for entry in entries:
                        if ':' in entry:
                            name, nodes = entry.split(':')
                            node_list = [int(n.strip()) for n in nodes.split(',') if n.strip()]
                            support_groups[name.strip()] = node_list
                except Exception as e:
                    st.error(f"Invalid format. Please follow the instructions. Error: {str(e)}")

        additional_deadload_lcs = st.text_input("Enter additional dead load L/Cs (comma-separated):")
        additional_deadload_lcs = [int(x.strip()) for x in additional_deadload_lcs.split(',') if x.strip().isdigit()]

        def get_max_abs_with_lc(df_node_reactions, force_col):
            try:
                if df_node_reactions.empty or df_node_reactions[force_col].isnull().all():
                    return None, None, None
                max_abs_idx = df_node_reactions[force_col].abs().idxmax()
                max_value = df_node_reactions.loc[max_abs_idx, force_col]
                lc_num = df_node_reactions.loc[max_abs_idx, 'L/C']
                lc_name = lc_name_map.get(lc_num, f"LC {int(lc_num)}")
                return max_value, lc_num, lc_name
            except Exception as e:
                st.error(f"Error in get_max_abs_with_lc: {str(e)}")
                return None, None, None

        def analyze(df_reactions, support_groups, additional_deadload_lcs):
            try:
                results = {}
                for support_name, node_list in support_groups.items():
                    results[support_name] = {'nodes_data': {}, 'overall_max': {}, 'per_load_case_max': {}}
                    overall = {f: None for f in ['FX', 'FY', 'FZ']}
                    lc_max = {f: None for f in ['FX', 'FY', 'FZ']}
                    lc_name = {f: None for f in ['FX', 'FY', 'FZ']}
                    for node in node_list:
                        df_node = df_reactions[df_reactions['Node'] == node]
                        node_data = {}
                        for f in ['FX', 'FY', 'FZ']:
                            val, lc, name = get_max_abs_with_lc(df_node, f)
                            node_data[f] = {'value': val, 'lc': lc, 'lc_name': name}
                            if val is not None and (overall[f] is None or abs(val) > abs(overall[f])):
                                overall[f] = val
                                lc_max[f] = lc
                                lc_name[f] = name
                        results[support_name]['nodes_data'][node] = node_data

                    results[support_name]['overall_max'] = {
                        f: {'value': overall[f], 'lc': lc_max[f], 'lc_name': lc_name[f]}
                        for f in ['FX', 'FY', 'FZ']
                    }

                    df_group = df_reactions[df_reactions['Node'].isin(node_list)]
                    for lc in sorted(df_group['L/C'].unique()):
                        df_lc = df_group[df_group['L/C'] == lc]
                        name = lc_name_map.get(lc, f"LC {lc}")
                        results[support_name]['per_load_case_max'][lc] = {
                            'lc_name': name,
                            'FX': df_lc['FX'].abs().max() if not df_lc['FX'].isnull().all() else None,
                            'FY': df_lc['FY'].abs().max() if not df_lc['FY'].isnull().all() else None,
                            'FZ': df_lc['FZ'].abs().max() if not df_lc['FZ'].isnull().all() else None
                        }

                    if additional_deadload_lcs:
                        sums = {}
                        for f in ['FX', 'FY', 'FZ']:
                            total = 0.0
                            for lc in additional_deadload_lcs:
                                df_lc = df_group[df_group['L/C'] == lc]
                                if not df_lc.empty and not df_lc[f].isnull().all():
                                    total += df_lc[f].abs().max()
                            sums[f] = total if total > 0 else None
                        results[support_name]['additional_deadload_sum'] = sums

                return results
            except Exception as e:
                st.error(f"Error in analyze function: {str(e)}")
                st.error(f"Traceback: {traceback.format_exc()}")
                return {}

        if submitted and support_groups:
            try:
                results = analyze(df_reactions, support_groups, additional_deadload_lcs)
                for support_name, data in results.items():
                    st.subheader(f"Results for {support_name}")
                    st.markdown("**Overall Max Reactions**")
                    st.write(pd.DataFrame(data['overall_max']).T)
                    if 'additional_deadload_sum' in data:
                        st.markdown("**Sum of Max Values for Additional Dead Loads**")
                        st.write(data['additional_deadload_sum'])
                    st.markdown("**Per Load Case Maximums**")
                    per_lc = pd.DataFrame.from_dict(data['per_load_case_max'], orient='index')
                    st.dataframe(per_lc)
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.error(f"Traceback: {traceback.format_exc()}")
                
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
else:
    st.info("Please upload an Excel file to begin analysis.")
