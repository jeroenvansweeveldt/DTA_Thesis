import pandas as pd
import argparse

def clean_text_field(text):
    # Replace newline characters with spaces
    cleaned_text = text.replace("\n", " ")
    # Remove leading and trailing whitespaces at the beginning and end of the entire text
    cleaned_text = cleaned_text.strip()
    return cleaned_text

def extract_metadata(df):
    # Extract metadata fields from the DataFrame
    metadata_list = []

    for index, row in df.iterrows():
        metadata = {col: clean_text_field(str(row[col])) for col in df.columns}
        metadata_list.append(metadata)

    return metadata_list

def write_to_txt(metadata_list, output_file):
    # Write metadata to a tab-delimited text file
    with open(output_file, "w", encoding="utf-8") as file:
        # Write header
        file.write("\t".join(metadata_list[0].keys()) + "\n")

        # Write data
        for metadata in metadata_list:
            file.write("\t".join(map(str, metadata.values())) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract metadata from Excel table and write to a flat text file.")
    parser.add_argument("input_excel_file", help="Input Excel file name")
    parser.add_argument("output_txt_file", help="Output text file name")

    args = parser.parse_args()

    input_excel_file = args.input_excel_file
    output_txt_file = args.output_txt_file

    # Read the Excel file into a DataFrame
    df = pd.read_excel(input_excel_file)

    # Extract metadata
    metadata_list = extract_metadata(df)

    # Write metadata to a tab-delimited text file
    write_to_txt(metadata_list, output_txt_file)

    print("Metadata extracted and written to", output_txt_file)