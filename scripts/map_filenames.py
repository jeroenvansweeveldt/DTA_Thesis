import os
import argparse
import pandas as pd
from pandas import DataFrame

def create_filemap(input_folder: str) -> DataFrame:
    """
    Create Excel file to map page numbers to the filenames.
    The script makes sure that the hidden file ".DS_Store" generated on MacOS systems
    is not included.
    """
    filenames = [filename for filename in os.listdir(input_folder) if filename != ".DS_Store"]
    filenames.sort()

    filemap = DataFrame({"Filename": filenames,
                         "Pagenr": ""})
    
    return filemap

def save_file(filemap: DataFrame, output_filename: str, output_folder: str):
    """
    Save the Excel file while making sure the file does not get overwritten.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created '{output_folder}' folder.")

    filename, extension = os.path.splitext(output_filename)
    output_path = os.path.join(output_folder, output_filename)

    copy_number = 0
    while os.path.exists(output_path):
        if copy_number == 0:
            output_filename = f"{filename}{extension}"
        else:
            output_filename = f"{filename}({copy_number}){extension}"
        copy_number += 1
        output_path = os.path.join(output_folder, output_filename)
  
    print(f"File '{output_filename}' written to '{output_folder}'.")
    return filemap.to_excel(output_path, index=False)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Generate Excel file to map pagenumber to its respective filename.")
    p.add_argument("input_folder", help="Path to the input folder.")
    p.add_argument("output_filename", help="Filename of the output")

    args = p.parse_args()

    output_folder = "../logical_layout_analysis/data"
    filemap = create_filemap(args.input_folder)
    save_file(filemap, args.output_filename, output_folder)