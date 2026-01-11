import streamlit as st
import google.generativeai as genai
import json
from datetime import date
import io
import requests
import urllib.parse
import random
import re
import base64
import os

# --- NEW LIBRARY FOR WORD DOCS ---
from docx import Document
from docx.shared import Inches, Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="DLP Generator", layout="centered")

# --- 2. API KEY EMBEDDED IN CODE ---
# Replace this with your actual Google AI API key
EMBEDDED_API_KEY = "AIza......"  # REPLACE WITH YOUR ACTUAL KEY

# --- 3. IMAGE HANDLING FIXED FOR YOUR FILES ---
def get_image_base64(image_filename):
    """Get base64 encoded image or use placeholder"""
    try:
        if os.path.exists(image_filename):
            with open(image_filename, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        else:
            # Try to find file with similar name
            for file in os.listdir('.'):
                if image_filename.lower() in file.lower():
                    with open(file, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        st.sidebar.warning(f"Error loading {image_filename}: {str(e)}")
    return None

def add_custom_header():
    """Add custom header with maroon background and logos"""
    
    st.markdown("""
    <style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        margin-bottom: 25px;
        background-color: #800000; /* MAROON BACKGROUND */
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(128, 0, 0, 0.3);
        color: white;
    }
    .logo-box {
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        border: 2px solid white;
        border-radius: 8px;
        padding: 5px;
    }
    .logo-box img {
        max-width: 90px;
        max-height: 90px;
        object-fit: contain;
    }
    .logo-placeholder {
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid white;
        border-radius: 8px;
        color: #800000;
        font-size: 12px;
        text-align: center;
        padding: 5px;
        font-weight: bold;
    }
    .center-content {
        text-align: center;
        flex-grow: 1;
        padding: 0 25px;
    }
    .dept-name {
        font-size: 22px;
        font-weight: bold;
        color: white;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    .division-name {
        font-size: 18px;
        font-weight: bold;
        color: #FFD700; /* Gold color for contrast */
        margin: 8px 0;
    }
    .school-name {
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin: 8px 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .header-subtext {
        font-size: 13px;
        color: #FFD700; /* Gold color */
        margin-top: 8px;
        font-style: italic;
        font-weight: bold;
    }
    
    /* App title styling */
    .app-title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        color: #800000; /* Maroon */
        margin: 15px 0 25px 0;
        padding: 10px;
        border-bottom: 3px solid #800000;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # DEBUG: Show files in directory
    debug_info = ""
    all_files = os.listdir('.')
    image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    # Display debug info in sidebar
    with st.sidebar.expander("📁 Debug - Files Found", expanded=False):
        st.write("All files in directory:", all_files)
        st.write("Image files found:", image_files)
    
    # Get DEPED logo
    deped_logo_base64 = None
    deped_filenames = [
        "deped logo.png", 
        "deped_logo.png", 
        "deped-logo.png",
        "deped_logo_uploaded.png"
    ]
    
    for filename in deped_filenames:
        deped_logo_base64 = get_image_base64(filename)
        if deped_logo_base64:
            st.sidebar.success(f"✓ Found DepEd logo: {filename}")
            break
    
    if not deped_logo_base64:
        # Try to find any file with 'deped' in the name
        for file in all_files:
            if 'deped' in file.lower():
                deped_logo_base64 = get_image_base64(file)
                if deped_logo_base64:
                    st.sidebar.success(f"✓ Found DepEd logo: {file}")
                    break
    
    # Get SCHOOL logo - LOOK FOR YOUR SPECIFIC FILENAME
    school_logo_base64 = None
    
    # First try the exact long filename
    long_filename = "393893242_355506113695594_2301660718121341125_n-removebg-preview.png"
    school_logo_base64 = get_image_base64(long_filename)
    
    if school_logo_base64:
        st.sidebar.success(f"✓ Found school logo: {long_filename}")
    else:
        # Try other possible school logo filenames
        school_filenames = [
            "school_logo.jpg", 
            "school_logo.png",
            "manual_nhs_logo.jpg",
            "manual_nhs_logo.png",
            "manual.jpg",
            "manual.png",
            "nhs_logo.jpg",
            "logo.jpg"
        ]
        
        for filename in school_filenames:
            school_logo_base64 = get_image_base64(filename)
            if school_logo_base64:
                st.sidebar.success(f"✓ Found school logo: {filename}")
                break
        
        # Last resort: look for any image with 'manual' or 'nhs' in name
        if not school_logo_base64:
            for file in all_files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')) and ('manual' in file.lower() or 'nhs' in file.lower()):
                    school_logo_base64 = get_image_base64(file)
                    if school_logo_base64:
                        st.sidebar.success(f"✓ Found school logo: {file}")
                        break
    
    # Create HTML for header
    header_html = """
    <div class="header-container">
        <div>
            {deped_logo}
        </div>
        <div class="center-content">
            <p class="dept-name">DEPARTMENT OF EDUCATION REGION XI</p>
            <p class="division-name">DIVISION OF DAVAO DEL SUR</p>
            <p class="school-name">MANUAL NATIONAL HIGH SCHOOL</p>
            <p class="header-subtext">Kiblawan North District</p>
        </div>
        <div>
            {school_logo}
        </div>
    </div>
    """
    
    # Determine logo display
    if deped_logo_base64:
        deped_display = f'<div class="logo-box"><img src="data:image/png;base64,{deped_logo_base64}" alt="DepEd Logo"></div>'
    else:
        deped_display = '<div class="logo-placeholder">DEPED<br>REGION XI</div>'
        st.sidebar.warning("⚠️ DepEd logo not found")
    
    if school_logo_base64:
        school_display = f'<div class="logo-box"><img src="data:image/png;base64,{school_logo_base64}" alt="School Logo"></div>'
    else:
        school_display = '<div class="logo-placeholder">MANUAL<br>NATIONAL<br>HIGH SCHOOL</div>'
        st.sidebar.warning("⚠️ School logo not found")
        st.sidebar.info("Please make sure your school logo file is named one of:")
        st.sidebar.write("- 393893242_355506113695594_2301660718121341125_n-removebg-preview.png")
        st.sidebar.write("- school_logo.jpg/png")
        st.sidebar.write("- manual_nhs_logo.jpg/png")
    
    # Display header
    st.markdown(header_html.format(
        deped_logo=deped_display,
        school_logo=school_display
    ), unsafe_allow_html=True)

# [REST OF YOUR CODE REMAINS THE SAME - paste all other functions here]
# Continue with the AI Generator, DOCX Creator, and Streamlit UI sections...
