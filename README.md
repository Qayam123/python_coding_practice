This is a series of python files I have created to learn Python OOPS concepts and use it efficiently
Following are the steps to Extract a file and convert it into csv format for Further analysis or transformation purpose

# Install deps
pip install pandas pyarrow openpyxl xlrd lxml

# Convert a single file
python tabular_to_csv.py --input /path/to/file.xlsx --out ./csv_out

# Convert a folder (recursively)
python tabular_to_csv.py --input /path/to/folder --out ./csv_out --recursive

# Only certain types
python tabular_to_csv.py --input /path/to/fpython tabular_to_csv.py --input /path/to/folder --out ./csv_out --recursive --pattern "*.parquet"

# Chunk for big files
