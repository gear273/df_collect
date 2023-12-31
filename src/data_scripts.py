import csv
import pandas as pd
import json
import tempfile
import shutil
import os
from pathlib import Path
import uuid


# to CSV function
# def save_to_csv(data, filename):
#     if not data:
#         print("No data to save.")
#         return

#     fieldnames = [
#         "Name",
#         "Photo",
#         "Tags",
#         "Long Description",
#         "Summary",
#         "Location",
#         "Venue",
#         "Gmaps link",
#         "Date",
#         "Month",
#         "Day",
#         "Year",
#         "Time",
#         "AM/PM",
#         "Price",
#         "Link",
#         "Keyword",
#         "Category",
#         "People",
#         "Group Size",
#     ]

#     flattened_data = []
#     for events in data.values():
#         for event_data in events.values():
#             # # Remove the URL field from the event_data dictionary
#             # event_data.pop("URL", None)
#             flattened_data.append(event_data)

#     with open(filename, "w", newline="", encoding="utf-8") as output_file:
#         dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
#         dict_writer.writeheader()
#         dict_writer.writerows(flattened_data)


def save_dict_to_csv(all_events_dict, csv_filename):
    flattened_data = []

    for keyword, keyword_events_dict in all_events_dict.items():
        for event_id, event_info in keyword_events_dict.items():
            if event_info is not None:  # if event_info is None, we skip the event
                info_copy = (
                    event_info.copy()
                )  # we don't want to modify the original dict
                info_copy["Keyword"] = keyword
                # info_copy["event_id"] = event_id
                flattened_data.append(info_copy)

    df = pd.DataFrame(flattened_data)
    df.to_csv(
        csv_filename, index=False
    )  # write dataframe to CSV, without the row index


# from CSV function
def load_from_csv(filename):
    df = pd.read_csv(filename)
    return df


def delete_duplicates(data, columns_to_compare=None):
    if isinstance(data, str):  # if the input is a file path
        data = pd.read_csv(data)

    # Keep one instance of each event with the same name, remove others
    df_no_duplicates = data.drop_duplicates(subset=columns_to_compare, keep="first")

    return df_no_duplicates  # return the DataFrame object


def delete_duplicates_add_keywords(data, columns_to_compare=None):
    if isinstance(data, str):  # if the input is a file path
        data = pd.read_csv(data)

    original_data = data.copy()  # copy the original data to compare later

    # Convert 'Keyword' to a set, which removes duplicates within each group
    data["Keyword"] = data.groupby(columns_to_compare)["Keyword"].transform(
        lambda x: ",".join(set(x.str.split(",").sum()))
    )

    # Keep one instance of each event with the same name, remove others
    df_no_duplicates = data.drop_duplicates(subset=columns_to_compare, keep="first")

    # Print the indexes and keywords
    added_keywords_rows = df_no_duplicates[
        df_no_duplicates["Keyword"].str.contains(",", na=False)
    ]
    indexes_and_keywords = added_keywords_rows[["Keyword"]]
    print("\nRows that gained keywords:\n")
    with pd.option_context("display.max_rows", None, "display.max_columns", None):
        print(indexes_and_keywords)
    print("\nTotal rows that gained keywords: ", indexes_and_keywords.shape[0])

    return df_no_duplicates


# ##


def json_save(data, filename):
    # backup
    json_data = json.dumps(data)
    # Save the JSON string to a file
    with open(filename, "w") as file:
        file.write(json_data)


def json_read(json_filename):
    # Specify the filename of the JSON backup file
    # Load JSON data from the file
    with open(json_filename, "r") as file:
        json_data = file.read()

    # Convert the JSON data back into the dictionary
    json_dict = json.loads(json_data)

    return json_dict


# def filter_rows_by_keywords(df, action_params):
#     columns = action_params["columns"]
#     keywords = action_params["keywords"]
#     skip_columns = action_params["skip_columns"]
#     keywords = [kw.lower() for kw in keywords]

#     # Process each row
#     for index, row in df.iterrows():
#         row_text = ""

#         # Combine text from all relevant columns
#         for column in columns:
#             if column not in skip_columns:
#                 row_text += " " + str(row[column]).lower()

#         # Check if any of the keywords is in the combined text
#         if not any(keyword in row_text for keyword in keywords):
#             df = df.drop(index)


def filter_rows_by_keywords(df, action_params):
    columns = action_params["columns"]
    keywords = action_params["keywords"]
    skip_columns = action_params["skip_columns"]
    keywords = [kw.lower() for kw in keywords]

    mask = []
    # Process each row
    for index, row in df.iterrows():
        row_text = ""

        # Combine text from all relevant columns
        for column in columns:
            if column not in skip_columns:
                row_text += " " + str(row[column]).lower()

        # Check if any of the keywords is in the combined text
        if any(keyword in row_text for keyword in keywords):
            mask.append(True)
        else:
            mask.append(False)

    # Return the DataFrame with only the rows that contain at least one keyword
    return df[mask]


def manipulate_csv_data(
    file_path=None, output_filepath=None, operations=None, input_df=None
):
    """
    This is how to set parameters:

    operations = [
            # ... other operations
            {'action': 'substring', 'column_name': 'Month', 'start_index': 0, 'end_index': 3},
            {'action': 'uppercase', 'column_name': 'Month'},
            # ... other substring operations
        ]
    """

    if file_path is None and input_df is None:
        raise ValueError("Either a file path or an input DataFrame must be provided.")
    elif file_path is not None and input_df is not None:
        raise ValueError("Only one of file path or input DataFrame should be provided.")

    if input_df is not None:
        df = input_df
    else:
        df = pd.read_csv(file_path)

    # Fill NA/NaN values with an empty string
    df = df.fillna("")

    if output_filepath == None:
        output_filepath = file_path

    if operations == None:
        return print("No operations specified. Skipping function...")

    # Apply operations
    for operation in operations:
        if operation["action"] == "add_column":
            df[operation["column_name"]] = operation["column_value"]
        elif operation["action"] == "remove_column":
            df.drop(columns=[operation["column_name"]], axis=1, inplace=True)
        elif operation["action"] == "lowercase":
            df[operation["column_name"]] = (
                df[operation["column_name"]].astype(str).str.lower()
            )
        elif operation["action"] == "uppercase":
            df[operation["column_name"]] = (
                df[operation["column_name"]].astype(str).str.upper()
            )
        elif operation["action"] == "titlecase":
            df[operation["column_name"]] = (
                df[operation["column_name"]].astype(str).str.title()
            )
        elif operation["action"] == "split":
            df[operation["new_column_name"]] = (
                df[operation["column_name"]]
                .astype(str)
                .str.split(pat=operation["delimiter"])
            )
        elif operation["action"] == "substring":
            start_index = operation["start_index"]
            end_index = operation["end_index"]
            new_column_name = operation.get("new_column_name", None)
            if new_column_name:
                df[new_column_name] = (
                    df[operation["column_name"]].astype(str).str[start_index:end_index]
                )
            else:
                df[operation["column_name"]] = (
                    df[operation["column_name"]].astype(str).str[start_index:end_index]
                )
        elif operation["action"] == "keyword_filter":
            keyword = operation["keyword"]
            df = df[~df[operation["column_name"]].str.contains(keyword, case=False)]
        elif operation["action"] == "filter_rows_by_keywords":
            # df = filter_rows_by_keywords(
            #     df,
            #     {
            #         "columns": operation["columns"],
            #         "keywords": operation["keywords"],
            #         "skip_columns": operation.get("skip_columns"),
            #     },
            # )
            action_params = {
                "columns": operation["columns"],
                "keywords": operation["keywords"],
                "skip_columns": operation.get("skip_columns", []),
            }
            df = filter_rows_by_keywords(df, action_params)

        else:
            raise ValueError(f"Invalid action '{operation['action']}'")

    df.to_csv(output_filepath, index=False)

    return df


def json_to_df(file_path):
    # Load JSON data from file
    with open(file_path) as file:
        data = json.load(file)

    try:
        # Try to normalize the JSON data (i.e., handle nested structure)
        df = pd.json_normalize(data)
    except:
        # If an error is raised, assume the JSON data isn't nested
        df = pd.DataFrame(data)

    return df


def json_read(json_filename):
    # Specify the filename of the JSON backup file
    # Load JSON data from the file
    with open(json_filename, "r") as file:
        json_data = file.read()

    # Convert the JSON data back into the dictionary
    json_dict = json.loads(json_data)

    return json_dict


def json_save(data, filename):
    # backup
    json_data = json.dumps(data)
    # Save the JSON string to a file
    with open(filename, "w") as file:
        file.write(json_data)


def backup_data(input_data, backup_directory, input_name=None):
    # Convert backup_directory to a Path object
    backup_directory = Path(backup_directory)
    # Create backup_directory if it doesn't exist
    backup_directory.mkdir(parents=True, exist_ok=True)

    # Determine the file extension
    if isinstance(input_data, pd.DataFrame):
        file_extension = ".csv"
    elif isinstance(input_data, str) and input_data.endswith((".csv", ".txt", ".json")):
        file_extension = os.path.splitext(input_data)[1]
    elif isinstance(input_data, dict) or (
        isinstance(input_data, str) and input_data.endswith(".json")
    ):
        file_extension = ".json"
    elif isinstance(input_data, str):
        file_extension = ".txt"
    else:
        raise ValueError("Unsupported data type")

    # Create a temporary file with the desired file name
    with tempfile.NamedTemporaryFile(
        suffix=file_extension, delete=False, mode="w"
    ) as temp_file:
        # Save the input data to the temporary file
        if isinstance(input_data, pd.DataFrame):
            input_data.to_csv(temp_file.name, index=False)
        elif isinstance(input_data, str) and input_data.endswith(
            (".csv", ".txt", ".json")
        ):
            with open(input_data, "r") as data_file:
                temp_file.write(data_file.read())
        elif isinstance(input_data, dict):
            json.dump(input_data, temp_file)
        elif isinstance(input_data, str) and input_data.endswith(".json"):
            with open(input_data, "r") as data_file:
                json_data = json.load(data_file)
            with open(temp_file.name, "w") as temp_json_file:
                json.dump(json_data, temp_json_file)
        elif isinstance(input_data, str):
            temp_file.write(input_data.encode("utf-8"))

        # Determine the backup file name
        if input_name is not None:
            backup_file_name = f"{input_name}_backup{file_extension}"
        else:
            backup_file_name = f"backup_{uuid.uuid4()}{file_extension}"

        # Copy the temporary file to the backup directory
        backup_file_path = backup_directory / backup_file_name
        shutil.copy(temp_file.name, backup_file_path)

    # Remove the temporary file
    os.unlink(temp_file.name)
