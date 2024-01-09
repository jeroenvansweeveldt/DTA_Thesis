import json, os, argparse

p = argparse.ArgumentParser()
p.add_argument("inputfile")
p.add_argument("metafile")
p.add_argument("outputfile")
args = p.parse_args()



def read_metadata(metafile):
	metalines = open(metafile,"r",encoding="utf-8").readlines()
	metadic = {}
	for line in metalines[1:]:
		line = line.strip().split("\t")
		id = line[2]
		print(line[39])
		record = {"sender": line[24] if line[24] != "nan" else "",
            "addressee": line[26] if line[26] != "nan" else "",
            "sender-addressee_pair": line[40] if line[40] != "nan" else "",
            "date": line[8] if line[8] != "nan" else "",
            "year": line[9] if line[9] != "nan" else "",
            "language": line[19] if line[19] != "nan" else "",
			"gender_sender": line[36] if line [36] != "nan" else "",
			"gender_addressee": line[37] if line [37] != "nan" else "",
            "gender_pair": line[38] if line[38] != "nan" else "",
            "connection_type": line[39] if line[39] != "nan" else "",
            "generation_sender": line[28] if line[28] != "nan" else "",
            "generation_addressee": line[32] if line[32] != "nan" else "",
            "sender_is_older": line[30] if line[30] != "nan" else "",
            "sender_over_40": line[29] if line[29] != "nan" else "",
			"addressee_over_40": line[33] if line[33] != "nan" else "",
            "age_gap_over_20": line[35] if line[35] != "nan" else ""
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

WINDOW_SIZE = 30
queries = ["god","jesus","lord","almighty"]
meta = read_metadata("corpora/jeake_metadata.txt")
opf = open("jeake_dataset.txt","w",encoding="utf-8")
opf.write("NR\t\
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
PAGE\t\
LENGTH\t\
TOKEN_ID\t\
REL_TOKEN_POS\t\
QUERY\t\
LEFT\t\
HIT\t\
RIGHT\n")

records = json.load(open(args.inputfile,"r",encoding="utf-8"))

for nr,record in enumerate(records):
	text = record.get("TEXT")
	id = record.get("NR")
	if "PAGE" in record:
		page = record.get("PAGE")
	else:
		page = "NA"
	tokens = tokenize(text)
	#print(tokens)
	hits = {}
	for i,token in enumerate(tokens):
		token = token.lower()
		for query in queries:
			if query in token:
				if query in hits:
					hits[query].append(i)
				else:
					hits[query] = [i]
	for query,indices in hits.items():
		for index in indices:
			token_id = "%s.%s_%s"%(id,index,index)
			left = tokens[max(index-WINDOW_SIZE,0):index]
			hit = tokens[index]
			right = tokens[index+1:min(index+WINDOW_SIZE+1,len(tokens)-1)]
			nr = int(nr)
			opf.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(id,
																							 meta[id]["sender"],
																							 meta[id]["addressee"],
																							 meta[id]["sender-addressee_pair"],
																							 meta[id]["date"],
																							 meta[id]["year"],
																							 meta[id]["language"],
																							 meta[id]["gender_sender"],
																							 meta[id]["gender_addressee"],
																							 meta[id]["gender_pair"],
																							 meta[id]["connection_type"],
																							 meta[id]["generation_sender"],
																							 meta[id]["generation_addressee"],
																							 meta[id]["sender_is_older"],
																							 meta[id]["sender_over_40"],
																							 meta[id]["addressee_over_40"],
																							 meta[id]["age_diff_over_20"],
																							 page,
																							 len(tokens),
																							 token_id,round(100*index/len(tokens),2),
																							 query,
																							 " ".join(left),
																							 hit,
																							 " ".join(right)))
opf.close()


