import numpy as np
import pandas as pd
import argparse

def map_values(source_df: pd.DataFrame, target_df: pd.DataFrame, value_cols: list) -> pd.DataFrame:
    """ 
    Reconciles the values of two dataframe columns of mismatched length.
    This is to be applied to cases in which we want to calculate relative frequencies
    of a queried corpus.

    Arguments:
        source_df (pd.DataFrame): The entries (ids) with their number of hits per entry.
        target_df (pd.DataFrame): All entries in the data set. The values
        of the column to which the source data (source_df) is mapped is empty.
    
    Returns:
        pd.DataFrame: A data frame with all hits mapped to their respective index number.
            The entries that did not contain any hits are assigned value zero.
    """
    # set the index for both data frames
    source_df.set_index("id", inplace=True)
    target_df.set_index("id", inplace=True)

    # update the target data frame with values from the source data frame
    target_df.update(source_df[value_cols])

    # reset the index for the resulting data frame
    result_df = target_df.reset_index()

    # fill the empty values with zeroes and cast all values as integers
    result_df.fillna(0, inplace=True)
    result_df[value_cols] = result_df[value_cols].astype(int)


    return result_df

if __name__ == "__main__":

    p = argparse.ArgumentParser(description="Process two .txt data frames to reconcile data.\
The script assumes that the index column of both files is called 'id'.\
The script requires you to change the names of the value columns ('value_columns') as required for your particlar case.\
Example usage is when you have queried a corpus for a certain word and you wish to calculate the relative frequencies of that word.\
You can extract a .txt data frame from your metadata with all the word counts per entry, and do the same with all the hits per entry.\
Feed them to this script, and it will map the number of hits to your total number of entries.\
This is meant for cases where your number of hits in your queried entries is mismatched to your total number of entries.")
    
    p.add_argument("source_file", help="The data frame (recommended as a .txt file) containing the entries with hits from your query.")
    p.add_argument("target_file", help="The data frame (recommended as a .txt file) containing the total number of entries from your metadata.\
The script assumes that the values of the columns you wish to map your source data to are empty.")
    
    p.add_argument("output_file", help="A data frame with the number of hits per file mapped to the total number of files from your metadata.")

    args = p.parse_args()

    source = pd.read_csv(args.source_file, delimiter="\t")
    target = pd.read_csv(args.target_file, delimiter="\t")

    # match items in list to your data frame columns
    value_columns = ["SOCIAL_LIFE",
                     "TRAVEL_TRANSPORT",
                     "TRADE_FINANCES",
                     "HEALTH_SICKNESS",
                     "POLITICS_WAR"]

    result_df = map_values(source, target, value_columns)
    result_df.to_csv(args.output_file, index=False, sep='\t')