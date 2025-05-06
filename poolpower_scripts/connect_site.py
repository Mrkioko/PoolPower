# Import necessary libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os # Helps in building path names

# --- Configuration ---
# 1. **SECURE THIS FILE!** Do NOT commit your JSON key file to Git.
#    Add its name to your .gitignore file.
# 2. Update this path to where you saved your downloaded JSON key file on your computer.
#    Using os.path.join is good practice. os.path.dirname(__file__) gets the directory
#    of the current script. Adjust the '..' and file name based on your file structure.
#    Example: If your key file is one folder up from your script:
# GOOGLE_KEY_FILE = os.path.join(os.path.dirname(__file__), '..', 'your-project-name-etc.json')
# Example: If your key file is in the same folder as your script:
# GOOGLE_KEY_FILE = os.path.join(os.path.dirname(__file__), 'your-project-name-etc.json')

# *** REPLACE THE LINE BELOW WITH THE CORRECT PATH TO YOUR FILE ***
# FIX: Replaced backslashes with forward slashes to avoid Python's escape character interpretation
GOOGLE_KEY_FILE = 'C:/Users/User/Documents/GitHub/PoolPower/poolpower_scripts/poolpower-fd17d74bd0d0.json' # <--- UPDATED THIS LINE

# Update with the exact name of your Google Sheet
# *** REPLACE THE LINE BELOW WITH YOUR SPREADSHEET NAME ***
SPREADSHEET_NAME = 'POOL POWER OPERATIONS DATA' # <--Do Not- UPDATE THIS LINE

# --- Authentication ---
# Define the scope (the services your script needs access to)
# We need access to Google Sheets and Google Drive (as Sheets files are stored on Drive)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

try:
    # Step 1: Load the credentials from the JSON key file
    # This file contains the service account credentials downloaded from Google Cloud
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_KEY_FILE, scope)

    # Step 2: Authorize the gspread client using the credentials
    # This client will be used to interact with your Google Sheets
    gc = gspread.authorize(credentials)

    print("Successfully authenticated with Google Sheets API.")

    # --- Open the Spreadsheet ---
    # Step 3: Open the spreadsheet by its exact name
    # Ensure the service account email address has been shared on this Google Sheet
    spreadsheet = gc.open(SPREADSHEET_NAME)

    print(f"Successfully opened spreadsheet: '{SPREADSHEET_NAME}'")

    # --- Example of how to access a worksheet (Next Steps) ---
    # Step 4 (Example): Access a specific tab (worksheet) within the spreadsheet
    # Replace 'Deals' with the actual name of your worksheet tab
    # try:
    #     deals_sheet = spreadsheet.worksheet('Deals')
    #     print("Accessed 'Deals' worksheet.")

    #     # Step 5 (Example): Read data from the worksheet
    #     # Get all records as a list of dictionaries (each dict is a row)
    #     # The first row is assumed to be headers
    #     # all_deal_records = deals_sheet.get_all_records()
    #     # print(f"Read {len(all_deal_records)} records from 'Deals' tab.")

    #     # You can now process all_deal_records (e.g., using pandas)

    # except gspread.WorksheetNotFound:
    #      print("Error: Worksheet 'Deals' not found. Check the tab name in your Google Sheet.")
    # except Exception as e:
    #      print(f"An error occurred while accessing or reading the worksheet: {e}")


except FileNotFoundError:
    print(f"Error: Google API key file not found at {GOOGLE_KEY_FILE}")
    print("Please ensure the path in GOOGLE_KEY_FILE is correct and the file exists.")
except gspread.SpreadsheetNotFound:
    print(f"Error: Spreadsheet '{SPREADSHEET_NAME}' not found.")
    print("Please check the spreadsheet name and ensure the service account email has 'Editor' access to it.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("Please check your credentials, scope, and network connection.")

# This script only connects and opens the spreadsheet.
# You will add more code after the 'spreadsheet = gc.open(SPREADSHEET_NAME)' line
# to select worksheets, read data, write data, etc.
