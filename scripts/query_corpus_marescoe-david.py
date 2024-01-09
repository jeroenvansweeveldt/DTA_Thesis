import json, os, argparse

p = argparse.ArgumentParser()
p.add_argument("inputfile")
p.add_argument("metafile")
p.add_argument("outputfile")
args = p.parse_args()


# marescoe
def read_metadata(metafile):
	metalines = open(metafile,"r",encoding="utf-8").readlines()
	metadic = {}
	for line in metalines[1:]:
		line = line.strip().split("\t")
		id = line[0]
		print(id)
		record = {"sender": line[12],
			"addressee": line[14],
			"sender-addressee_pair": line[28],
			"date": "-".join([line[35],line[36],line[37]]),
			"year": line[38],
			"language":line[10],
			"gender_sender": line[24],
			"gender_addressee": line[25],
			"gender_pair": line[26],
			"connection_type": line[27],
			"generation_sender": line[16],
			"generation_addressee": line[20],
			"sender_is_older": line[18],
			"sender_over_40": line[17],
			"addressee_over_40": line[21],
			"age_gap_over_20": line[23]
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
queries = ["god","jesus","lord","almighty","father","saint","dicu","dieu"]
meta = read_metadata("corpora/marescoe-david_metadata.txt")
opf = open("marescoe-david_dataset.txt","w",encoding="utf-8")
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
	id = record.get("ID")
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
			opf.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(id,
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


