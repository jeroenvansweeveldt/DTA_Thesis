import os
import argparse
import pandas as pd
import csv
import statistics
import lxml
from lxml import etree
from xml.etree.ElementTree import Element
from typing import Tuple, Dict

#GLOBALS
HOCR_NS = "{http://www.w3.org/1999/xhtml}"

def process_line(line: Element) -> Tuple:
    """
    Helper function for 'process_file'. This function focuses
    on the individual lines in a page. It retrieves XHTML elements
    on the word and line levels that will help the 'process_file'
    construct a dictionary with all relevant info on an OCR scanned
    page.

    Arguments:
        line (Element): the XHTML element to be processed.
    
    Returns:
        Tuple: A tuple containing relevant values of the page's line.
            line_id = the current line's unique identifier.
            coordinates = the bounding box coordinates of the line within the page.
            line = the words within the line.
            confidence = the OCR's confidence values of each word.
            avg = the calculated mean of the confidence values within the current line.
            stdev = the standard deviation of the confidence values within the current line.
    """
    conf_val, wordlist = [], []
    #retrieve the children of XHTML element 'line'
    children = line.getchildren()
    for child in children:
        #append textual content of child element to list
        wordlist.append(child.text)
        #iterate over the "title" attribute in the 'ocr_word' class
        #the attribute is made up of two parts:
        #'bbox 1312 232 1376 267; x_wconf 88'
        #which are the bounding box coordinates, and the confidence value
        for token in child.get("title").split("; "):
            #split the confidence value token so we can isolate its numeric value
            token = token.split(" ")
        conf_val.append(token[1])
    #cast each element of conf_val as an integer
    conf_val = [int(i) for i in conf_val]
    #get the unique identifier for the 'ocr_line' class
    line_id = line.get('id')
    #get the bounding box coordinates for the 'ocr_line' class
    #which again is part of the 'title' attribute, made up of the following parts:
    #'bbox 226 365 635 397; baseline 0 -5; x_size 33; x_descenders 7; x_ascenders 11'
    coordinates = line.get('title').split(";")
    coordinates = coordinates[0].split(" ")
    coordinates = coordinates[1:] #we only want the numerical values
    line = ' '.join(wordlist)
    confidence = conf_val
    avg = float(round(statistics.mean(conf_val), 2))
    #set default standard deviation to 0.0 and only calculate this value
    #in case there is more than one word in the line to avoid errors
    stdev = 0.0
    if len(conf_val) > 1:
        stdev = round(statistics.stdev(conf_val), 2)

    return (line_id, coordinates, line, confidence, avg, stdev)

def process_file(file: str, writer: csv.writer, file_num: Dict) -> csv.writer:
    """
    Process HOCR-files resulting from Tesseract page scans. With the helper function
    'process_line', all words in every line on the scanned page, along with their
    coordinates and confidence values are extracted. 'Process_file' gathers this
    information into a dictionary, adds to those the page dimensions, and writes the
    information to a data set in the form of a .csv file using the csv.writer object.

    Arguments:
        file (str): the path to the HOCR file to be processed.
        writer (csv.writer): the .csv writer object used to write the extracted data.
        file_num (Dict): a dictionary mapping the filenames to their respective file numbers.

    Returns:
        csv.writer: the csv writer after writing the extracted data.
    """
    #parse the lxml to find the page dimensions.
    tree = lxml.etree.parse(file)
    root = tree.getroot()
    page_info = root.find(f'.//{HOCR_NS}div[@class="ocr_page"]')
    page_info = page_info.get("title")
    file_name = page_info.split('"')
    file_name = file_name[1].split("\\")
    file_name = file_name[-1]
    page_dim = page_info.split(";")
    page_dim = page_dim[1].split(" ")
    page_dim = page_dim[2:]

    #store the line location in a variable
    lines = root.findall(f'.//{HOCR_NS}span[@class="ocr_line"]')

    #iterate over the lines in the files to gather relevant information
    for l in lines:
        #call the process_line function and unpack the returned tuple into
        #separate variables representing the processed information for that line
        (line_id, coordinates, line, confidence, avg, stdev) = process_line(l)
        #print(coordinates)
        #print(line)
        #print(confidence)

        #skip pages that are flagged as "onnuttig" (useless)
        if file_num[file_name] == "ONNUTTIG":
            continue

        #construct a dictionary containing the processed information for the current line
        row = {
            "Filename": file_name,
            "File number": file_num[file_name],
            "Line id": line_id,
            "Line": line,
            "Confidence": confidence,
            "Average": avg,
            "StDev": stdev
        }
        #create list of page locations representing the page coordinates
        coor_pages = ["page left", "page top", "page right", "page bottom"]
        #simultaneously iterate over the page dimensions (page_dim) and
        #their respective representations in the coor_pages list
        #and add these to the row dictionary, using the coor_page titles
        #as keys and the page_dims as values
        for cp,title in zip(page_dim, coor_pages):
            row[title] = cp
        #do the same for the line coordinates extracted from the process_line function
        coor_titles = ["left", "top", "right", "bottom"]
        for ct,title in zip(coordinates, coor_titles):
            row[title] = ct

        #write the 'row' dictionary as a csv
        writer.writerow(row)
    return writer

def main(input_file: str, output_file: str, folder_path: str) -> csv.writer:
    #define a dictionary that will shape the features of dataset
    headers = {
            "Filename": "Filename",
            "File number": "File number",
            "page left": "Page left",
            "page top": "Page top",
            "page right": "Page right",
            "page bottom": "Page bottom",
            "Line id": "Line id",
            "Line": "Line",
            "Confidence": "Confidence",
            "Average":"Average",
            "StDev": "Standard deviation",
            "left": "Line left",
            "top": "Line top",
            "right": "Line right",
            "bottom": "Line bottom"
    }

    #implement copy number increment to prevent overwriting files
    filename, extention = os.path.splitext(output_file)
    copy_number = 0
    while os.path.exists(output_file):
        if copy_number == 0:
            output_file = f"{filename}{extention}"
        else:
            output_file = f"{filename}({copy_number}){extention}"
        copy_number += 1

    #open a csv writer and write the dictionary keys as headers for
    #the rows in the dataset

    with open(output_file, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(headers)

        #Not possible to iterate as we normally would over the csv.reader object.
        #Stating 'file_num[file_map["filename"]] = [file_map["pagenr"]]' will result in
        #errors due to the csv reader object only recognising the headers --
        #we need the filenames and their respective page numbers, though!

        #Therefore, we first loop over the headers, then choose to continue.
        #To access the actual information we need (filenames + page numbers),
        #we need to skip the header row.
        with open(input_file) as csvfile:
            file_map = csv.reader(csvfile, delimiter=";")
            file_num = {}
            for i, row in enumerate(file_map):
                if i == 0: #this is the header row
                    continue
                #assign the second element [1](filenumber) of the row
                #to the dictionary file_num using the first element [0]
                #(filename) as a key
                file_num[row[0]] = row[1]

        for f in os.listdir(folder_path):
            #.DS_Store is a hidden file annoyingly generated on MacOS systems
            #and will crash the loop if taken into consideration
            if f == ".DS_Store":
                continue
            else:
                file_path = os.path.join(folder_path, f)
                #write .csv file using the information processed by
                #the process_file function, and assign file-/page number
                #mapping
                writer = process_file(file_path, writer, file_num)

    print(f"New file created: '{output_file}'.")
    return writer

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Extract data from HOCR output files and combine them with\
filename + pagenumber .csv file to create a dataset to perform logical layout analysis.")
    p.add_argument("input_file", help="Path to input .csv with filenames and their corresponding pagenumbers.")
    p.add_argument("output_file", help="Output .csv filename generated by this script.")
    p.add_argument("folder_path", help="Path to the folder containing the HOCR output files.")    
    args = p.parse_args()

    output_folder = "../logical_layout_analysis/data"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_filename = os.path.join(output_folder, args.output_file)

    main(args.input_file, output_filename, args.folder_path)