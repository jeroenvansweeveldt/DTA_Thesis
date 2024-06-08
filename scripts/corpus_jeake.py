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
INVALID_PARAGRAPHS = ["CHAPTER",
                      "FOOTNOTE",
                      "TITLE",
                      "ID",
                      "NOISE",
                      "HEADER",
                      "LATIN"
                      ]
SEPARATORS = ["&", #title and id
              "ù", #dateline and sign-off
              "€", #date and sender_raw
              "%", #sign-off and sender_raw
              "£", #addressee_raw and dateline
              "$", #dateline and sender_raw
              ]
LANGUAGE_MAPPING = {"[E]": "ENGLISH",
                    "[L]": "LATIN",
                    }

def separate_ti_id(title_part, id_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "ID" and "TITLE" tags
    """
    CURRENT_DICT["TITLE"] += " " + title_part
    CURRENT_DICT["ID"] += id_part

def separate_dl_so(dateline_part, signoff_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "DATELINE" and "SIGN-OFF" tags
    """
    if CURRENT_DICT["DATELINE"]:
        CURRENT_DICT["DATELINE"] += " " + dateline_part
    else:
        CURRENT_DICT["DATELINE"] += dateline_part

    if CURRENT_DICT["SIGN-OFF"]:
        CURRENT_DICT["SIGN-OFF"] += " " + signoff_part
    else:
        CURRENT_DICT["SIGN-OFF"] += signoff_part
    
    CURRENT_DICT["TEXT"] += f"{dateline_part}\n{signoff_part}"

def separate_da_sr(date_part, sender_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "DATE" and "SENDER" tags
    """
    if CURRENT_DICT["DATE"]:
        CURRENT_DICT["DATE"] += " " + date_part
    else:
        CURRENT_DICT["DATE"] += date_part
    
    if CURRENT_DICT["SENDER_RAW"]:
        CURRENT_DICT["SENDER_RAW"] += " " + sender_part
    else:
        CURRENT_DICT["SENDER_RAW"] += sender_part
    
    CURRENT_DICT["TEXT"] += f"{date_part}\n{sender_part}"

def separate_so_sr(signoff_part, sender_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "SIGN-OFF" and "SENDER" tags
    """
    if CURRENT_DICT["SIGN-OFF"]:
        CURRENT_DICT["SIGN-OFF"] += " " + signoff_part
    else:
        CURRENT_DICT["SIGN-OFF"] += signoff_part
    
    if CURRENT_DICT["SENDER_RAW"]:
        CURRENT_DICT["SENDER_RAW"] += " " + sender_part
    else:
        CURRENT_DICT["SENDER_RAW"] += sender_part
    
    CURRENT_DICT["TEXT"] += f"{signoff_part}\n{sender_part}"

def separate_ad_dl(addressee_part, dateline_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "ADDRESSEE_RAW" and "DATELINE" tags
    """
    if CURRENT_DICT["ADDRESSEE_RAW"]:
        CURRENT_DICT["ADDRESSEE_RAW"] += " " + addressee_part
    else:
        CURRENT_DICT["ADDRESSEE_RAW"] += addressee_part

    if CURRENT_DICT["DATELINE"]:
        CURRENT_DICT["DATELINE"] += " " + dateline_part
    else:
        CURRENT_DICT["DATELINE"] += dateline_part
    
    CURRENT_DICT["TEXT"] += f"{addressee_part}\n{dateline_part}"

def separate_dl_sr(dateline_part, sender_part):
    """
    Separates MULTI-annotated line.
    Used for lines that contain both "DATELINE" and "SENDER" tags
    """
    if CURRENT_DICT["DATELINE"]:
        CURRENT_DICT["DATELINE"] += " " + dateline_part
    else:
        CURRENT_DICT["DATELINE"] += dateline_part

    if CURRENT_DICT["SENDER_RAW"]:
        CURRENT_DICT["SENDER_RAW"] += " " + sender_part
    else:
        CURRENT_DICT["SENDER_RAW"] += sender_part
    
    CURRENT_DICT["TEXT"] += f"{dateline_part}\n{sender_part}"

def generate_corpus(input_dir) -> OrderedDict:
    """
    Create a list of dictionaries, each dictionary entry representing
    a letter from the corpus.
    """
    # CURRENT_DICT must be set as a global to prevent an out-of-bounds error
    global CURRENT_DICT

    corpus_dict = []
    filenumber_prefix = "j_"
    filenumber_suffix = 1
    current_chapter = ""

    # make sure you don't let the script iterate over the files in randomised sequence (default),
    # otherwise it will assign wrong values to keys, resulting in Tartarean mayhem
    # like Jeake's dad signing off letters to his son with "your loving wife"
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

                        if annotation not in INVALID_PARAGRAPHS:
                            valid_paragraph = True

                        # we use the annotation TITLE coupled with the first opened bracket of the textline of Title ("[")
                        # we can thus prevent a redundant dictionary being created if there are two subsequent textlines
                        # with a TITLE annotation
                        if "TITLE" in annotation and textline.startswith('['):
                            CURRENT_DICT = OrderedDict({"SERIAL_NR": f"{filenumber_prefix}{filenumber_suffix}",
                                                        "ID": "",
                                                        "TITLE": textline,
                                                        "PAGE": pagenumber,
                                                        "SENDER": "",
                                                        "SENDER_RAW": "",
                                                        "ADDRESSEE": "",
                                                        "ADDRESSEE_RAW": "",
                                                        "SALUTATION": "",
                                                        "SIGN-OFF": "",
                                                        "POSTSCRIPT": "",
                                                        "ADDRESSLINE": "",
                                                        "DATELINE": "",
                                                        "DATE": "",
                                                        "NOTES": "",
                                                        "LATIN": "",
                                                        "FOOTNOTE": "",
                                                        "BODY": "",
                                                        "TEXT": "",
                                                        "CHAPTER": current_chapter,
                                                        "LANGUAGE": ""
                                                        })
                            corpus_dict.append(CURRENT_DICT)
                            filenumber_suffix += 1
                        
                        # update the chapter for every dictionary entry
                        elif annotation == "CHAPTER":
                            current_chapter = textline

                        elif annotation == "LATIN":
                            if "[L]" not in CURRENT_DICT["LANGUAGE"]:
                                CURRENT_DICT["LANGUAGE"] = "[L]"

                        # now that the basics for the current dictionary are prepared
                        # we handle the multi-line annotations    
                        elif annotation == "MULTI":
                            for symbol in SEPARATORS:
                                if symbol in textline:
                                    separator = symbol
                        
                            if separator:
                                parts = textline.split(separator, 1)
                                if len(parts) == 2:
                                    if separator == "&":
                                        separate_ti_id(parts[0], parts[1])
                                    elif separator == "ù":
                                        separate_dl_so(parts[0], parts[1])
                                    elif separator == "€":
                                        separate_da_sr(parts[0], parts[1])
                                    elif separator == "%":
                                        separate_so_sr(parts[0], parts[1])
                                    elif separator == "£":
                                        separate_ad_dl(parts[0], parts[1])
                                    elif separator == "$":
                                        separate_dl_sr(parts[0], parts[1])

                        else:
                            # add remaining keys/annotations to the dictionary
                            # they must not contain useless info such as NOISE and HEADER
                            # return an empty (default) value if no annotation is found in CURRENT_DICT
                            # concatenate with a newline rather than whitespace to follow the book's layout 
                            if annotation not in ["NOISE", "HEADER"]:
                                CURRENT_DICT[annotation] = (CURRENT_DICT.get(annotation, "") + textline).strip() + "\n"

                            # create one final key, TEXT, which contains all text included in the letter
                            CURRENT_DICT.setdefault("TEXT", "").strip()

                            if annotation not in INVALID_PARAGRAPHS:
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
        filtered_entry = {key: value for key, value in entry.items() if key not in ["BODY", "NOISE", "HEADER"]}
        #filter out keys with empty values
        filtered_entry = {key: value for key, value in filtered_entry.items() if value}

        if "SENDER" in filtered_entry:
            filtered_entry["SENDER_RAW"] = filtered_entry.pop("SENDER")
        if "ADDRESSEE" in filtered_entry:
            filtered_entry["ADDRESSEE_RAW"] = filtered_entry.pop("ADDRESSEE")

        if not "LANGUAGE" in filtered_entry:
            filtered_entry["LANGUAGE"] = "[E]"
        else:
            filtered_entry["LANGUAGE"] += " & [E]"

        # yes I know first defining the languages in tags such as "[E]" and then
        # converting them to their full names is a bit of a convolutional and unnessecary
        # operation, but I wanted to have everything consistent and I only came up with
        # doing this after I went with the regular tags first and then realised the
        # desirability of having the tags written in full names instead
        # so I'm going to need you to get all the way off my back about this
        if "LANGUAGE" in filtered_entry:
            language_tags = filtered_entry["LANGUAGE"].split(" & ")
            language_names = [LANGUAGE_MAPPING.get(tag.strip(), tag.strip()) for tag in language_tags]
            filtered_entry["LANGUAGE"] = " & ".join(language_names)

        reordered_entry = OrderedDict()
        for key in CURRENT_DICT.keys():
            if key in filtered_entry:
                reordered_entry[key] = filtered_entry[key]

        # remove trailing newlines in the key values
        for key in filtered_entry:
            if key in reordered_entry:
                reordered_entry[key] = reordered_entry[key].lstrip('\n')
                reordered_entry[key] = reordered_entry[key].rstrip('\n')

        filtered_corpus_dict.append(dict(reordered_entry))

    clean_keys = ["SALUTATION",
                  "SIGN-OFF",
                  "POSTSCRIPT",
                  "NOTES",
                  "FOOTNOTE",
                  "TEXT"
                  ]

    for entry in filtered_corpus_dict:
        for key in clean_keys:
            if key in entry:
                entry[key] = utils.clean_punct(entry[key])
                entry[key] = utils.remove_hyphens(entry[key])
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
This script is adapted to work with the Jeake corpus.")
    p.add_argument("--input_dir", type=str, default="../corpus/master_jeake", help="Path to the input directory.")
    p.add_argument("--output_dir", type=str, default="../corpus", help="Name of the output directory.")

    args = p.parse_args()
    corpus_dict = generate_corpus(args.input_dir)
    corpus_dict = clean_corpus(corpus_dict)

    save_files(corpus_dict, args.output_dir, "corpus_jeake.json")
    print(f"'corpus_jeake.json' saved in {args.output_dir}")

if __name__ == "__main__":
    main()