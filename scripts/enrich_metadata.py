import os
import sys
import argparse
import numpy as np
import pandas as pd

def load_file(input_df, sheet_name):
    """
    Loads the file specified by the user in the command line.
    The in order to load succesfully, the file must contain a worksheet with the following columns:

    'SENDER_BIRTH_YEAR'
    'ADDRESSEE_BIRTH_YEAR'
    'YEAR',
    'SENDER_CLEANED' or, alternatively, 'SENDER'
    'ADDRESSEE_CLEANED', or, alternatively, 'ADDRESSEE'

    In case of two possible columns names, the script will look for the primarily specified
    column name first before checking whether its alternative is available.

    If a required column is unavailable, a Value Error will be raised, asking the user
    to check if both the sheet name, as well as the missing column, are present in the file,
    and terminate with a non-zero exit code, indicating an error condition. 
    """
    try:
        df = pd.read_excel(input_df, sheet_name)
        required_columns = ["SENDER_BIRTH_YEAR",
                            "ADDRESSEE_BIRTH_YEAR",
                            "YEAR",
                            "SENDER_CLEANED",
                            "ADDRESSEE_CLEANED"]
        for column in required_columns:
            if column not in df.columns:
                if column == "YEAR" in df.columns:
                    continue
                elif column == "SENDER_CLEANED" and "SENDER" in df.columns:
                    continue
                elif column == "ADDRESSEE_CLEANED" and "ADDRESSEE" in df.columns:
                    continue
                else:
                    raise ValueError(f"Error: Program failed to execute. Please check if '{sheet_name}' or column '{column}' are present in the data frame.")
        return df
    except FileNotFoundError:
        print(f"Error: File '{input_df}' not found.")
        sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)

def age_diff_bool(df, col_a: str, col_b: str) -> pd.DataFrame:
    """
    Calculates the age difference between two correspondents by subtracting their birth dates.
    The method returns a new column that checks whether the sender is older than the addressee,
    expressed in boolean values ("TRUE" or "FALSE").
    Returns "UNK" if one of the correspondents' age is unknown.
    Returns "MULT" is both correspondents are comprised of multiple people.

    Arguments:
        col_a (str): select the column of sender birth dates.
        col_b (str): select the column of addressee birth dates.

    Returns:
        pd.DataFrame: an updated data frame with the added column "AGE_GAP_OVER_20",
        that checks whether there is an age gap of over 20 years between the sender
        and addressee.
    """
    age_diff_labels = []

    for index, row in df.iterrows():
        sender_year = row[col_a]
        addressee_year = row[col_b]
        if pd.notna(sender_year) or pd.notna(addressee_year):
            if sender_year in  ["MULT"] and addressee_year in ["MULT"]:
                age_diff = "MULT"
            elif sender_year in ["UNK", "MULT"] or addressee_year in ["UNK", "MULT"]:
                age_diff = "UNK"
            else:
                difference = abs(sender_year - addressee_year)
                if difference >= 20:
                    age_diff = "TRUE"
                else:
                    age_diff = "FALSE"
            age_diff_labels.append(age_diff)
        else:
            age_diff_labels.append(None)

    df["AGE_GAP_OVER_20"] = age_diff_labels
    return df

def age_diff_int(df, col_a: str, col_b: str) -> pd.DataFrame:
    """
    Calculates the age difference between two correspondents by subtracting their birth dates.
    The method returns a new column that marks the number of years of age difference between
    the sender and addressee.

    Arguments:
        col_a (str): select the column of sender birth dates.
        col_b (str): select the column of addressee birth dates.

    Returns:
        pd.DataFrame: an updated data frame with the added column "AGE_GAP_OVER_20",
        that marks the number of years of age difference between the sender and
        addressee.
    """
    age_diff_values = []

    for index, row in df.iterrows():
        sender_year = row[col_a]
        addressee_year = row[col_b]
        age_diff = None
        if pd.notna(sender_year) or pd.notna(addressee_year):
            if sender_year in ["UNK", "MULT"] or addressee_year in ["UNK", "MULT"]:
                pass
            else:
                sender_diff = abs(int(sender_year) - int(addressee_year))
                addressee_diff = abs(int(addressee_year) - int(sender_year))
                age_diff = int(min(sender_diff, addressee_diff))
        age_diff_values.append(age_diff)

    df["AGE_GAP"] = age_diff_values
    return df

def older_correspondent(df, col_a: str, col_b: str) -> pd.DataFrame:
    """
    Calculates the age difference between two correspondents by subtracting their birth dates.
    The function returns two new columns that marks whether the addressee is older than the sender.

    Arguments:
        df (pd.DataFrame): the data frame you want to pass through this function.
        col_a (str): select the column of sender birth dates.
        col_b (str): select the column of addressee birth dates.

    Returns:
        pd.DataFrame: an updated data frame with the added column "ADDRESSEE_IS_OLDER",
        that marks the number of years of age difference between the sender and
        addressee.
    """
    add_older_labels, sen_older_labels = [], []

    for index, row in df.iterrows():
        sender_year = row[col_a]
        addressee_year = row[col_b]
        if pd.notna(sender_year) and pd.notna(addressee_year):
            if addressee_year in ["UNK"]:
                add_older = "UNK"
                sen_older = "UNK"
            elif addressee_year in ["MULT"]:
                add_older = "MULT"
                sen_older = "MULT"
            elif sender_year in ["UNK"]:
                add_older = "UNK"
                sen_older = "UNK"
            elif sender_year in ["MULT"]:
                add_older = "MULT"
                sen_older = "MULT"
            else:
                if addressee_year <= sender_year:
                    add_older = "TRUE"
                    sen_older = "FALSE"
                else:
                    add_older = "FALSE"
                    sen_older = "TRUE"
            add_older_labels.append(add_older)
            sen_older_labels.append(sen_older)
        else:
            add_older_labels.append(None)
            sen_older_labels.append(None)

    df["SENDER_IS_OLDER"], df["ADDRESSEE_IS_OLDER"] = sen_older_labels, add_older_labels
    return df

def addressee_over_40(df, col_a: int, col_b: str) -> pd.DataFrame:
    """
    Calculates whether the addressee is older than 40 years.

    Arguments:
        df (pd.DataFrame): the data frame you want to pass through this function.
        col_a (str): select the column of year of writing.
        col_b (str): select the column of addressee birth date.

    Returns:
        pd.DataFrame: an updated data frame with the added column "ADDRESEE_OVER_40",
        that checks whether the addressee is over 40 years old.
    """
    age_labels = []

    for index, row in df.iterrows():
        letter_year = row[col_a]
        addressee_year = row[col_b]
        if pd.notna(letter_year) and pd.notna(addressee_year):
            if addressee_year in ["UNK"]:
                mid_age = "UNK"
            elif addressee_year in ["MULT"]:
                mid_age = "MULT"
            elif isinstance(letter_year, str):
                mid_age = "UNK"
            else:
                difference = abs(letter_year - addressee_year)
                if difference >= 40:
                    mid_age = "TRUE"
                else:
                    mid_age = "FALSE"
            age_labels.append(mid_age)
        else:
            age_labels.append(None)

    df["ADDRESSEE_OVER_40"] = age_labels
    return df

def sender_over_40(df, col_a: str, col_b: str) -> pd.DataFrame:
    """
    Calculates whether the sender is older than 40 years.

    Arguments:
        df (pd.DataFrame): the data frame you want to pass through this function.
        col_a (str): select the column of year of writing.
        col_b (str): select the column of sender birth date.

    Returns:
        pd.DataFrame: an updated data frame with the added column "SENDER_OVER_40",
        that checks whether the sender is over 40 years old.
    """
    age_labels = []

    for index, row in df.iterrows():
        letter_year = row[col_a]
        sender_year = row[col_b]
        if pd.notna(letter_year) and pd.notna(sender_year):
            if sender_year in ["UNK"]:
                mid_age = "UNK"
            elif sender_year in ["MULT"]:
                mid_age = "MULT"
            elif isinstance(letter_year, str):
                mid_age = "UNK"
            else:
                difference = abs(letter_year - sender_year)
                if difference >= 40:
                    mid_age = "TRUE"
                else:
                    mid_age = "FALSE"
            age_labels.append(mid_age)
        else:
            age_labels.append(None)

    df["SENDER_OVER_40"] = age_labels
    return df

def genders(df, col_a: str, col_b: str) -> pd.DataFrame:
    """
    Pairs the gender of both correspondents together.

    Arguments:
        df (pd.DataFrame): the data frame you want to pass through this function.
        col_a (str): select the column containing the genders of the senders.
        col_b (str): select the column containing the genders of the addressees.

    Returns:
        pd.DataFrame: an updated data frame with the added column "GENDER_PAIR",
        that pairs the sender and addressee names together.
    """
    genders = []

    for index, row in df.iterrows():
        gender_send = row[col_a]
        gender_add = row[col_b]

        if pd.notna(gender_send) and pd.notna(gender_add):
            pair = f'"{gender_send}", "{gender_add}"'
            genders.append(pair)
        else:
            genders.append(None)
    
    df["GENDER_PAIR"] = genders
    return df

def pairs(df, col_a: str, col_b: str) -> pd.DataFrame:
    """
    Groups sender and addressee pairs together.

    Arguments:
        df (pd.DataFrame): the data frame you want to pass through this function.
        col_a (str): select the column containing the names of the senders.
        col_b (str): select the column containing the names of the addressees.

    Returns:
        pd.DataFrame: an updated data frame with the added column "SENDER-ADDRESSEE_PAIR",
        that pairs the sender and addressee names together.
    """
    paired = []

    for index, row in df.iterrows():
        sender = row[col_a]
        addressee = row[col_b]

        if pd.notna(sender) and pd.notna(addressee):
            pair = f'"{sender}", "{addressee}"'
            paired.append(pair)
        else:
            paired.append(None)
    
    df["SENDER-ADDRESSEE_PAIR"] = paired
    return df

def apply_functions(df) -> pd.DataFrame:
    """ 
    Applies all previously defined method to the worksheet.
    A print message will notify which column was added to the worksheet.
    If the column already exists, a notification will be printed informing
    that the column is already present in the worksheet,
    and the method will not be applied, preserving the existing colum.

    Returns:
        df (pd.DataFrame): an updated data frame with all the columns
        constructed by the previous methods included.
    """
    if "SENDER_IS_OLDER" not in df.columns:
        df = older_correspondent(df, "SENDER_BIRTH_YEAR", "ADDRESSEE_BIRTH_YEAR")
        print("Column 'SENDER_IS_OLDER' added to data frame.")
    else:
        print("Column 'SENDER_IS_OLDER' already exists.")
    if "SENDER_OVER_40" not in df.columns:
        df = sender_over_40(df, "YEAR", "SENDER_BIRTH_YEAR")
        print("Column 'SENDER_OVER_40' added to data frame.")
    else:
        print("Column 'SENDER_OVER_40' already exists.")
    if "ADDRESSEE_OVER_40" not in df.columns:
        df = addressee_over_40(df, "YEAR", "ADDRESSEE_BIRTH_YEAR")
        print("Column 'ADDRESSEE_OVER_40' added to data frame.")
    else:
        print("Column 'ADDRESSEE_OVER_40' already exists.")
    if "AGE_GAP" not in df.columns:
        df = age_diff_int(df, "SENDER_BIRTH_YEAR", "ADDRESSEE_BIRTH_YEAR")
        print("Column 'AGE_GAP' added to data frame.")
    else:
        print("Column 'AGE_GAP' already exists.")
    if "AGE_GAP_OVER_20" not in df.columns:
        df = age_diff_bool(df, "SENDER_BIRTH_YEAR", "ADDRESSEE_BIRTH_YEAR")
        print("Column 'AGE_GAP_OVER_20' added to data frame.")
    else:
        print("Column 'AGE_GAP_OVER_20' already exists.")
    if "SENDER-ADDRESSEE_PAIR" not in df.columns:
        df = pairs(df, "SENDER_CLEANED", "ADDRESSEE_CLEANED")
        print("Column 'SENDER-ADDRESSEE_PAIR' added to data frame.")
    else:
        print("SENDER-ADDRESSEE_PAIR already exists.")
    if "GENDER_PAIRS" not in df.columns:
        df = genders(df, "GENDER_SENDER", "GENDER_ADDRESSEE")
        print("Column 'GENDER_PAIR added to data frame.")
    else:
        print("SENDER-ADDRESSEE_PAIR already exists.")
        
    return df

def save_file(output_df):
    """
    Saves the processed Excel worksheet to a .csv file. If the file already exists,
    it will not be overwitten. Instead, it will add a '(#)' copy number suffix to the filename.

    returns:
        df (pd.DataFrame): a .csv output file with the applied methods.
    """
    filename, _ = os.path.splitext(output_df)
    copy_number = 0
    while os.path.exists(output_df):
        if copy_number == 0:
            output_df = f"{filename}.csv"
        else:
            output_df = f"{filename}({copy_number}).csv"
        copy_number += 1
    df.to_csv(output_df, index=False)
    print(f"New file created: '{output_df}'.")
    return output_df

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Enrich the metadata of digitised letter correspondences. \
The script assumes that the data set is in .xlsx format, and that it contains the following columns:\
'ADDRESSEE_BIRTH_YEAR' t\ \
'SENDER_BIRTH_YEAR' t\ \
'YEAR' or 'YEAR_OF_WRITING' t\ \
'SENDER_CLEANED' or 'SENDER' t\ \
'ADDRESSEE_CLEANED' or 'ADDRESSEE'. You may need to pip install openpyxl to run Pandas' read_excel method present in this script.")
    p.add_argument("input_df", type=str, help="The folder and name of your input .xslx file.")
    p.add_argument("sheet_name", type=str, help="The name of the worksheet in the Excel file that should be processed.")
    p.add_argument("output_df", type=str, help="The folder and filename of the script's output .csv file.")
    args = p.parse_args()
  

    df = load_file(args.input_df, args.sheet_name)
    df = apply_functions(df)
    save_file(args.output_df)