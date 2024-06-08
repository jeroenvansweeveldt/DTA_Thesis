import os
import json
import argparse
import pandas as pd
import lxml
from lxml import etree
from xml.etree.ElementTree import Element
from collections import OrderedDict
import utils

#globals
HOCR_NS = "{http://www.w3.org/1999/xhtml}"
CURRENT_DICT = {}
VALID_PARAGRAPHS = ["BODY",
                    "FRENCH",
                    "SIGN-OFF",
                    "POSTSCRIPT"
                    ]
SEPARATORS = ["@", #id and title
              "+", #language and body
              "ù", #title and date_of_reply
              "§", #id and body
              "=", #body and sign-off
              "#", #bill and body
              ]
LANGUAGE_MAPPING = {"[D]": "DUTCH",
                    "[E]": "ENGLISH",
                    "[F]": "FRENCH",
                    "[G]": "GERMAN"
                    }

def separate_id_ti(id_part, title_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "ID" and "TITLE" tags
    """
    CURRENT_DICT["ID"] += id_part
    CURRENT_DICT["TITLE"] += title_part

def separate_la_bo(language_part, body_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "LANGUAGE" and "BODY" tags
    """
    if CURRENT_DICT["LANGUAGE"]:
        CURRENT_DICT["LANGUAGE"] += " " + language_part
    else:
        CURRENT_DICT["LANGUAGE"] += language_part

    if CURRENT_DICT["BODY"]:
        CURRENT_DICT["BODY"] += " " + body_part
    else:
        CURRENT_DICT["BODY"] += body_part
    
    CURRENT_DICT["TEXT"] += body_part

def separate_ti_da(title_part, date_reply_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "TITLE" and "DATE_OF_REPLY" tags
    """
    if CURRENT_DICT["TITLE"]:
        CURRENT_DICT["TITLE"] += " " + title_part
    else:
        CURRENT_DICT["TITLE"] += title_part
    
    if CURRENT_DICT["DATE_OF_REPLY"]:
        CURRENT_DICT["DATE_OF_REPLY"] += " " + date_reply_part
    else:
        CURRENT_DICT["DATE_OF_REPLY"] += date_reply_part

def separate_id_bo(id_part, body_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "ID" and "BODY" tags
    """
    if CURRENT_DICT["ID"]:
        CURRENT_DICT["ID"] += " " + id_part
    else:
        CURRENT_DICT["ID"] += id_part

    if CURRENT_DICT["BODY"]:
        CURRENT_DICT["BODY"] += " " + body_part
    else:
        CURRENT_DICT["BODY"] += body_part
    
    CURRENT_DICT["TEXT"] += body_part

def separate_bo_si(body_part, signoff_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "BODY" and "SIGN-OFF" tags
    """
    if CURRENT_DICT["BODY"]:
        CURRENT_DICT["BODY"] += " " + body_part
    else:
        CURRENT_DICT["BODY"] += body_part

    if CURRENT_DICT["SIGN-OFF"]:
        CURRENT_DICT["SIGN-OFF"] += " " + signoff_part
    else:
        CURRENT_DICT["SIGN-OFF"] += signoff_part + " "
    
    CURRENT_DICT["TEXT"] += f" {body_part} {signoff_part}"

def separate_bi_bo(bill_part, body_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "BILL" and "BODY" tags
    """
    if CURRENT_DICT["BILL"]:
        CURRENT_DICT["BILL"] += " " + bill_part
    else:
        CURRENT_DICT["BILL"] += bill_part

    if CURRENT_DICT["BODY"]:
        CURRENT_DICT["BODY"] += " " + body_part
    else:
        CURRENT_DICT["BODY"] += body_part
    
    CURRENT_DICT["TEXT"] += body_part

def generate_corpus(input_dir) -> OrderedDict:
    """
    Create a list of dictionaries, each dictionary entry representing
    a letter from the corpus.
    """
    # CURRENT_DICT must be set as a global to prevent an out-of-bounds error
    global CURRENT_DICT

    corpus_dict = []
    filenumber_prefix = "m-d_"
    filenumber_suffix = 1
    current_chapter = ""

    # make sure you don't let the script iterate over the files in randomised sequence (default),
    file_names = sorted(os.listdir(input_dir))
    for file_name in file_names:
        if file_name.endswith(".hocr"):
                filepath = os.path.join(input_dir, file_name)

                tree = lxml.etree.parse(filepath)
                root = tree.getroot()

                page_info = root.find(f'.//{HOCR_NS}div[@class="ocr_page"]')
                pagenumber = page_info.get("page_number")

                # set variables to control addition of newlines between paragraphs
                first_line = True
                first_paragraph = True

                for paragraph in root.findall(f'.//{HOCR_NS}p[@class="ocr_par"]'):
                    # to control the addition of unnecessary newlines, we must exclude
                    # paragraphs that 1) start at the top of the page (which is why we retrieve the id)
                    # and 2) paragraphs that follow annotation tags not incorporated in the dictionary
                    valid_paragraph = False
                    paragraph_id = paragraph.get("id")

                    for line in paragraph.findall(f'.//{HOCR_NS}span[@class="ocr_line"]'):
                        # make sure the script gathers the corrected lines instead of the original ones
                        line_correction = line.get("line_correction")
                        textline = line_correction if line_correction != "nan" else line.get("line")
                        annotation = line.get("annotation")

                        if annotation in VALID_PARAGRAPHS:
                            valid_paragraph = True

                        # in the Marescoe-David corpus, the first line of the letter scanned
                        # by the OCR is either the date of arrival, or the date
                        # hence we use these annotations to mark the beginning of each letter
                        if annotation == "DATE_OF_ARRIVAL" or annotation == "DATE":
                            CURRENT_DICT = OrderedDict({"SERIAL_NR": f"{filenumber_prefix}{filenumber_suffix}",
                                                        "ID": "",
                                                        "TITLE": "",
                                                        "PAGE": pagenumber,
                                                        "SENDER_RAW": "",
                                                        "ADDRESSEE_RAW": "",
                                                        "SALUTATION": "",
                                                        "SIGN-OFF": "",
                                                        "POSTSCRIPT": "",
                                                        "PLACE_OF_WRITING": "",
                                                        "DATELINE": "",
                                                        "DATE": "",
                                                        "BODY": "",
                                                        "FOOTNOTE": "",
                                                        "TEXT": "",
                                                        "EXCHANGE_RATE": "",
                                                        "BILL": "",
                                                        "CHAPTER": current_chapter,
                                                        "LANGUAGE": "",
                                                        "YEAR": "",
                                                        "DATE_OF_WRITING": "",
                                                        "DATE_OF_ARRIVAL": "",
                                                        "DATE_OF_REPLY": ""
                                                        })
                            if annotation == "DATE_OF_ARRIVAL":
                                CURRENT_DICT["DATE_OF_ARRIVAL"] = textline
                            if annotation == "DATE":
                                CURRENT_DICT["DATE"] = textline

                            corpus_dict.append(CURRENT_DICT)
                            filenumber_suffix += 1

                        # update the chapter for every dictionary entry
                        elif annotation == "CHAPTER":
                            current_chapter = textline

                        # now that the basics for the current dictionary are prepared
                        # we handle the multi-line annotations    
                        elif annotation == "MULTI":
                            for symbol in SEPARATORS:
                                if symbol in textline:
                                    separator = symbol
                        
                            if separator:
                                parts = textline.split(separator, 1)
                                if len(parts) == 2:
                                    if separator == "@":
                                        separate_id_ti(parts[0], parts[1])
                                    elif separator == "+":
                                        separate_la_bo(parts[0], parts[1])
                                    elif separator == "ù":
                                        separate_ti_da(parts[0], parts[1])
                                    elif separator == "§":
                                        separate_id_bo(parts[0], parts[1])
                                    elif separator == "=":
                                        separate_bo_si(parts[0], parts[1])
                                    elif separator == "#":
                                        separate_bi_bo(parts[0], parts[1])

                        else:
                            # add remaining keys/annotations to the dictionary
                            # they must not contain useless info such as NOISE and HEADER
                            # concatenate with a newline tag to follow the books layout
                            # but make an exception for the "LANGUAGE" tags
                            if annotation not in ["NOISE", "HEADER", "LANGUAGE"]:
                                CURRENT_DICT[annotation] = (CURRENT_DICT.get(annotation, "") + textline).strip() + "\n"
                            if annotation in ["LANGUAGE"]:
                                CURRENT_DICT[annotation] = (CURRENT_DICT.get(annotation, "") + textline).strip()

                            # create one final key, TEXT, which contains all text included in the letter
                            CURRENT_DICT.setdefault("TEXT", "").strip()

                            # make sure the SALUTATION annotation appears ahead of the other keys in the TEXT values
                            # the Marescoe-David .xml is a mess in terms of paragraph allocation
                            # and needs a bit of handholding to get everything in the right spot
                            if annotation == "SALUTATION":
                                CURRENT_DICT["TEXT"] = textline.strip() + "\n" + CURRENT_DICT["TEXT"]

                            if annotation in VALID_PARAGRAPHS:
                                # add "[F]" tag to "LANGUAGE" key when a "FRENCH" annotation tag is found in the letter's body
                                if annotation == "FRENCH":
                                    if "[F]" not in CURRENT_DICT["LANGUAGE"]:
                                        if CURRENT_DICT["LANGUAGE"]:
                                            CURRENT_DICT["LANGUAGE"] += " & [F]"
                                        else:
                                            CURRENT_DICT["LANGUAGE"] = "[F]"

                                # add newline symbols where a new paragraph begins
                                # do not add these newlines if the annotation is in the list of irrelevant annotations
                                if not first_line and valid_paragraph and not (first_paragraph and paragraph_id == "par_1_1"):
                                    # concatenate with a newline to follow the book's layout
                                    CURRENT_DICT["TEXT"] += "\n"
                                else:
                                    first_line = False
                                    first_paragraph = False
                                CURRENT_DICT["TEXT"] += textline.strip()                      

                    if valid_paragraph:
                        CURRENT_DICT["TEXT"] += "\n"
                
                first_paragraph = True

    return corpus_dict

def clean_corpus(corpus_dict: OrderedDict) -> dict:
    """
    Remove unnecessary keys from the list of dictionaries,
    and apply some rudimentary text cleaning
    and finally an extra key with the word count of the "TEXT" key values
    """
    filtered_corpus_dict = []

    for entry in corpus_dict:
        # filter on keys relevant to the corpus
        filtered_entry = {key: value for key, value in entry.items() if key not in ["BODY", "FRENCH", "NOISE", "HEADER"]}
        #filter out keys with empty values
        filtered_entry = {key: value for key, value in filtered_entry.items() if value}

        if "TITLE" in filtered_entry:
            cleaned_title = filtered_entry["TITLE"].replace(" tO ", " to ").replace(" t0 ", " to ")
            title_split = cleaned_title.split("to", 1)
            if len(title_split) == 2:
                filtered_entry["SENDER_RAW"] = title_split[0].strip()
                filtered_entry["ADDRESSEE_RAW"] = title_split[1].strip()
            else:
                filtered_entry["SENDER_RAW"] = title_split[0].strip()
                filtered_entry["ADDRESSEE_RAW"] = ""
        
        if "DATELINE" in filtered_entry:
            if filtered_entry["DATELINE"].strip().endswith("[UNDATED]"):
                filtered_entry["DATE_OF_WRITING"] = filtered_entry["DATELINE"].split()[-1]
                filtered_entry["PLACE_OF_WRITING"] = " ".join(filtered_entry["DATELINE"].split()[:-1])
            else:
                filtered_entry["DATE_OF_WRITING"] = " ".join(filtered_entry["DATELINE"].split()[-3:])
                filtered_entry["PLACE_OF_WRITING"] = " ".join(filtered_entry["DATELINE"].split()[:-3])
                filtered_entry["YEAR"] = filtered_entry["DATELINE"].split()[-1]

        if "DATE" in filtered_entry:
            filtered_entry["YEAR"] = filtered_entry["DATE"].split()[-1]

            if filtered_entry["DATE"].strip().startswith("LONDON"):
                filtered_entry["DATELINE"] = filtered_entry["DATE"]
                filtered_entry["DATE_OF_WRITING"] = " ".join(filtered_entry["DATE"].split()[-3:])
                filtered_entry["PLACE_OF_WRITING"] = " ".join(filtered_entry["DATE"].split()[:-3])

            else:
                filtered_entry["DATE_OF_WRITING"] = filtered_entry["DATE"]
            
            # no more need for the "DATE" key now that the info in this annotation
            # has been distributed
            del filtered_entry["DATE"]
        
        if not "LANGUAGE" in filtered_entry:
            filtered_entry["LANGUAGE"] = "[E]"

        if "LANGUAGE" in filtered_entry:
            language_tags = filtered_entry["LANGUAGE"].split(" & ")
            language_names = [LANGUAGE_MAPPING.get(tag.strip(), tag.strip()) for tag in language_tags]
            filtered_entry["LANGUAGE"] = " & ".join(language_names)

        if filtered_entry["ID"].strip().startswith("[A"):
            filtered_entry["CHAPTER"] = "APPENDIX"

        reordered_entry = OrderedDict()
        for key in CURRENT_DICT.keys():
            if key in filtered_entry:
                reordered_entry[key] = filtered_entry[key]
        reordered_entry["SENDER_RAW"] = filtered_entry.get("SENDER_RAW", "")
        reordered_entry["ADDRESSEE_RAW"] = filtered_entry.get("ADDRESSEE_RAW", "")
        reordered_entry["SALUTATION"] = filtered_entry.get("SALUTATION", "")

        # remove trailing newlines in the key values
        for key in filtered_entry:
            if key in reordered_entry:
                reordered_entry[key] = reordered_entry[key].lstrip('\n')
                reordered_entry[key] = reordered_entry[key].rstrip('\n')

        filtered_corpus_dict.append(dict(reordered_entry))

    clean_keys = ["SALUTATION",
                  "SIGN-OFF",
                  "POSTSCRIPT",
                  "FOOTNOTE",
                  "TEXT",
                  "EXCHANGE_RATE",
                  "BILL"
                  ]

    for entry in filtered_corpus_dict:
        for key in clean_keys:
            if key in entry:
                # we'll only use clean_spelling, because the liberal
                # use of hyphens in the Marescoe-David corpus might
                # cause the remove_hyphens function to royally fuck
                # up the layout
                entry[key] = utils.clean_spelling(entry[key])

    for entry in filtered_corpus_dict:
        if "TEXT" in entry:
            text = entry["TEXT"]
            n_words = utils.tokenize(text)
            entry["N_WORDS"] = n_words

    return filtered_corpus_dict

def save_files(dict, output_dir, output_file):
    output_path = os.path.join(output_dir, output_file)
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="UTF-8") as file:
        json.dump(dict, file, indent=2)

def main():
    p = argparse.ArgumentParser(description="Create a corpus of letter correspondence from the .hocr corpus master files. \
This script is adapted to work with the Marescoe-David corpus.")
    p.add_argument("--input_dir", type=str, default="../corpus/master_marescoe-david", help="Path to the input directory.")
    p.add_argument("--output_dir", type=str, default="../corpus", help="Name of the output directory.")

    args = p.parse_args()
    corpus_dict = generate_corpus(args.input_dir)
    corpus_dict = clean_corpus(corpus_dict)

    save_files(corpus_dict, args.output_dir, "corpus_marescoe-david.json")
    print(f"'corpus_marescoe-david.json' saved in {args.output_dir}")

if __name__ == "__main__":
    main()