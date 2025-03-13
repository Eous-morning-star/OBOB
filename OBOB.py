import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import base64
import gspread
from google.oauth2.service_account import Credentials

st.markdown(
    """
    <style>
    /* Hide the Streamlit edit pencil icon */
    [data-testid="stDeployButton"] {display: none !important;}
    
    /* Hide the GitHub logo in the top right corner */
    header {visibility: hidden;}
    
    /* Hide Streamlit's main menu */
    #MainMenu {visibility: hidden;}
    
    /* Hide Streamlit footer (Powered by Streamlit) */
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Set your passkey (Change this to your desired passkey)
PASSKEY = "indorama2024"  # 🔥 Change this to your secret passkey

# ✅ Check if user is authenticated
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False  # Default to False

# ✅ Show login form if not authenticated
if not st.session_state.authenticated:
    st.title("🔒 Secure Access")

    # User input for passkey
    passkey_input = st.text_input("Enter Passkey:", type="password")  # Hide input for security

    # Verify passkey
    if st.button("Unlock"):
        if passkey_input == PASSKEY:
            st.session_state.authenticated = True  # Set authentication to True
            st.success("✅ Access Granted! Welcome to the App.")
            st.rerun()  # ✅ Use st.rerun() instead

        else:
            st.error("❌ Incorrect Passkey. Please try again.")

    # Stop execution if authentication fails
    st.stop()

# ✅ If authenticated, show the main app
st.sidebar.success("🔓 Access Granted")

    if st.sidebar.button("🔒 Logout"):
        st.session_state.authenticated = False  # Reset authentication state
        st.session_state.page = "passkey"  # Redirect to Passkey page
        st.rerun()  # Refresh app to apply changes

# Define deviation thresholds for specific equipment
equipment_thresholds = ({
    # 1670
    "1670-PA-02A": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1670-PA-02B": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1670-PA-02C": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1670-PA-04A": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1670-PA-04B": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1670-PA-04C": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                }, 

    # 1600
    "1600-PA-04A": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1600-PA-04B": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1600-KF-02A": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1600-KF-02B": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1600-KF-02C": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
# 1680
    "1680-PA-01A": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1680-PA-01B": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1680-PH-01A": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
    "1680-PH-01B": {"Driving End Temp": {"min": 0, "max": 70}, "Driven End Temp": {"min": 0, "max": 70},
                "DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "NDE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor Driving End Temp": {"min": 0, "max": 70}, "Motor Driven End Temp": {"min": 0, "max": 70}, "Motor DE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Horizontal RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Vertical RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Vertical RMS (mm/s)": {"min": 0, "max": 6}, 
                    "Motor DE Axial RMS (mm/s)": {"min": 0, "max": 6}, "Motor NDE Axial RMS (mm/s)": {"min": 0, "max": 6}
                },
})


# ✅ Authenticate Google Sheets with the correct scope
def authenticate_google_sheets():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", 
                  "https://www.googleapis.com/auth/drive"]  # Added Drive access for permission issues
        
        creds = Credentials.from_service_account_info(st.secrets["GOOGLE_SHEET_KEY"], scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"❌ Google Sheets authentication failed: {e}")
        return None

# ✅ Connect to Google Sheets
client = authenticate_google_sheets()
if client:
    try:
        sheet = client.open("INDORAMA LLF").worksheet("Sheet2")
        st.success("✅ Connected to Google Sheets successfully!")
    except Exception as e:
        st.error(f"❌ Unable to open Google Sheet: {e}")
else:
    st.stop()

# Apply CSS for black buttons
st.markdown(
    """
    <style>
    /* Make all text bold */
    h1, h2, h3, h4, h5, h6, p, label {
        font-weight: bold !important;
        font-size: 18px !important;
    }

    /* Add black shadow to headings */
    h1, h2, h3, h4, h5, h6 {
        text-shadow: 3px 3px 5px black !important;
    }

    /* Ensure text is visible over the background */
    body, .stApp {
        color: white !important; /* Change to black if needed */
    }
    
    /* Style Streamlit buttons */
    div.stButton > button {
        background-color: black !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border: 2px solid white !important;
    }

    /* Change button color when hovered */
    div.stButton > button:hover {
        background-color: #333 !important;  /* Darker black on hover */
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ Load existing data from Google Sheets
def load_data():
    """Fetch data from Google Sheets."""
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame()
    
# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "main"  # Set default page to "main"

def validate_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing columns in dataset: {', '.join(missing)}")
        return False
    return True

# Add Utility Functions Here
def calculate_kpis():
    """Calculate KPIs and return data for charts."""
    data = load_data()
    if data.empty:
        return {
            "avg_temp": "No Data",
            "running_percentage": "No Data",
            "data": data
        }

    # ✅ Ensure "Is Running" column exists and convert properly
    if "Is Running" not in data.columns:
        raise KeyError("❌ 'Is Running' column is missing in the dataset!")
    
    data["Is Running"] = data["Is Running"].astype(str).str.lower().map({"true": 1, "false": 0, "1": 1, "0": 0}).fillna(0)
    
    # ✅ Ensure "Driving End Temp" and "Driven End Temp" exist & are numeric
    for col in ["Driving End Temp", "Driven End Temp"]:
        if col not in data.columns:
            data[col] = 0  # Set default value
        data[col] = pd.to_numeric(data[col], errors="coerce")
    
    # ✅ Compute KPIs safely
    avg_temp = data[["Driving End Temp", "Driven End Temp"]].mean().mean() if not data[["Driving End Temp", "Driven End Temp"]].empty else 0
    running_percentage = (data["Is Running"].sum() / len(data)) * 100 if len(data) > 0 else 0
    
    return {
        "avg_temp": f"{avg_temp:.2f}°C",
        "running_percentage": f"{running_percentage:.2f}%",
        "data": data
    }

# Function to set background image from an online URL
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Use the corrected GitHub raw image URL
set_background("https://raw.githubusercontent.com/Eous-morning-star/INDORAMA-MAIN/main/picture.jpg")

# Display the logo at the top of the homepage
st.image("indorama_logo.png", use_container_width=True)

# Main Page Functionality
if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
        #Main Page
    st.subheader("Your Gateway to Enhanced Maintenance Efficiency")

    # Greeting Based on Time
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"

    st.header(greeting)

    # Footer Section
    st.write("---")  # Separator line
    st.write("### 📜 Footer Information")

    st.write("""
                - **Application Version**: 1.0.0  
                - **Developer**: [Nwaoba Kenneth / PE Mechanical]
                - **Approved by**: [Nitin Narkhede / Mechanical]
                - **Contact Support**: [kenneth.nwaoba@indorama.com](mailto:support@yourcompany.com)
                """)

    st.write("""
                This application is designed to improve condition monitoring and maintenance tracking for Indorama Petrochemicals Ltd/OBOB GAS PLANT.
                For assistance or feedback, please reach out via the support link above. This application is approved by Mr. Nitin Narkhede (nitin.narkhede@indorama.com)
                """)

    # Display KPIs
    st.subheader("Key Performance Indicators (KPIs)")
    kpis = calculate_kpis()
    col1, col2 = st.columns(2)
    col1.metric("Average Temperature", kpis["avg_temp"])
    col2.metric("Running Equipment", kpis["running_percentage"])

    st.write("---")

    # ✅ Weekly Report Dashboard
    st.title("Weekly Report Dashboard")
    
    # ✅ Filter by date range
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7), key="weekly_report_start_date")
    end_date = st.date_input("End Date", value=datetime.now(), key="weekly_report_end_date")
    
    # ✅ Load the data
    data = load_data()
    
    if data.empty:
        st.warning("No data available. Please enter condition monitoring data first.")
    else:
        # ✅ Ensure Required Columns Exist
        required_columns = ["Date", "Equipment", "Driving End Temp", "Driven End Temp", "DE Horizontal RMS (mm/s)", "DE Vertical RMS (mm/s)", "DE Axial RMS (mm/s)", "NDE Horizontal RMS (mm/s)", "NDE Vertical RMS (mm/s)", "NDE Axial RMS (mm/s)", 
        "Motor Driving End Temp", "Motor Driven End Temp", "Motor DE Horizontal RMS (mm/s)", "Motor DE Vertical RMS (mm/s)", "Motor DE Axial RMS (mm/s)", "Motor NDE Horizontal RMS (mm/s)", "Motor NDE Vertical RMS (mm/s)", "Motor NDE Axial RMS (mm/s)", "Is Running"]
        if not validate_columns(data, required_columns):
            st.error("Dataset does not contain all required columns for analysis.")
        else:
            # ✅ Convert columns to correct types
            data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
            data["Is Running"] = data["Is Running"].astype(str).str.lower() == "true"  # Convert to boolean
            
            # ✅ Ensure numeric values
            for col in ["Driving End Temp", "Driven End Temp", "DE Horizontal RMS (mm/s)", "DE Vertical RMS (mm/s)", "DE Axial RMS (mm/s)", "NDE Horizontal RMS (mm/s)", "NDE Vertical RMS (mm/s)", "NDE Axial RMS (mm/s)", 
        "Motor Driving End Temp", "Motor Driven End Temp", "Motor DE Horizontal RMS (mm/s)", "Motor DE Vertical RMS (mm/s)", "Motor DE Axial RMS (mm/s)", "Motor NDE Horizontal RMS (mm/s)", "Motor NDE Vertical RMS (mm/s)", "Motor NDE Axial RMS (mm/s)"]:
                data[col] = pd.to_numeric(data[col], errors="coerce")
    
            # ✅ Filter data based on date range and running equipment
            filtered_data = data[
                (data["Date"] >= pd.Timestamp(start_date)) &
                (data["Date"] <= pd.Timestamp(end_date)) &
                (data["Is Running"] == True)  # Only include running equipment
            ]
    
            if filtered_data.empty:
                st.success("✅ All equipment is operating within thresholds, or no running equipment was found for the selected date range.")
            else:
                # ✅ Check for deviations
                deviations = []
    
                for _, row in filtered_data.iterrows():
                    equipment = row["Equipment"].strip()  # Remove any extra spaces

                    
    
                    if equipment in equipment_thresholds:
                        thresholds = equipment_thresholds[equipment]  # ✅ Moved inside the loop
    
                        if (
                            not (thresholds["Driving End Temp"]["min"] <= row["Driving End Temp"] <= thresholds["Driving End Temp"]["max"]) or
                            not (thresholds["Driven End Temp"]["min"] <= row["Driven End Temp"] <= thresholds["Driven End Temp"]["max"]) or
                            not (thresholds["Motor Driving End Temp"]["min"] <= row["Motor Driving End Temp"] <= thresholds["Motor Driving End Temp"]["max"]) or
                            not (thresholds["Motor Driven End Temp"]["min"] <= row["Motor Driven End Temp"] <= thresholds["Motor Driven End Temp"]["max"]) or
                            not (thresholds["DE Horizontal RMS (mm/s)"]["min"] <= row["DE Horizontal RMS (mm/s)"] <= thresholds["DE Horizontal RMS (mm/s)"]["max"]) or
                            not (thresholds["NDE Horizontal RMS (mm/s)"]["min"] <= row["NDE Horizontal RMS (mm/s)"] <= thresholds["NDE Horizontal RMS (mm/s)"]["max"]) or
                            not (thresholds["DE Vertical RMS (mm/s)"]["min"] <= row["DE Vertical RMS (mm/s)"] <= thresholds["DE Vertical RMS (mm/s)"]["max"]) or
                            not (thresholds["NDE Vertical RMS (mm/s)"]["min"] <= row["NDE Vertical RMS (mm/s)"] <= thresholds["NDE Vertical RMS (mm/s)"]["max"]) or
                            not (thresholds["DE Axial RMS (mm/s)"]["min"] <= row["DE Axial RMS (mm/s)"] <= thresholds["DE Axial RMS (mm/s)"]["max"]) or
                            not (thresholds["NDE Axial RMS (mm/s)"]["min"] <= row["DE Axial RMS (mm/s)"] <= thresholds["DE Axial RMS (mm/s)"]["max"]) or
                            not (thresholds["Motor DE Horizontal RMS (mm/s)"]["min"] <= row["Motor DE Horizontal RMS (mm/s)"] <= thresholds["Motor DE Horizontal RMS (mm/s)"]["max"]) or
                            not (thresholds["Motor NDE Horizontal RMS (mm/s)"]["min"] <= row["Motor NDE Horizontal RMS (mm/s)"] <= thresholds["Motor NDE Horizontal RMS (mm/s)"]["max"]) or
                            not (thresholds["Motor DE Vertical RMS (mm/s)"]["min"] <= row["Motor DE Vertical RMS (mm/s)"] <= thresholds["Motor DE Vertical RMS (mm/s)"]["max"]) or
                            not (thresholds["Motor NDE Vertical RMS (mm/s)"]["min"] <= row["Motor NDE Vertical RMS (mm/s)"] <= thresholds["Motor NDE Vertical RMS (mm/s)"]["max"]) or
                            not (thresholds["Motor DE Axial RMS (mm/s)"]["min"] <= row["Motor DE Axial RMS (mm/s)"] <= thresholds["Motor DE Axial RMS (mm/s)"]["max"]) or
                            not (thresholds["Motor NDE Axial RMS (mm/s)"]["min"] <= row["Motor NDE Axial RMS (mm/s)"] <= thresholds["NDE Axial RMS (mm/s)"]["max"])
                        ):
                            deviations.append(row)
    
                deviation_data = pd.DataFrame(deviations)
    
                if deviation_data.empty:
                    st.success("✅ All running equipment is within the specified thresholds.")
                else:
                    st.subheader("⚠️ Running Equipment with Deviations")
                    st.dataframe(deviation_data)
    
                    # ✅ Generate Recommendations
                    st.write("### 🔍 Recommendations")
                    recommendations = []
    
                    for _, row in deviation_data.iterrows():
                        equipment = row["Equipment"]
                        thresholds = equipment_thresholds.get(equipment, {})
    
                        if thresholds:
                            
                            if not (thresholds["Driving End Temp"]["min"] <= row["Driving End Temp"] <= thresholds["Driving End Temp"]["max"]):
                                recommendations.append(f"🔧 **{equipment}**: Driving End Temp is outside the range {thresholds['Driving End Temp']['min']} - {thresholds['Driving End Temp']['max']} °C.")

                            if not (thresholds["Driven End Temp"]["min"] <= row["Driven End Temp"] <= thresholds["Driven End Temp"]["max"]):
                                recommendations.append(f"🔧 **{equipment}**: Driven End Temp is outside the range {thresholds['Driven End Temp']['min']} - {thresholds['Driven End Temp']['max']} °C.")

                            if not (thresholds["Motor Driving End Temp"]["min"] <= row["Motor Driving End Temp"] <= thresholds["Motor Driving End Temp"]["max"]):
                                recommendations.append(f"🔧 **{equipment}**: Motor Driving End Temp is outside the range {thresholds['Motor Driving End Temp']['min']} - {thresholds['Motor Driving End Temp']['max']} °C.")

                            if not (thresholds["Motor Driven End Temp"]["min"] <= row["Motor Driven End Temp"] <= thresholds["Motor Driven End Temp"]["max"]):
                                recommendations.append(f"🔧 **{equipment}**: Motor Driven End Temp is outside the range {thresholds['Motor Driven End Temp']['min']} - {thresholds['Motor Driven End Temp']['max']} °C.")

                            if not (thresholds["DE Horizontal RMS (mm/s)"]["min"] <= row["DE Horizontal RMS (mm/s)"] <= thresholds["DE Horizontal RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: DE Horizontal RMS is outside the range {thresholds['DE Horizontal RMS (mm/s)']['min']} - {thresholds['DE Horizontal RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["NDE Horizontal RMS (mm/s)"]["min"] <= row["NDE Horizontal RMS (mm/s)"] <= thresholds["NDE Horizontal RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: NDE Horizontal RMS is outside the range {thresholds['NDE Horizontal RMS (mm/s)']['min']} - {thresholds['NDE Horizontal RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["DE Vertical RMS (mm/s)"]["min"] <= row["DE Vertical RMS (mm/s)"] <= thresholds["DE Vertical RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: DE Vertical RMS is outside the range {thresholds['DE Vertical RMS (mm/s)']['min']} - {thresholds['DE Vertical RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["NDE Vertical RMS (mm/s)"]["min"] <= row["NDE Vertical RMS (mm/s)"] <= thresholds["NDE Vertical RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: NDE Vertical RMS is outside the range {thresholds['NDE Vertical RMS (mm/s)']['min']} - {thresholds['NDE Vertical RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["DE Axial RMS (mm/s)"]["min"] <= row["DE Axial RMS (mm/s)"] <= thresholds["DE Axial RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: DE Axial RMS is outside the range {thresholds['DE Axial RMS (mm/s)']['min']} - {thresholds['DE Axial RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["NDE Axial RMS (mm/s)"]["min"] <= row["NDE Axial RMS (mm/s)"] <= thresholds["NDE Axial RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: NDE Axial RMS is outside the range {thresholds['NDE Axial RMS (mm/s)']['min']} - {thresholds['NDE Axial RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["Motor DE Horizontal RMS (mm/s)"]["min"] <= row["Motor DE Horizontal RMS (mm/s)"] <= thresholds["Motor DE Horizontal RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: Motor DE Horizontal RMS is outside the range {thresholds['Motor DE Horizontal RMS (mm/s)']['min']} - {thresholds['Motor DE Horizontal RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["Motor NDE Horizontal RMS (mm/s)"]["min"] <= row["Motor NDE Horizontal RMS (mm/s)"] <= thresholds["Motor NDE Horizontal RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: Motor NDE Horizontal RMS is outside the range {thresholds['Motor NDE Horizontal RMS (mm/s)']['min']} - {thresholds['Motor NDE Horizontal RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["Motor DE Vertical RMS (mm/s)"]["min"] <= row["Motor DE Vertical RMS (mm/s)"] <= thresholds["Motor DE Vertical RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: Motor DE Vertical RMS is outside the range {thresholds['Motor DE Vertical RMS (mm/s)']['min']} - {thresholds['Motor DE Vertical RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["Motor NDE Vertical RMS (mm/s)"]["min"] <= row["Motor NDE Vertical RMS (mm/s)"] <= thresholds["Motor NDE Vertical RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: Motor NDE Vertical RMS is outside the range {thresholds['Motor NDE Vertical RMS (mm/s)']['min']} - {thresholds['Motor NDE Vertical RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["Motor DE Axial RMS (mm/s)"]["min"] <= row["Motor DE Axial RMS (mm/s)"] <= thresholds["Motor DE Axial RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: Motor DE Axial RMS is outside the range {thresholds['Motor DE Axial RMS (mm/s)']['min']} - {thresholds['Motor DE Axial RMS (mm/s)']['max']} mm/s.")

                            if not (thresholds["Motor NDE Axial RMS (mm/s)"]["min"] <= row["Motor NDE Axial RMS (mm/s)"] <= thresholds["Motor NDE Axial RMS (mm/s)"]["max"]):
                                recommendations.append(f"📊 **{equipment}**: Motor NDE Axial RMS is outside the range {thresholds['Motor NDE Axial RMS (mm/s)']['min']} - {thresholds['Motor NDE Axial RMS (mm/s)']['max']} mm/s.")

                            if row["DE Oil Level"] == "Low":
                                recommendations.append(f"🛢️ **{equipment}**: Oil level is low. Consider refilling.")

                            if row["NDE Oil Level"] == "Low":
                                recommendations.append(f"🛢️ **{equipment}**: Oil level is low. Consider refilling.")

                    if recommendations:
                        for rec in recommendations:
                            st.info(rec)
                    else:
                        st.success("✅ No immediate issues detected in the deviations data.")
                    # ✅ Add CSS to make the "Download Report" button black
                    st.markdown(
                        """
                        <style>
                        div.stDownloadButton > button {
                            background-color: black !important;
                            color: white !important;
                            border-radius: 10px !important;
                            padding: 10px 15px !important;
                            font-size: 16px !important;
                            font-weight: bold !important;
                            border: 2px solid white !important;
                        }
                    
                        div.stDownloadButton > button:hover {
                            background-color: #333 !important;
                            color: white !important;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                    # ✅ Download Weekly Report
                    st.write("#### Download Weekly Report")
                    csv = deviation_data.to_csv(index=False)
                    st.download_button("Download Report as CSV", data=csv, file_name="weekly_report.csv", mime="text/csv")

        # Ensure data is available from KPI calculation
    data = kpis["data"]

    if not data.empty:  # Check if the data is available
        st.write("---")
        st.subheader("Running Equipment by Area")

        # Calculate the percentage of running equipment per area
        if "Area" in data.columns and "Is Running" in data.columns:
            running_percentage_by_area = (
                    data.groupby("Area")["Is Running"].mean() * 100
            ).reset_index()
            running_percentage_by_area.rename(
                columns={"Is Running": "Running Percentage (%)"}, inplace=True
            )

            # Display the table
            st.table(running_percentage_by_area)
        else:
            st.warning("The dataset does not contain 'Area' or 'Is Running' columns.")
    else:
        st.warning("No data available to calculate running equipment percentages.")

    # Add KPI Charts
    data = kpis["data"]
    if not data.empty:  # Check if data is available
        st.write("---")
        st.subheader("KPI Charts")

        import plotly.express as px

        # Average Temperature Trend
        if "Driving End Temp" in data.columns and "Driven End Temp" in data.columns:
            # Calculate the average temperature
            data["Avg Temp"] = data[["Driving End Temp", "Driven End Temp"]].mean(axis=1)

            # Aggregate average temperature by date
            avg_temp_trend = data.groupby("Date", as_index=False)["Avg Temp"].mean()

            st.write("### Average Temperature Trend")

            # Create a Plotly line chart
            fig = px.line(
                avg_temp_trend,
                x="Date",
                y="Avg Temp",
                title="Average Temperature Trend Over Time",
                labels={"Avg Temp": "Average Temperature (°C)", "Date": "Date"},
                markers=True,  # Adds markers for each data point
            )

            # Enhance chart aesthetics
            fig.update_traces(line=dict(width=2))
            fig.update_layout(
                title_font_size=18,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                hovermode="x unified",  # Combine hover info
            )

            st.plotly_chart(fig)
        else:
            st.warning("Temperature data (Driving End or Driven End) is missing in the dataset.")


        # Running Equipment Count
        if "Is Running" in data.columns and "Area" in data.columns:
            running_equipment_by_area = data.groupby(["Date", "Area"])["Is Running"].sum().reset_index()
            st.write("### Running Equipment Count by Area")

            # Create the bar chart with Plotly
            fig = px.bar(
                running_equipment_by_area,
                x="Date",
                y="Is Running",
                color="Area",
                title="Running Equipment Count by Area",
                labels={"Is Running": "Running Equipment Count"},
            )
            fig.update_layout(barmode="stack")
            st.plotly_chart(fig)
        else:
            st.warning("The dataset does not contain 'Is Running' or 'Area' columns.")

    else:
        st.warning("No data available for KPI charts.")


    # Next Button to Navigate
    if st.button("Next"):
        st.session_state.page = "monitoring"

elif st.session_state.page == "monitoring":
            
    def filter_data(df, equipment, start_date, end_date):
        """Filter data by equipment and date range."""
        df["Date"] = pd.to_datetime(df["Date"])  # Convert Date column to datetime
        filtered_df = df[
            (df["Equipment"] == equipment) &
            (df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date))
            ]
        return filtered_df

    # Tabs for Condition Monitoring and Report
    tab1, tab2 = st.tabs(["Condition Monitoring", "Report"])

    with tab1:
        st.header("Condition Monitoring Data Entry")

        # Equipment lists for each area
        equipment_lists = {
            "1670": [
                "1670-PA-02A", "1670-PA-02B", "1670-PA-02C", "1670-PA-04A", "1670-PA-04B",
                "1670-PA-04C"
            ],
            "1600": [
                "1600-PA-04A", "1600-PA-04B", "1600-KF-02A", "1600-KF-02B", "1600-KF-02C" 
            ],
            "1680": [
                "1680-PA-01A", "1680-PA-01B", "1680-PH-01A", "1680-PH-01B"
            ],
        }

        # ✅ Store last selected equipment
        if "last_selected_equipment" not in st.session_state:
            st.session_state.last_selected_equipment = None
            
        # ✅ Persistent fields
        date = st.date_input("Date", key="date", value=datetime.now().date())
        area = st.selectbox("Select Area", options=list(equipment_lists.keys()), key="area")
        equipment_options = equipment_lists.get(area, [])
        selected_equipment = st.selectbox("Select Equipment", options=equipment_options, key="equipment")

    # ✅ Reset "Is Running" when new equipment is selected
        if st.session_state.last_selected_equipment != selected_equipment:
            st.session_state.is_running = False
            st.session_state.last_selected_equipment = selected_equipment  # Update last selected equipment

    # ✅ Checkbox for "Is the equipment running?"
        is_running = st.checkbox("Is the equipment running?", key="is_running")
        
        # Data Entry Fields
        if is_running:
            de_temp = st.number_input("Driving End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                      key="de_temp")
            dr_temp = st.number_input("Driven End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                      key="dr_temp")
            de_oil_level = st.selectbox("DE Oil Level", ["Normal", "Low", "High"], key="de_oil_level")
            nde_oil_level = st.selectbox("NDE Oil Level", ["Normal", "Low", "High"], key="nde_oil_level")
            abnormal_sound = st.selectbox("Abnormal Sound", ["No", "Yes"], key="abnormal_sound")
            leakage = st.selectbox("Leakage", ["No", "Yes"], key="leakage")
            observation = st.text_area("Observations", key="observation")

            # Vibration Monitoring for de
            st.subheader("DE Vibration Monitoring")
            de_horizontal_vibration_rms_velocity = st.number_input("DE Horizontal RMS (mm/s)", min_value=0.0, max_value=100.0,
                                                     step=0.1,
                                                     key="de_horizontal_vibration_rms_velocity")
            de_vertical_vibration_rms_velocity = st.number_input("DE Vertical RMS (mm/s)", min_value=0.0, max_value=10.0,
                                                          step=0.1,
                                                          key="de_vertical_vibration_rms_velocity")
            de_axial_vibration_rms_velocity = st.number_input("DE Axial RMS (mm/s)", min_value=0.0, max_value=1000.0, step=0.1,
                                                     key="de_axial_vibration_rms_velocity")

            # Vibration Monitoring for motor nde
            st.subheader("NDE Vibration Monitoring")
            nde_horizontal_vibration_rms_velocity = st.number_input("NDE Horizontal RMS (mm/s)", min_value=0.0, max_value=100.0,
                                                     step=0.1,
                                                     key="nde_horizontal_vibration_rms_velocity")
            nde_vertical_vibration_rms_velocity = st.number_input("NDE Vertical RMS (mm/s)", min_value=0.0, max_value=10.0,
                                                          step=0.1,
                                                          key="nde_vertical_vibration_rms_velocity")
            nde_axial_vibration_rms_velocity = st.number_input("NDE Axial RMS (mm/s)", min_value=0.0, max_value=1000.0, step=0.1,
                                                     key="nde_axial_vibration_rms_velocity")                            

            # Motor Inputs
            st.subheader("Motor Monitoring")
            motor_de_temp = st.number_input("Motor Driving End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                  key="motor_de_temp")
            motor_dr_temp = st.number_input("Motor Driven End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                  key="motor_dr_temp")
            motor_abnormal_sound = st.selectbox("Motor Abnormal Sound", ["No", "Yes"], key="motor_abnormal_sound")
            
            # Vibration Monitoring for motor de
            st.subheader("Motor DE Vibration Monitoring")
            motor_de_horizontal_vibration_rms_velocity = st.number_input("Motor DE Horizontal RMS (mm/s)", min_value=0.0, max_value=100.0,
                                                     step=0.1,
                                                     key="motor_de_horizontal_vibration_rms_velocity")
            motor_de_vertical_vibration_rms_velocity = st.number_input("Motor DE Vertical RMS (mm/s)", min_value=0.0, max_value=10.0,
                                                          step=0.1,
                                                          key="motor_de_vertical_vibration_rms_velocity")
            motor_de_axial_vibration_rms_velocity = st.number_input("Motor DE Axial RMS (mm/s)", min_value=0.0, max_value=1000.0, step=0.1,
                                                     key="motor_de_axial_vibration_rms_velocity")

            # Vibration Monitoring for motor nde
            st.subheader("Motor NDE Vibration Monitoring")
            motor_nde_horizontal_vibration_rms_velocity = st.number_input("Motor NDE Horizontal RMS (mm/s)", min_value=0.0, max_value=100.0,
                                                     step=0.1,
                                                     key="motor_nde_horizontal_vibration_rms_velocity")
            motor_nde_vertical_vibration_rms_velocity = st.number_input("Motor NDE Vertical RMS (mm/s)", min_value=0.0, max_value=10.0,
                                                          step=0.1,
                                                          key="motor_nde_vertical_vibration_rms_velocity")
            motor_nde_axial_vibration_rms_velocity = st.number_input("Motor NDE Axial RMS (mm/s)", min_value=0.0, max_value=1000.0, step=0.1,
                                                     key="motor_nde_axial_vibration_rms_velocity")                                        

        # Submit Button
        
        if st.button("Submit Data"):
            try:
                # ✅ Retrieve values correctly from session state
                date = st.session_state.date
                area = st.session_state.area
                equipment = st.session_state.equipment  # 🔥 Fix: Ensure we get equipment correctly
                is_running = st.session_state.is_running
                
                new_data = pd.DataFrame([{
                    "Date": date.strftime("%Y-%m-%d"),
                    "Area": area,
                    "Equipment": equipment,
                    "Is Running": is_running,
                    "Driving End Temp": de_temp if is_running else 0.0,
                    "Driven End Temp": dr_temp if is_running else 0.0,
                    "DE Oil Level": de_oil_level if is_running else "N/A",
                    "NDE Oil Level": nde_oil_level if is_running else "N/A",
                    "Abnormal Sound": abnormal_sound if is_running else "N/A",
                    "Leakage": leakage if is_running else "N/A",
                    "Observation": observation if is_running else "Not Running",
                    "DE Horizontal RMS (mm/s)": de_horizontal_vibration_rms_velocity if is_running else 0.0,
                    "DE Vertical RMS (mm/s)": de_vertical_vibration_rms_velocity if is_running else 0.0,
                    "DE Axial RMS (mm/s)": de_axial_vibration_rms_velocity if is_running else 0.0,
                    "NDE Horizontal RMS (mm/s)": nde_horizontal_vibration_rms_velocity if is_running else 0.0,
                    "NDE Vertical RMS (mm/s)": nde_vertical_vibration_rms_velocity if is_running else 0.0,
                    "NDE Axial RMS (mm/s)": nde_axial_vibration_rms_velocity if is_running else 0.0,
                    "Motor Driving End Temp": motor_de_temp if is_running else 0.0,
                    "Motor Driven End Temp": motor_dr_temp if is_running else 0.0,
                    "Motor Abnormal Sound": motor_abnormal_sound if is_running else "N/A",
                    "Motor DE Horizontal RMS (mm/s)": motor_de_horizontal_vibration_rms_velocity if is_running else 0.0,
                    "Motor DE Vertical RMS (mm/s)": motor_de_vertical_vibration_rms_velocity if is_running else 0.0,
                    "Motor DE Axial RMS (mm/s)": motor_de_axial_vibration_rms_velocity if is_running else 0.0,
                    "Motor NDE Horizontal RMS (mm/s)": motor_nde_horizontal_vibration_rms_velocity if is_running else 0.0,
                    "Motor NDE Vertical RMS (mm/s)": motor_nde_vertical_vibration_rms_velocity if is_running else 0.0,
                    "Motor NDE Axial RMS (mm/s)": motor_nde_axial_vibration_rms_velocity if is_running else 0.0,
                }])
        
                # ✅ Ensure Google Sheets connection exists
                if sheet:
                    existing_data = sheet.get_all_records()
                    df = pd.DataFrame(existing_data)
                    df = pd.concat([df, new_data], ignore_index=True)
                
                    # ✅ Save updated data to Google Sheets
                    sheet.clear()
                    sheet.update([df.columns.values.tolist()] + df.values.tolist())
                
                    st.success("✅ Data saved to Google Sheets!")

                else:
                    st.error("❌ Unable to save data: Google Sheet connection is missing.")
            except Exception as e:
                st.error(f"Error saving data: {e}")


    # Tab 2: Reports and Visualizations
    with tab2:
        st.header("Reports and Visualization")
        file_path = "data/condition_data.csv"

        # Load data
        data = load_data()

        if data.empty:
            st.warning("No data available. Please enter condition monitoring data first.")
        else:
            st.write("### Full Data")
            st.dataframe(data)

            # Check if 'Equipment' column exists
            if "Equipment" not in data.columns:
                st.error("The 'Equipment' column is missing. Please check the data file.")
            else:
                # Combine all equipment into a single list
                all_equipment = [equipment for area in equipment_lists.values() for equipment in area]

                # Dropdown for Equipment Selection
                equipment_options = data["Equipment"].unique()
                selected_equipment = st.selectbox("Select Equipment", options=equipment_options)

                # Date Range Inputs
                start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
                end_date = st.date_input("End Date", value=datetime.now())

                if start_date > end_date:
                    st.error("Start date cannot be later than end date.")
                else:
                    # Filter Data
                    filtered_data = filter_data(data, selected_equipment, start_date, end_date)

                    if filtered_data.empty:
                        st.warning(f"No data found for {selected_equipment} between {start_date} and {end_date}.")
                    else:
                        st.write(f"### Filtered Data for {selected_equipment}")
                        st.dataframe(filtered_data)

                        # ✅ Visualization Section
                        st.subheader("Data Visualizations")
                        
                        # Allow user to choose the dataset for visualization
                        data_option = st.radio(
                            "Select data for visualization:",
                            options=["General Table (All Data)", "Filtered Table"],
                            key="data_option"
                        )
                        
                        # Select appropriate dataset based on user choice
                        if data_option == "General Table (All Data)":
                            visualization_data = data  # Use the full dataset
                            st.write("Using data from the general table (all records).")
                        else:
                            visualization_data = filtered_data  # Use the filtered dataset
                            st.write("Using data from the filtered table.")
                        
                        # ✅ Retrieve max limits from thresholds
                        if selected_equipment in equipment_thresholds:
                            thresholds = equipment_thresholds[selected_equipment]
                        else:
                            thresholds = {}  # Default to empty if no thresholds available
                        
                        # Driving and Driven End Temperature Trend
                        if "Driving End Temp" in visualization_data.columns and "Driven End Temp" in visualization_data.columns:
                            st.write("#### Driving and Driven End Temperature Trend for Equipment")
                            temp_chart_data = visualization_data[["Date", "Driving End Temp", "Driven End Temp"]].melt(
                                id_vars="Date",
                                var_name="Temperature Type",
                                value_name="Temperature"
                            )
                            fig = px.line(
                                temp_chart_data,
                                x="Date",
                                y="Temperature",
                                color="Temperature Type",
                                title="Driving and Driven End Temperature Trend",
                                labels={"Temperature": "Temperature (°C)"}
                            )
                        
                            # ✅ Add max limit lines if available
                            if "Driving End Temp" in thresholds:
                                fig.add_hline(y=thresholds["Driving End Temp"]["max"], line_dash="dash", line_color="red",
                                              annotation_text="Max Driving Temp")
                            if "Driven End Temp" in thresholds:
                                fig.add_hline(y=thresholds["Driven End Temp"]["max"], line_dash="dash", line_color="blue",
                                              annotation_text="Max Driven Temp")
                        
                            st.plotly_chart(fig)
                        else:
                            st.warning("Temperature data (Driving End or Driven End) is missing in the selected dataset.")
                        
                        # Equipment DE Vibration Trend
                        if all(col in visualization_data.columns for col in ["DE Horizontal RMS (mm/s)", "DE Vertical RMS (mm/s)", "DE Axial RMS (mm/s)"]):
                            st.write("#### Vibration Trend for Equipment DE")
                            vibration_chart_data = visualization_data[
                                ["Date", "DE Horizontal RMS (mm/s)", "DE Vertical RMS (mm/s)", "DE Axial RMS (mm/s)"]
                            ].melt(id_vars="Date", var_name="Vibration Type", value_name="Value")
                        
                            fig = px.line(
                                vibration_chart_data,
                                x="Date",
                                y="Value",
                                color="Vibration Type",
                                title="Vibration Trend for Equipment DE",
                                labels={"Value": "Vibration RMS (mm/s)"}
                            )
                        
                            # ✅ Add max limit lines if available
                            for vib_type in ["DE Horizontal RMS (mm/s)", "DE Vertical RMS (mm/s)", "DE Axial RMS (mm/s)"]:
                                if vib_type in thresholds:
                                    fig.add_hline(y=thresholds[vib_type]["max"], line_dash="dash", line_color="red",
                                                  annotation_text=f"Max {vib_type}")
                        
                            st.plotly_chart(fig)
                        else:
                            st.warning("DE Vibration data is missing in the selected dataset.")
                        
                        # Equipment NDE Vibration Trend
                        if all(col in visualization_data.columns for col in ["NDE Horizontal RMS (mm/s)", "NDE Vertical RMS (mm/s)", "NDE Axial RMS (mm/s)"]):
                            st.write("#### Vibration Trend for Equipment NDE")
                            vibration_chart_data = visualization_data[
                                ["Date", "NDE Horizontal RMS (mm/s)", "NDE Vertical RMS (mm/s)", "NDE Axial RMS (mm/s)"]
                            ].melt(id_vars="Date", var_name="Vibration Type", value_name="Value")
                        
                            fig = px.line(
                                vibration_chart_data,
                                x="Date",
                                y="Value",
                                color="Vibration Type",
                                title="Vibration Trend for Equipment NDE",
                                labels={"Value": "Vibration RMS (mm/s)"}
                            )
                        
                            # ✅ Add max limit lines if available
                            for vib_type in ["NDE Horizontal RMS (mm/s)", "NDE Vertical RMS (mm/s)", "NDE Axial RMS (mm/s)"]:
                                if vib_type in thresholds:
                                    fig.add_hline(y=thresholds[vib_type]["max"], line_dash="dash", line_color="red",
                                                  annotation_text=f"Max {vib_type}")
                        
                            st.plotly_chart(fig)
                        else:
                            st.warning("NDE Vibration data is missing in the selected dataset.")
                        
                        # Motor Driving and Motor Driven End Temperature Trend
                        if "Motor Driving End Temp" in visualization_data.columns and "Motor Driven End Temp" in visualization_data.columns:
                            st.write("#### Motor Driving and Motor Driven End Temperature Trend for Equipment")
                            temp_chart_data = visualization_data[["Date", "Motor Driving End Temp", "Motor Driven End Temp"]].melt(
                                id_vars="Date",
                                var_name="Temperature Type",
                                value_name="Temperature"
                            )
                            fig = px.line(
                                temp_chart_data,
                                x="Date",
                                y="Temperature",
                                color="Temperature Type",
                                title="Motor Driving and Motor Driven End Temperature Trend",
                                labels={"Temperature": "Temperature (°C)"}
                            )
                        
                            # ✅ Add max limit lines if available
                            if "Motor Driving End Temp" in thresholds:
                                fig.add_hline(y=thresholds["Motor Driving End Temp"]["max"], line_dash="dash", line_color="red",
                                              annotation_text="Max Motor Driving Temp")
                            if "Motor Driven End Temp" in thresholds:
                                fig.add_hline(y=thresholds["Motor Driven End Temp"]["max"], line_dash="dash", line_color="blue",
                                              annotation_text="Max Motor Driven Temp")
                        
                            st.plotly_chart(fig)
                        else:
                            st.warning("Motor Temperature data is missing in the selected dataset.")
                        
                        # Motor DE Vibration Trend
                        if all(col in visualization_data.columns for col in ["Motor DE Horizontal RMS (mm/s)", "Motor DE Vertical RMS (mm/s)", "Motor DE Axial RMS (mm/s)"]):
                            st.write("#### Vibration Trend for Motor DE")
                            vibration_chart_data = visualization_data[
                                ["Date", "Motor DE Horizontal RMS (mm/s)", "Motor DE Vertical RMS (mm/s)", "Motor DE Axial RMS (mm/s)"]
                            ].melt(id_vars="Date", var_name="Vibration Type", value_name="Value")
                        
                            fig = px.line(
                                vibration_chart_data,
                                x="Date",
                                y="Value",
                                color="Vibration Type",
                                title="Vibration Trend for Motor DE",
                                labels={"Value": "Vibration RMS (mm/s)"}
                            )
                        
                            # ✅ Add max limit lines if available
                            for vib_type in ["Motor DE Horizontal RMS (mm/s)", "Motor DE Vertical RMS (mm/s)", "Motor DE Axial RMS (mm/s)"]:
                                if vib_type in thresholds:
                                    fig.add_hline(y=thresholds[vib_type]["max"], line_dash="dash", line_color="red",
                                                  annotation_text=f"Max {vib_type}")
                        
                            st.plotly_chart(fig)
                        else:
                            st.warning("Motor DE Vibration data is missing in the selected dataset.")
                        
                        # Motor NDE Vibration Trend
                        if all(col in visualization_data.columns for col in ["Motor NDE Horizontal RMS (mm/s)", "Motor NDE Vertical RMS (mm/s)", "Motor NDE Axial RMS (mm/s)"]):
                            st.write("#### Vibration Trend for Motor NDE")
                            vibration_chart_data = visualization_data[
                                ["Date", "Motor NDE Horizontal RMS (mm/s)", "Motor NDE Vertical RMS (mm/s)", "Motor NDE Axial RMS (mm/s)"]
                            ].melt(id_vars="Date", var_name="Vibration Type", value_name="Value")
                        
                            fig = px.line(
                                vibration_chart_data,
                                x="Date",
                                y="Value",
                                color="Vibration Type",
                                title="Vibration Trend for Motor NDE",
                                labels={"Value": "Vibration RMS (mm/s)"}
                            )
                        
                            # ✅ Add max limit lines if available
                            for vib_type in ["Motor NDE Horizontal RMS (mm/s)", "Motor NDE Vertical RMS (mm/s)", "Motor NDE Axial RMS (mm/s)"]:
                                if vib_type in thresholds:
                                    fig.add_hline(y=thresholds[vib_type]["max"], line_dash="dash", line_color="red",
                                                  annotation_text=f"Max {vib_type}")
                        
                            st.plotly_chart(fig)
                        else:
                            st.warning("Motor NDE Vibration data is missing in the selected dataset.")
# Add Back Button
if st.button("Back to Home"):
    st.session_state.page = "main"
