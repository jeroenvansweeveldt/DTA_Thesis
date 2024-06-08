import os
import argparse
from bs4 import BeautifulSoup

def reorder_xml(input_dir, output_dir=None):
    if output_dir is None:
        output_dir = input_dir
    
    os.makedirs(output_dir, exist_ok = True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".hocr"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            with open(input_path, "r", encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'xml')
    
            lines_to_move = []
            for line in soup.find_all("span", class_="ocr_line"):
                id_correction = line.get("id_correction")
                if id_correction and id_correction != "nan":
                    lines_to_move.append(line)

            for line in lines_to_move:
                id_correction = line.get("id_correction")
                target_id = id_correction[:-2]
                target_line = soup.find(id=target_id)
                
                if target_line:
                    parent = line.parent.extract()
                    target_line.parent.insert_after(parent)
                
            with open(output_path, "w", encoding="UTF-8") as file:
                file.write(str(soup))

            print(f"{filename}'s .xml was reordered in {output_dir}.")

def main():
    p = argparse.ArgumentParser(description="Reorder the .xml elements of a .hocr file to ensure that all letter info \
is clustered correctly when running the scripts to create the corpora.")
    p.add_argument("input_dir", type=str, help="Path the the input folder.")
    p.add_argument("--output_dir", type=str, help="Path to the output folder. Optional.")
    args = p.parse_args()

    reorder_xml(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()