import re

def clean_punct(text: str) -> str:
    """
    Normalises stylised hyphens, apostrophes, and punctuation marks.

    Arguments:
        text (str): The text containing the symbols to be normalised.

    Returns:
        text (str): The text with normalised symbols.
    """
    del_chars = ["©",
                 "®",
                 "™"
                 ]
    
    text = text.replace("—", "-")
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace('“', '"').replace('”', '"')
    
    for char in del_chars:
        text = text.replace(char, "")

    return text

def remove_hyphens(text: str) -> str:
    """
    Eliminates hyphenated words that appear at the end of a textline (in our case, row)
    and combines the separated syllables into a single word. This operation is important
    to return accurate word counts from the written correspondences.

    Arguments:
        line (str): The current line, ending with the hyphenated word syllable.
        next_line (str): The next line, starting with the next syllable of the hyphenated word.

    Returns:
        line (str): the line with the separated syllables combined into a single word.
    """
    # Regular expression to match hyphenated words
    hyphen = r"(\w+)-\s*(\w+)([.,;:!?\)])?\s*"
    word = re.sub(hyphen, r"\1\2\3\n", text)
    word = word

    return word

def clean_spelling(text: str) -> str:
    """
    Fixes recurrent errors returned by the OCR-algorithm.
    This is mostly applicable to the Marescoe-David corpus, which has a
    fine print on relatively glossy paper, causing confusion in the Tesseract engine.

    Arguments:
        text (str): Text in need of spelling correction.

    Returns:
        text (str): The corrected text.
    """
    text = re.sub(r"\B\|\B", "I", text)
    text = re.sub(r"\bIam\b", "I am", text)
    text = re.sub(r"\bTam\b", "I am", text)
    text = re.sub(r"\b1am\b", "I am", text)
    text = re.sub(r"\B\[am\b", "I am", text)
    text = re.sub(r"\bIhave\b", "I have", text)
    text = re.sub(r"\bThave\b", "I have", text)
    text = re.sub(r"\B\[have\b", "I have", text)
    text = re.sub(r"\bThaving\b", "I having", text)
    text = re.sub(r"\B\[having\b", "I having", text)
    text = re.sub(r"\bItrust\b", "I trust", text)
    text = re.sub(r"\bIreceived", "I received", text)
    text = re.sub(r"\bIremit\b", "I remit", text)
    text = re.sub(r"\bIshall\b", "I shall", text)
    text = re.sub(r"\bIFT\b", "If I", text)
    text = re.sub(r"\bifI\b", "if I", text)
    text = re.sub(r"\bandto\b", "and to", text)
    text = re.sub(r"\bina\b", "in a", text)
    text = re.sub(r"\bisa\b", "is a", text)
    text = re.sub(r"\bif1\b", "if I", text)
    text = re.sub(r"\bifit\b", "if it", text)
    text = re.sub(r"\bIfit\b", "If it", text)
    text = re.sub(r"\bIfand\b", "If and", text)
    text = re.sub(r"\bifand", "if and", text)
    text = re.sub(r"\bgota\b", "got a", text)
    text = re.sub(r"\bnota\b", "not a", text)
    text = re.sub(r"\bnotall\b", "not all", text)   
    text = re.sub(r"\bNotall\b", "Not all", text)
    text = re.sub(r"\bIfin\b", "If in", text)
    text = re.sub(r"\bifin\b", "if in", text)
    text = re.sub(r"\bifthe\b", "if the", text) 
    text = re.sub(r"\bIfthe\b", "If the", text) 
    text = re.sub(r"\blitcle\b", "little", text)
    text = re.sub(r"\bcither\b", "either", text)
    text = re.sub(r"\bjourncy\b", "journey", text)
    text = re.sub(r"\bmoncy\b", "money", text)
    text = re.sub(r"\bnamcly\b", "namely", text)
    text = re.sub(r"\bpicces\b", "pieces", text)
    text = re.sub(r"\bscason\b", "season", text)
    text = re.sub(r"\btherc\b", "there", text)
    text = re.sub(r"\bweck\b", "week", text)
    text = re.sub(r"\byct\b", "yet", text)
    text = re.sub(r"\bct\b", "et", text)
    text = re.sub(r"\bmicux\b", "mieux", text)
    text = re.sub(r"\bMicux\b", "Mieux", text)
    text = re.sub(r"\bplusicurs\b", "plusieurs", text)   
    text = re.sub(r"\bPlusicurs\b", "Plusieurs", text)
    text = re.sub(r"\bJay\b", "J'ay", text)
    text = re.sub(r"\bjay\b", "j'ay", text)
    text = re.sub(r"\bDicu\b", "Dieu", text)   
    text = re.sub(r"\bdicu\b", "dieu", text) 
    text = re.sub(r"\badicu\b", "adieu", text)
    text = re.sub(r"\bAdicu\b", "Adieu", text)
    text = re.sub(r"\bdernicre\b", "derniere", text)
    text = re.sub(r"\bheurcuse\b", "heureuse", text)
    text = re.sub(r"\bMonsicur\b", "Monsieur", text)
    text = re.sub(r"\bmonsicur\b", "monsieur", text)
    text = re.sub(r"\bpartic\b", "partie", text)
    text = re.sub(r"\breccu\b", "receu", text)
    text = re.sub(r"\bLethicullier\b", "Lethieullier", text)
    text = re.sub(r"\bLethicullier's\b", "Lethieullier's", text)  
    text = re.sub(r"\bNorrk(?:6|é)ping\b", "Norrköping", text)
    text = re.sub(r"\bNyk(?:6|é)ping\b", "Nyköping", text)
    text = re.sub(r"\bLiibeck\b", "Lübeck", text)
    text = re.sub(r"\bLitbeck\b", "Lübeck", text)
    text = re.sub(r"\bNiirnberg\b", "Nürnberg", text)
    text = re.sub(r"\bNiiremberg\b", "Nüremberg", text)
    text = re.sub(r"\bGliickstadt\b", "Glückstadt", text)
    text = re.sub(r"\bCronstr(?:6|é)m\b", "Cronström", text)
    text = re.sub(r"\bCronstr(?:6|é)ms\b", "Cronströms", text)
    text = re.sub(r"\bOsterby\b", "Österby", text)
    text = re.sub(r"\bliibs\b", "lübs", text)
    text = re.sub(r"\bStiibbing\b", "Stübbing", text)
    text = re.sub(r"\bBacrle\b", "Baerle", text)
    text = re.sub(r"\bsce\b", "see", text)
    text = re.sub(r"\bsoc\b", "soe", text)
    text = re.sub(r"\bmce\b", "mee", text)
    text = re.sub(r"\bthey’\]\B", "they'l", text)
    text = re.sub(r"\bIb\b", "lb", text)
    text = re.sub(r"\bIbs\b", "lbs", text)
    text = re.sub(r"\bSIb\b", "Slb", text)
    text = re.sub(r"\b1oth\b", "10th", text)
    text = re.sub(r"\b2oth\b", "20th", text)
    text = re.sub(r"\b3oth\b", "30th", text)
    text = re.sub(r"\br2th\b", "12th", text)
    text = re.sub(r"\bsth\b", "5th", text)
    text = re.sub(r"\bss\b", "5s", text)
    text = re.sub(r"\brsth\b", "15th", text)

    return text

def tokenize(text):
    """
    Function to count the words in a given dictionary key.
    """
    words = text.split()
 
    return len(words)