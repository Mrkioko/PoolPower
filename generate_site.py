# Import necessary libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os # Helps in building path names
import shutil # Helps in copying files
import urllib.parse # For more robust URL encoding

# --- Configuration ---
# Get the directory where the currently running script is located
SCRIPT_DIR = os.path.dirname(__file__)
# Get the root directory of the Git repository (assuming script is in a subfolder like poolpower_scripts)
# Adjust the '..' sequence if your script is in a different level of subfolder
REPO_ROOT = os.path.join(SCRIPT_DIR, '..') # Assuming script is one level down from repo root

# 1. **SECURE THIS FILE!** Do NOT commit your JSON key file to Git.
#    Add its name to your .gitignore file.
# 2. Update this path to where you saved your downloaded JSON key file relative to the SCRIPT_DIR.
# *** REPLACE THE LINE BELOW WITH THE CORRECT FILENAME OF YOUR JSON KEY FILE ***
GOOGLE_KEY_FILE = os.path.join(SCRIPT_DIR, 'poolpower_scripts\poolpower-fd17d74bd0d0.json') # <--- UPDATED THIS LINE

# Update with the exact name of your Google Sheet
# *** REPLACE THE LINE BELOW WITH YOUR SPREADSHEET NAME ***
SPREADSHEET_NAME = 'POOL POWER OPERATIONS DATA' # <--- UPDATED THIS LINE based on your output

# Update with the exact name of your 'Deals' tab in the spreadsheet
# *** CHECK YOUR GOOGLE SHEET AND UPDATE THIS LINE IF 'Deals' IS NOT THE EXACT TAB NAME ***
DEALS_SHEET_NAME = 'Deals' # <--- CHECK AND UPDATE THIS LINE

# *** REPLACE WITH YOUR ACTUAL POOLPOWER WHATSAPP NUMBER (with country code, no +) ***
# Example: For +254712345678, use '254712345678'
POOLPOWER_WHATSAPP_NUMBER = '254745771747' # <--- UPDATE THIS LINE

# Folder containing your template files (index_template.html, style.css, script.js) relative to the SCRIPT_DIR
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, 'templates') # <--- UPDATED: Templates folder relative to script

# Folder where the generated static site files will be saved (for GitHub Pages) relative to the REPO_ROOT
SITE_DIR = os.path.join(REPO_ROOT, 'docs') # <--- UPDATED: Output folder relative to repo root

INDEX_TEMPLATE = os.path.join(TEMPLATES_DIR, 'index_template.html') # <--- Use TEMPLATES_DIR
OUTPUT_INDEX = os.path.join(SITE_DIR, 'index.html') # The file GitHub Pages/Netlify will serve
STYLE_CSS_SRC = os.path.join(TEMPLATES_DIR, 'style.css') # <--- Source CSS path
STYLE_CSS_DEST = os.path.join(SITE_DIR, 'style.css') # <--- Destination CSS path
SCRIPT_JS_SRC = os.path.join(TEMPLATES_DIR, 'script.js') # <--- Source JS path
SCRIPT_JS_DEST = os.path.join(SITE_DIR, 'script.js') # <--- Destination JS path


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
        deals_sheet = spreadsheet.worksheet(DEALS_SHEET_NAME) # Using the variable here
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
            # Ensure the site output directory exists (docs folder)
            if not os.path.exists(SITE_DIR):
                 os.makedirs(SITE_DIR)
                 print(f"Created directory: {SITE_DIR}")

            # Read the HTML template file from the templates folder
            try:
                with open(INDEX_TEMPLATE, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            except FileNotFoundError:
                 print(f"Error: Index template file not found at {INDEX_TEMPLATE}")
                 print(f"Please ensure '{INDEX_TEMPLATE}' exists in your templates folder.")
                 exit()

            # Replace the placeholder in the template with the generated deals HTML
            # Also replace the WhatsApp number placeholder in the header link
            final_html_content = template_content.replace('[DEALS_PLACEHOLDER]', deals_html_output)
            final_html_content = final_html_content.replace('[YourPoolPowerNumber]', POOLPOWER_WHATSAPP_NUMBER)


            # Save the final HTML to the output file in the SITE_DIR (docs folder)
            with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
                f.write(final_html_content)
            print(f"Successfully generated {OUTPUT_INDEX}")


            # --- Copy Static Assets (CSS, JS) from templates to SITE_DIR ---
            try:
                if os.path.exists(STYLE_CSS_SRC):
                     shutil.copy(STYLE_CSS_SRC, STYLE_CSS_DEST) # Copy from SRC to DEST
                     print(f"Copied {STYLE_CSS_SRC} to {STYLE_CSS_DEST}")
                else:
                     print(f"Warning: CSS template file not found at {STYLE_CSS_SRC}")
                     print(f"Please ensure '{STYLE_CSS_SRC}' exists in your templates folder.")


                if os.path.exists(SCRIPT_JS_SRC):
                     shutil.copy(SCRIPT_JS_SRC, SCRIPT_JS_DEST) # Copy from SRC to DEST
                     print(f"Copied {SCRIPT_JS_SRC} to {SCRIPT_JS_DEST}")
                else:
                     print(f"Warning: JS template file not found at {SCRIPT_JS_SRC}")
                     print(f"Please ensure '{SCRIPT_JS_SRC}' exists in your templates folder.")


            except Exception as e:
                print(f"An error occurred while copying static files: {e}")


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

