import os
import json
import argparse

#globals
WINDOW_SIZE = 30
QUERIES = ["god",
		   "jesus",
		   "lord",
		   "almighty",
		   "father",
		   "saint",
		   "dieu"
		   ]

def read_metadata(metadata_file):
	metalines = open(metadata_file, "r", encoding="UTF-8").readlines()
	metadic = {}
	for line in metalines[1:]:
		line = line.strip().split("\t")
		id = line[0]
		record = {"sender": line[22] if line[22] != "nan" else "",
            "addressee": line[23] if line[23] != "nan" else "",
            "sender-addressee_pair": line[37] if line[37] != "nan" else "",
            "date": line[15] if line[15] != "nan" else "",
            "year": int(float(line[14])) if line[14] != "nan" else "",
            "language": line[13] if line[13] != "nan" else "",
			"gender_sender": line[28] if line [28] != "nan" else "",
			"gender_addressee": line[29] if line [29] != "nan" else "",
            "gender_pair": line[38] if line[38] != "nan" else "",
            "connection_type": line[30] if line[30] != "nan" else "",
            "generation_sender": line[24] if line[24] != "nan" else "",
            "generation_addressee": line[26] if line[26] != "nan" else "",
            "sender_is_older": line[31] if line[31] != "nan" else "",
            "sender_over_40": line[33] if line[33] != "nan" else "",
			"addressee_over_40": line[34] if line[34] != "nan" else "",
			"age_gap": int(float(line[35])) if line[35] != "nan" else "",
            "age_gap_over_20": line[36] if line[36] != "nan" else ""
		}
		metadic[id] = record

	return metadic


def tokenize(text):
    lines = text.split("\n")
    tokens = []
    for line in lines:
        unhidden_tokens = [token for token in line.split(" ") if len(token) > 0]
        tokens.extend(unhidden_tokens)
        
    return tokens

if __name__ == "__main__":
	p = argparse.ArgumentParser(description="Query the corpus for instances referring to the divine. Optimised to work with the Jeake corpus.")
	p.add_argument("--input_file", type=str, default="../corpus/corpus_marescoe-david.json", help="Path to the corpus .json file.")
	p.add_argument("--metadata_file", type=str, default="../metadata/metadata_marescoe-david.txt", help="Path to the .txt metadata file.")
	p.add_argument("--output_file", type=str, default="dataset_marescoe-david.txt", help="Name of the output file.")
	args = p.parse_args()

	input_file = args.input_file
	metadata_file = args.metadata_file
	output_file = args.output_file
	output_dir = "../datasets"
	if not os.path.exists(output_dir):
		os.makedirs(output_dir, exist_ok=True)
	
	output_path = os.path.join(output_dir, output_file)

	meta = read_metadata(metadata_file)
	open_file = open(output_path, "w", encoding="UTF-8")
	open_file.write("NR\t\
SENDER\t\
ADDRESSEE\t\
SENDER-ADDRESSEE_PAIRS\t\
DATE\t\
YEAR\t\
LANGUAGE\t\
GENDER_SENDER\t\
GENDER_ADDRESSEE\t\
GENDER_PAIR\t\
CONNECTION_TYPE\t\
GENERATION_SENDER\t\
GENERATION_ADDRESSEE\t\
SENDER_IS_OLDER\t\
SENDER_OVER_40\t\
ADDRESSEE_OVER_40\t\
AGE_GAP_OVER_20\t\
AGE_GAP\t\
PAGE\t\
LENGTH\t\
TOKEN_ID\t\
REL_TOKEN_POS\t\
QUERY\t\
LEFT\t\
HIT\t\
RIGHT\n")

	records = json.load(open(input_file, "r", encoding="UTF-8"))

	for nr,record in enumerate(records):
		text = record.get("TEXT")
		id = record.get("SERIAL_NR")
		if not text:
			print(f"Record {id} has no data in its 'TEXT' field and will not be queried.")
			continue
		if "PAGE" in record:
			page = record.get("PAGE")
		else:
			page = "NA"
		tokens = tokenize(text)
		hits = {}
		for i,token in enumerate(tokens):
			token = token.lower()
			for query in QUERIES:
				if query in token:
					if query in hits:
						hits[query].append(i)
					else:
						hits[query] = [i]
		for query,indices in hits.items():
			for index in indices:
				token_id = "%s.%s_%s"%(id, index, index)
				left = tokens[max(index-WINDOW_SIZE, 0):index]
				hit = tokens[index]
				right = tokens[index+1:min(index+WINDOW_SIZE+1, len(tokens)-1)]
				nr = int(nr)
				open_file.write(
					f'{id}\t'
					f'{meta[id]["sender"]}\t'
					f'{meta[id]["addressee"]}\t'
					f'{meta[id]["sender-addressee_pair"]}\t'
					f'{meta[id]["date"]}\t{meta[id]["year"]}\t'
					f'{meta[id]["language"]}\t'
					f'{meta[id]["gender_sender"]}\t'
					f'{meta[id]["gender_addressee"]}\t'
					f'{meta[id]["gender_pair"]}\t'
					f'{meta[id]["connection_type"]}\t'
					f'{meta[id]["generation_sender"]}\t'
					f'{meta[id]["generation_addressee"]}\t'
					f'{meta[id]["sender_is_older"]}\t'
					f'{meta[id]["sender_over_40"]}\t'
					f'{meta[id]["addressee_over_40"]}\t'
					f'{meta[id]["age_gap_over_20"]}\t'
					f'{meta[id]["age_gap"]}\t'
					f'{page}\t{len(tokens)}\t'
					f'{token_id}\t'
					f'{round(100*index/len(tokens),2)}\t'
					f'{query}\t'
					f'{" ".join(left)}\t'
					f'{hit}\t'
					f'{" ".join(right)}\n'
				)
	print(f"{output_file} written to {output_dir}.")
	open_file.close()