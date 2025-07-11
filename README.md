# Support Reaction Analysis Tool

A Streamlit application for analyzing structural support reactions from Excel files.

## Features

- Upload Excel files with reaction data
- Automatic detection of data headers
- Support group definition and analysis
- Maximum reaction force calculations
- Per-load-case analysis
- Additional dead load calculations

## Deployment Instructions

### For Streamlit Cloud

1. **Repository Setup**
   - Ensure your repository is public or you have a paid Streamlit Cloud account
   - Make sure `code.py` is in the root directory
   - Include `requirements.txt` with all dependencies

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file path to: `code.py`
   - Deploy

### For Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the App**
   ```bash
   streamlit run code.py
   ```

## Troubleshooting

### Common Deployment Issues

1. **Missing Dependencies**
   - Ensure `requirements.txt` includes all necessary packages
   - Check that package versions are compatible

2. **File Upload Issues**
   - The app supports `.xlsx` files only
   - Maximum file size is 200MB (configurable in `.streamlit/config.toml`)

3. **Data Processing Errors**
   - Enable debug information checkbox to see detailed error messages
   - Check that your Excel file has the required columns (Node, L/C, FX, FY, FZ)

4. **Memory Issues**
   - Large files may cause memory problems
   - Consider splitting large datasets into smaller files

### Debug Information

The app includes a "Show debug information" checkbox that displays:
- Python version
- Pandas version
- Streamlit version
- File processing details
- Data shapes and column information

## File Format Requirements

Your Excel file should contain:
- **Reactions Data**: Columns for Node, L/C (Load Case), FX, FY, FZ
- **Load Cases Data**: Columns for L/C and Name (optional)

The app will automatically detect headers and process the data accordingly.

## Support

If you encounter issues:
1. Check the debug information
2. Verify your Excel file format
3. Try with a smaller test file first
4. Check the Streamlit Cloud logs for detailed error messages 