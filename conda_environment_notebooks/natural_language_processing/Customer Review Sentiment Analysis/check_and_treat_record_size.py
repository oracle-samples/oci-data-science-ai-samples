"""================================================================================================
Check Maximum Record Size and Modifier
file name:check_and_treat_record_size.py

In this method, if the length of the text column in a row is more than the maximum limit,
the code breaks the text into multiple rows with a maximum length characters,
and adds these broken rows to a list of broken_rows.
If there are any broken_rows, the code asks the user for consent to apply the breakdown on all the marked records.
If the user inputs "yes", the code appends the broken_rows to the original DataFrame and returns the updated DataFrame.
===================================================================================================
"""

import pandas as pd
from dataenforce import Dataset
from typing import Union

# TODO: for broken records, the sentiment at document level may not work properly since we created multiple documents.


def record_size_modifier(df: Union[Dataset["idx", "text", ...], None],
                         idx: str,
                         text: str,
                         max_limit: int = 5000) -> pd.DataFrame:
    """ Record Size Modifier

        If the length of the text column in a row is more than the maximum limit,
        the code breaks the text into multiple rows with a maximum length characters,
        and adds these broken rows to a list of broken_rows.
        If there are any broken_rows, the code asks the user for consent to apply the breakdown
        on all the marked records.
        If the user inputs "yes", the code appends the broken_rows to the original DataFrame
        and returns the updated DataFrame.

    :param df: DataFrame to check and modify
    :param idx: Placeholder for title of the column representing ID in the df; Chosen by the user.
    :param text: Placeholder for title of the column representing 'text' in the df; Chosen by the user.
    :param max_limit: Maximum length of each row's text column in characters
    :return: Updated DataFrame with broken rows appended if consented by user
    """
    broken_rows = []
    to_remove = []
    for index, row in df.iterrows():
        if row[text] is None:
            pass
        elif len(row[text]) > max_limit:
            print(f"Text in row with id {row[idx]} has more than {max_limit} characters")

            doc_text = row[text]
            while len(doc_text) > max_limit:
                # find last period or other sentence-ending punctuation mark before the limit
                end = max_limit

                # In the following line, [end-1] is to include the punctuation in the current sentence.
                while end > 0 and doc_text[end - 1] not in {'.', '!', '?'}:
                    end -= 1
                if end == 0:
                    # if no sentence-ending punctuation found, break at max_limit
                    end = max_limit
                # add broken row with truncated doc_text
                broken_rows.append({
                    idx: f"{row[idx]}",
                    text: doc_text[:end]
                })
                # remove the added doc_text from original doc_text
                doc_text = doc_text[end:].strip()
            # add any remaining doc_text as final broken row
            if doc_text:
                broken_rows.append({
                    idx: f"{row[idx]}",
                    text: doc_text
                })
            # Keep record of the original rows that are being broken down in order to remove them from the df
            to_remove.append(index)

    if broken_rows:
        response = input("Do you consent to break all the marked extra-long texts into multiple rows? (yes/no)").lower()

        while response not in ['yes', 'no']:
            response = input(
                f"Please respond either Yes or No without any extra characters.\n"
                f"Do you consent to break all the marked extra-long texts into multiple rows? (yes/no)").lower()

        if response == "yes":
            # Remove original record(s) from the DataFrame
            df = df.drop(to_remove, axis=0)
            # Add broken rows to the DataFrame
            df = pd.concat([df, pd.DataFrame(broken_rows)], ignore_index=True)
            print('Complete!')
        else:
            raise ValueError("Current system limitations: A record may be up to 5000 characters long. \n"
                             "User chose not to break the row into multiple rows.  \n"
                             "If agreed, those texts with above limit number of characters could be "
                             "broken down into multiple rows with the same ID. \n"
                             "Then, they could be rejoined back to the original dataset. \n"
                             "Alternatively, you can resolve that limitation outside of this notebook and retry later."
                             )

    return df
