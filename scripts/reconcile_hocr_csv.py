import os
import argparse
import lxml
from lxml import etree
import pandas as pd

#globals
HOCR_NS = "{http://www.w3.org/1999/xhtml}"

def reconcile_data(hocr_dir, df, map_filename_df, output_dir):
    annotated_df = pd.read_csv(df,
                 delimiter=";",
                 encoding="UTF-8")
    
    map_filenames = pd.read_csv(map_filename_df,
                            delimiter=";")
    
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(hocr_dir):
        if file_name.endswith(".hocr"):
            filepath = os.path.join(hocr_dir, file_name)

            tree = lxml.etree.parse(filepath)
            root = tree.getroot()

            page_info = root.find(f'.//{HOCR_NS}div[@class="ocr_page"]')
            hocr_file_name = page_info.get("title").split('"')[1].split("\\")[-1]

            match_filemap = map_filenames[map_filenames["filename"] == hocr_file_name]
            if not match_filemap.empty:
                if match_filemap.iloc[0]["pagenr"] == "ONNUTTIG":
                    continue

            match_filename = annotated_df[annotated_df["Filename"] == hocr_file_name]
            if not match_filename.empty:
                page_number = match_filename.iloc[0]["File number"]
            else:
                continue

            page_info.set("page_number", str(page_number))

            for page_elem in page_info:
                line_elements = page_elem.findall(f'.//{HOCR_NS}span[@class="ocr_line"]')

                for line_elem in line_elements:

                    hocr_line = line_elem.get("id")
                    match_line = annotated_df[(annotated_df["Filename"] == hocr_file_name) & (annotated_df["Line id"] == hocr_line)]
                    
                    id_correction = None
                    line_content = None
                    line_correction = None

                    #some entries in the dataframe are lacking the first line (id "line_1_1")
                    #investigating the .hocr files reveals that these belong to the headers.
                    #a conditional statement must prevent the script from crashing.
                    if not match_line.empty:
                        line_content = match_line.iloc[0]["Line"]
                        annotation = match_line.iloc[0]["Annotation"]
                    else:
                        annotation = "HEADER"
                    
                    #set conditionals to make the script work on both datasets
                    if not match_line.empty and "Line correction" in match_line.columns:
                        line_correction = match_line.iloc[0]["Line correction"]
                    else:
                        line_correction = None
                    if not match_line.empty and "Line id correction" in match_line.columns:
                        id_correction = match_line.iloc[0]["Line id correction"]
                    else:
                        id_correction = None
                
                    #strictly it's not necessary to append the content words of the line to its
                    #upper class level, this is more laziness on my part because I don't want to
                    #include yet another nested loop to iterate over the "ocr_word" level when
                    #putting together the .json corpus
                    #in fact, doing this while removing the necessecity to loop over a deeper
                    #.xhtml level is computationally less demanding
                    if id_correction is not None:
                        line_elem.set("id_correction", str(id_correction))

                    line_elem.set("line", str(line_content))

                    if line_correction is not None:
                        line_elem.set("line_correction", str(line_correction))

                    line_elem.set("annotation", str(annotation))

                    print(f"{file_name} written to {output_dir}.")

            output_filename = os.path.join(output_dir, file_name)
            tree.write(output_filename, pretty_print=True)

def main():
    p = argparse.ArgumentParser(description="Reconcile data from the annotated logical layout analysis dataframe with the original .hocr output files to create master files for the corpora.")
    p.add_argument("hocr_dir", type=str, help="Path to the folder containing the OCR output files in .hocr format.")
    p.add_argument("df", type=str, help="Path to the annotated logical layout analysis .csv file.")
    p.add_argument("map_filename_df", type=str, help="Path to the .csv containing the mapping of the filenames and their respective page numbers.")
    p.add_argument("output_dir", type=str, help="Path to the output folder.")
    args = p.parse_args()

    reconcile_data(args.hocr_dir, args.df, args.map_filename_df, args.output_dir)

if __name__ == "__main__":
    main()