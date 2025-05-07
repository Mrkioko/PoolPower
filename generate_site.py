# Import necessary libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os # Helps in building path names
import shutil # Helps in copying files
import urllib.parse # For more robust URL encoding

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

# *** REPLACE THE LINE BELOW WITH THE CORRECT PATH TO YOUR JSON KEY FILE ***
# Example path using forward slashes (recommended for Windows compatibility)
GOOGLE_KEY_FILE = 'C:/Users/User/Documents/GitHub/PoolPower/poolpower_scripts/poolpower-fd17d74bd0d0.json' # <-Do not-- UPDATE THIS LINE

# Update with the exact name of your Google Sheet
# *** REPLACE THE LINE BELOW WITH YOUR SPREADSHEET NAME ***
SPREADSHEET_NAME = 'POOL POWER OPERATIONS DATA' # <--Do Not- UPDATE THIS LINE

# Update with the exact name of your 'Deals' tab in the spreadsheet
DEALS_SHEET_NAME = 'Deals'

# *** REPLACE WITH YOUR ACTUAL POOLPOWER WHATSAPP NUMBER (with country code, no +) ***
# Example: For +254712345678, use '254712345678'
POOLPOWER_WHATSAPP_NUMBER = '254745771747' # <--- UPDATE THIS LINE

# Folder where your html/css/js templates are and where the output index.html will be saved
SITE_DIR = 'docs'
INDEX_TEMPLATE = os.path.join(SITE_DIR, 'index_template.html')
OUTPUT_INDEX = os.path.join(SITE_DIR, 'index.html') # The file GitHub Pages/Netlify will serve
STYLE_CSS = os.path.join(SITE_DIR, 'style.css') # Path to your CSS file
SCRIPT_JS = os.path.join(SITE_DIR, 'script.js') # Path to your JS file


# --- Authentication ---
# Define the scope (the services your script needs access to)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

gc = None # Initialize google sheets client outside try block

try:
    # Load the credentials from the JSON key file
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_KEY_FILE, scope)

    # Authorize the gspread client using the credentials
    gc = gspread.authorize(credentials)

    print("Successfully authenticated with Google Sheets API.")

except FileNotFoundError:
    print(f"Error: Google API key file not found at {GOOGLE_KEY_FILE}")
    print("Please ensure the path in GOOGLE_KEY_FILE is correct and the file exists.")
    exit() # Exit if credentials file is not found
except Exception as e:
    print(f"An unexpected error occurred during authentication: {e}")
    print("Please check your credentials, scope, and network connection.")
    exit() # Exit if authentication fails

# --- Read Data and Generate HTML ---
if gc: # Only proceed if authentication was successful
    try:
        # Open the spreadsheet by its exact name
        spreadsheet = gc.open(SPREADSHEET_NAME)
        print(f"Successfully opened spreadsheet: '{SPREADSHEET_NAME}'")

        # Access the 'Deals' worksheet
        deals_sheet = spreadsheet.worksheet(DEALS_SHEET_NAME)
        print(f"Accessed '{DEALS_SHEET_NAME}' worksheet.")

        # Get all records as a list of dictionaries
        # Assumes the first row in the sheet is the header row
        deals_data = deals_sheet.get_all_records()

        # Convert to pandas DataFrame for easier handling and filtering
        df_deals = pd.DataFrame(deals_data)

        # Filter for active deals where 'Is Active' column is 'Yes' (case-insensitive)
        # .astype(str) handles potential non-string values in the column
        # .str.lower() converts to lowercase for case-insensitive comparison
        active_deals_df = df_deals[df_deals['Is Active'].astype(str).str.lower() == 'yes'].copy()

        print(f"Found {len(active_deals_df)} active deals.")
        if not active_deals_df.empty:
            # --- Generate HTML Snippets for Each Deal ---
            deals_html_snippets = []
            for index, deal in active_deals_df.iterrows():
                # Use .get() with a default value for robustness in case a cell is empty
                deal_id = deal.get('Deal ID', 'N/A')
                item_name = deal.get('Item Name', 'Unnamed Deal')
                short_description = deal.get('Short Description', 'No description available.')
                target_qty = deal.get('Target Qty', 'N/A')
                est_price = deal.get('Est Price Per Item', 'N/A')
                image_url = deal.get('Image URL', '') # Default to empty string if no URL

                # Create the HTML snippet for a single deal item using Tailwind classes
                # Added data attributes to the button for JS to easily access deal info
                deal_snippet = f"""
            <div class="deal-item bg-white rounded-lg shadow-md p-6 mb-6 flex flex-col md:flex-row items-center">
                <img src="{image_url}" alt="{item_name}" class="w-32 h-32 object-cover rounded-md mb-4 md:mb-0 md:mr-6" onerror="this.onerror=null; this.src='https://placehold.co/128x128/e5e7eb/1f2937?text=No+Image';">
                <div class="flex-grow text-center md:text-left">
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">{item_name} ({deal_id})</h3>
                    <p class="text-gray-600 mb-3">{short_description}</p>
                    <p class="text-gray-700 mb-1"><strong>Target Qty:</strong> {target_qty}</p>
                    <p class="text-gray-700 mb-4"><strong>Est. Price:</strong> KSh {est_price}</p>
                  
                    <button
                        class="initiate-pool-btn bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-md transition duration-300 ease-in-out"
                        data-deal-id="{deal_id}"
                        data-item-name="{item_name}"
                        data-whatsapp-number="{POOLPOWER_WHATSAPP_NUMBER}" 
                    >
                        Ask about this Deal / Create Pool
                    </button>
                </div>
            </div>
            """
                deals_html_snippets.append(deal_snippet)

            # Combine all deal snippets into a single string
            deals_html_output = "\n".join(deals_html_snippets)

            # --- Assemble the Final HTML Page ---
            # Ensure the site directory exists
            if not os.path.exists(SITE_DIR):
                 os.makedirs(SITE_DIR)
                 print(f"Created directory: {SITE_DIR}")

            # Read the HTML template file
            try:
                with open(INDEX_TEMPLATE, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            except FileNotFoundError:
                 print(f"Error: Index template file not found at {INDEX_TEMPLATE}")
                 exit()

            # Replace the placeholder in the template with the generated deals HTML
            # Also replace the WhatsApp number placeholder in the header link
            final_html_content = template_content.replace('[DEALS_PLACEHOLDER]', deals_html_output)
            final_html_content = final_html_content.replace('[YourPoolPowerNumber]', POOLPOWER_WHATSAPP_NUMBER)


            # Save the final HTML to the output file
            with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
                f.write(final_html_content)

            # --- Copy Static Assets (CSS, JS) ---
            # Copy CSS and JS files to the output directory (assuming they are in SITE_DIR)
            try:
                if os.path.exists(STYLE_CSS):
                     shutil.copy(STYLE_CSS, os.path.join(SITE_DIR, 'style.css'))
                     print(f"Copied {STYLE_CSS} to {SITE_DIR}")
                else:
                     print(f"Warning: CSS file not found at {STYLE_CSS}")

                if os.path.exists(SCRIPT_JS):
                     shutil.copy(SCRIPT_JS, os.path.join(SITE_DIR, 'script.js'))
                     print(f"Copied {SCRIPT_JS} to {SITE_DIR}")
                else:
                     print(f"Warning: JS file not found at {SCRIPT_JS}")

            except Exception as e:
                print(f"An error occurred while copying static files: {e}")


            print(f"Successfully generated static site at {OUTPUT_INDEX}")

        else:
            print("No active deals found in the Google Sheet. No site generated.")


    except gspread.SpreadsheetNotFound:
        print(f"Error: Spreadsheet '{SPREADSHEET_NAME}' not found.")
        print("Please check the spreadsheet name and ensure the service account email has 'Editor' access to it.")
    except gspread.WorksheetNotFound:
         print(f"Error: Worksheet '{DEALS_SHEET_NAME}' not found.")
         print(f"Please check the tab name '{DEALS_SHEET_NAME}' in your Google Sheet.")
    except Exception as e:
        print(f"An unexpected error occurred while reading data or generating HTML: {e}")

