import os
from dotenv import load_dotenv
import json


def set_scraper_settings(keywords, number_of_events_per_keyword, ai_prompt):
    # Load environment variables from .env file
    load_dotenv()

    # airtable settings from .env file
    dotenv_path = ".env"

    try:
        load_dotenv(dotenv_path)

        # Get environment variables
        AIRTABLE_API_BASE_ID = os.getenv("AIRTABLE_API_BASE_ID")
        AIRTABLE_API_TABLE_NAME = os.getenv("AIRTABLE_API_TABLE_NAME")
        AIRTABLE_API_TOKEN = os.getenv("AIRTABLE_API_TOKEN")

        AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_API_BASE_ID}/{AIRTABLE_API_TABLE_NAME}"

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        # Read the SCRAPE_URL from the .env file
        SCRAPE_URL = os.getenv("SCRAPE_URL")

        # Check if the SCRAPE_URL is set
        if SCRAPE_URL is None:
            print("SCRAPE_URL not found in .env file")
        else:
            # Use the SCRAPE_URL in your code
            URL_TO_SCRAPE = SCRAPE_URL

    except ValueError:
        print("Failed to load one or more environment variables after 3 attempts.")

    # csv settings
    CSV_FILE_NAME = f"{AIRTABLE_API_TABLE_NAME}.csv"

    # Get current working directory for filepath
    CWD = os.getcwd()
    PATH_TO_CSV = os.path.join(CWD, "data", CSV_FILE_NAME)

    if input("Do you want to view the settings? (y/n): ") == "y":
        print(
            f"""
    AIRTABLE_API_TOKEN: 
    {AIRTABLE_API_TOKEN}

    AIRTABLE_API_URL: 
    {AIRTABLE_API_URL}

    OPENAI_API_KEY: 
    {OPENAI_API_KEY}

    URL_TO_SCRAPE: 
    {URL_TO_SCRAPE}

    PATH_TO_CSV: 
    {PATH_TO_CSV}

    keywords: 
    {keywords}

    number_of_events_per_keyword: 
    {number_of_events_per_keyword}

    ai_prompt: 
    {ai_prompt}
    """
        )

    # Define settings_dict
    settings_dict = {
        "AIRTABLE_API_TOKEN": AIRTABLE_API_TOKEN,
        "AIRTABLE_API_URL": AIRTABLE_API_URL,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "URL_TO_SCRAPE": URL_TO_SCRAPE,
        "PATH_TO_CSV": PATH_TO_CSV,
        "KEYWORDS": keywords,
        "NUMBER_OF_EVENTS_PER_KEYWORD": number_of_events_per_keyword,
        "AI_PROMPT": ai_prompt,
    }

    # Set the path to the data folder
    data_folder = "data"
    settings_path = os.path.join(data_folder, "settings.json")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Save the settings dictionary as a .json file
    with open((settings_path), "w") as fp:
        json.dump(settings_dict, fp)

    # Load the settings dictionary from the .json file
    with open((settings_path), "r") as fp:
        settings_dict = json.load(fp)

    return settings_dict