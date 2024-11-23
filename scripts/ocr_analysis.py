import difflib
from difflib import SequenceMatcher
import os.path
from lxml import etree
import json
import csv
import numpy as np
import pandas as pd
from collections import Counter
import argparse

def open_files(file):
    with open(file, encoding='UTF-8') as stream:
        r = stream.read()
        #change long dashes into short ones
        r = r.replace("—", "-")
        #change stylised hyphens into regular ones
        r = r.replace("‘", "'").replace("’", "'").replace("“", "'").replace("”", "'")

    s_chars = r
    s_words = r.split()
    s_lines = s_line = r.splitlines()
    
    return (s_chars, s_words, s_lines)


def generate_report(file_a, file_b, filename, label):

    """
    Creates a comparison report for two files.
    
    The function takes five arguments: the first two being the two files you want
    to compare and that have been read into the into the environment;
    the latter two are the pathnames of the corresponding files.
    Finally a label is added to differenciate the report types.
    
    A .html file is created (named diff_report by default). Pathname where the file
    will be written to should be adapted to suit your needs.
    """

    subdirs = {
        "_characters": "compare_chars",
        "_words": "compare_words",
        "_lines": "compare_lines"
        }
    if label not in subdirs:
        raise ValueError(f"Invalid label '{label}'. Expected one of {list(subdirs.keys())}.")

    subdir = subdirs[label]
    subdir_output = os.path.join(f"../ocr_analysis/", subdir)
    os.makedirs(subdir_output, exist_ok=True)

    output_dir = os.path.join(subdir_output, f"{filename}{label}.html")

    comparison = difflib.HtmlDiff().make_file(file_a, file_b)
    with open(output_dir, 'w') as compare_report:
        compare_report.write(comparison)
        compare_report.close

    return comparison

def pair_difference(comparison):

    """
    This function extracts the contents from the comparison report
    and pairs the differences in a list.
    """

    comparison = comparison.replace("&nbsp;"," ")
    root = etree.fromstring(comparison)

    table = root.findall(".//table")[0]

    pairs = []
    for row in table.findall(".//tr"):
        cells = row.findall(".//td")
        gold_cell = cells[2]
        if len(gold_cell.getchildren())>0:
            gold = gold_cell[0].text
        else:
            gold = gold_cell.text
        predicted_cell = cells[5]
        if len(predicted_cell.getchildren())>0:
            predicted = predicted_cell[0].text
        else:
            predicted = predicted_cell.text
        pairs.append((gold, predicted))
        
    return pairs

def seq_ratio(file_a, file_b):
    
    """
    Returns a score number representing how close two files match each other.
    The function takes two arguments, one for each file you wish to compare.
    """

    seq = SequenceMatcher(a=file_a, b=file_b)
    return seq.ratio()

def update_d(d, previous, current):
    if previous not in d: #if the previous key is not in the dictionary
        d[previous] = {} #make a nested dictionary for that key
    if current in d[previous]: #if the current key is in the previous dictionary
        d[previous][current] += 1 #increment value of current key
    else:
        d[previous][current] = 1 #otherwise, set value of current key to one
    return d

def separate_collection(collection, files_with_errors):

    """
    separate files from different collections
    and compare them to a gold standard.

    The function takes two arguments:
    
    - Collection chooses from which
    collection the input/output is compared (Jeake or Marescoe, or
    any other collection that might be added in the future).
    - Files_with_errors can be used to either summon a dictionary of
    all of the sequence matching results from all files across all
    collections (use '{}' as argument),
    or you can input a specific file as argument to return the
    sequence matching scores of that file. This argument can also
    be used stand-alone, outside of the function to call the
    nested dictionary.
    """

    files = os.listdir("../ocr_analysis/gold_standard/%s"%collection)
    #print(files)
    files = [f[3:-4] for f in files if f[-4:] == ".txt"]
    for f in files:
        current_errors = {}
        current_errors["file"] = f
        current_errors["collection"] = collection
        labels = ["_characters", "_words", "_lines"]
        output_path_gold = "../ocr_analysis/gold_standard/%s/gs_%s.txt" %(collection, f)
        output_path_abby = "../ocr_output/txt_%s_abbyy/abb_%s.txt" %(collection, f)
        output_path_tess = "../ocr_output/txt_%s_tesseract/%s.txt" %(collection, f)
        if not os.path.exists(output_path_gold):
            print(f"Gold standard file not found: {output_path_gold}")
            continue

        # Open and separate the gold standard using the OPENING AND SPLIT functions.
        (gold_chars,gold_words,gold_lines) = open_files(output_path_gold)

        # Open and separate the Abby files using the OPENING AND SPLIT FILES functions.
        (abby_chars,abby_words,abby_lines) = open_files(output_path_abby)

        # Create sequence ratios for every split level using the SEQUENCE MATCHING function.
        current_errors["abby_ratio_chars"] = seq_ratio(abby_chars, gold_chars)
        current_errors["abby_ratio_words"] = seq_ratio(abby_words, gold_words)
        current_errors["abby_ratio_lines"] = seq_ratio(abby_lines, gold_lines)
        
        # Open and separate the Tesseract files using the OPENING AND SPLIT FILES functions.
        (tess_chars,tess_words,tess_lines) = open_files(output_path_tess)

        # Create sequence ratios for every split level using the SEQUENCE MATCHING function.
        current_errors["tess_ratio_chars"] = seq_ratio(tess_chars, gold_chars)
        current_errors["tess_ratio_words"] = seq_ratio(tess_words, gold_words)
        current_errors["tess_ratio_lines"] = seq_ratio(tess_lines, gold_lines)

        files_with_errors[f] = current_errors

        # Generate comparison reports:
        generate_report(abby_chars, gold_chars, "%s_"%collection+f+"_abbyy", labels[0])
        generate_report(abby_words, gold_words, "%s_"%collection+f+"_abbyy", labels[1])
        generate_report(abby_lines, gold_lines, "%s_"%collection+f+"_abbyy", labels[2])
        generate_report(tess_chars, tess_chars, "%s_"%collection+f+"_tesseract", labels[0])
        generate_report(tess_words, tess_words, "%s_"%collection+f+"_tesseract", labels[1])
        generate_report(tess_lines, tess_lines, "%s_"%collection+f+"_tesseract", labels[2])

    return files_with_errors

def create_char_diff(path, outpath):
    os.makedirs(outpath, exist_ok=True)
    d = {}
    files = os.listdir(path)

    for filename in files:
        if filename.endswith("characters.html"):
            file_path = os.path.join(path, filename)
            with open(file_path, "r", encoding="utf-8") as html_file:
                comparison_content = html_file.read()

            print(f"Processing {filename}...")
            differences = pair_difference(comparison_content)
            diff_dict = {}
            for item in differences:
                diff_dict = update_d(diff_dict, item[0], item[1])

            json_output_path = os.path.join(outpath, f"{filename[:-5]}.json")
            with open(json_output_path, "w", encoding="utf-8") as outfile:
                json.dump(diff_dict, outfile, indent=2)          

def main():
    p = argparse.ArgumentParser(description="Analyse the OCR output.")
    p.add_argument("--output_dir", default="../ocr_analysis", help="Specify the output directory for the script.")
    p.add_argument("--collections", default=["jeake", "marescoe-david"], help="Specify the collection you wish to analyse.")
    p.add_argument("--errors", action="store_true", help="Create .json files to examine what words and characters the OCR swapped.")
    args = p.parse_args()

    files_with_errors = {}
    for collection in args.collections:
        print(f"Building comparison reports for {collection} collection.")
        try:
            files_with_errors = separate_collection(collection, files_with_errors)
        except Exception as e:
            print(f"Error building comparison reports for {collection} collection: {e}")
    print(f"Comparison reports written to {args.output_dir}.")
    for f, results in files_with_errors.items():
        print(f"Error ratio for file {f}: {results.values()}.")

    csv_output = os.path.join(args.output_dir, "error_ratios.csv")
    with open(csv_output, "w", newline="") as csvfile:
        field_names=results.keys()
        val = results.values()
        csv_writer = csv.DictWriter(csvfile, dialect="excel", fieldnames=field_names)
        csv_writer.writeheader()
        for f, results in files_with_errors.items():
            csv_writer.writerow(results)
        print(f"File 'error_ratios.csv' written to {args.output_dir}.")
    
    if args.errors:
        output_path_chars = os.path.join(args.output_dir, "error_analysis_chars")
        create_char_diff(
            path=os.path.join(args.output_dir, "compare_chars"),
            outpath=output_path_chars
        )
        print(f"Error analysis for OCR characters created in {output_path_chars}.")

if __name__ == "__main__":
    main()