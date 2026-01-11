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

# --- 3. IMAGE HANDLING FOR GITHUB ---
def get_image_base64(image_filename):
    """Get base64 encoded image or use placeholder"""
    try:
        if os.path.exists(image_filename):
            with open(image_filename, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
    except:
        pass
    return None

def add_custom_header():
    """Add custom header with logos"""
    
    st.markdown("""
    <style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0;
        border-bottom: 3px solid #003366;
        margin-bottom: 25px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .logo-box {
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        border: 2px solid #003366;
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
        background: #f0f0f0;
        border: 2px dashed #003366;
        border-radius: 8px;
        color: #666;
        font-size: 12px;
        text-align: center;
        padding: 5px;
    }
    .center-content {
        text-align: center;
        flex-grow: 1;
        padding: 0 20px;
    }
    .dept-name {
        font-size: 20px;
        font-weight: bold;
        color: #003366;
        margin: 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .division-name {
        font-size: 17px;
        font-weight: bold;
        color: #006600;
        margin: 5px 0;
    }
    .school-name {
        font-size: 22px;
        font-weight: bold;
        color: #990000;
        margin: 5px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .header-subtext {
        font-size: 12px;
        color: #666;
        margin-top: 5px;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Try to get logos (with different possible filenames)
    deped_logo_base64 = None
    school_logo_base64 = None
    
    # Try different possible filenames for DepEd logo
    deped_filenames = ["deped logo.png", "deped_logo.png", "deped-logo.png"]
    for filename in deped_filenames:
        if os.path.exists(filename):
            deped_logo_base64 = get_image_base64(filename)
            break
    
    # Try different possible filenames for school logo
    school_filenames = [
        "school_logo.jpg", 
        "school_logo.png",
        "manual_nhs_logo.jpg",
        "393893242_355506113695594_2301660718121341125_n.jpg"  # Original long name
    ]
    for filename in school_filenames:
        if os.path.exists(filename):
            school_logo_base64 = get_image_base64(filename)
            break
    
    # Create HTML
    header_html = """
    <div class="header-container">
        <div>
            {deped_logo}
        </div>
        <div class="center-content">
            <p class="dept-name">DEPARTMENT OF EDUCATION REGION XI</p>
            <p class="division-name">DIVISION OF DAVAO DEL SUR</p>
            <p class="school-name">MANUAL NATIONAL HIGH SCHOOL</p>
            <p class="header-subtext">Daily Lesson Plan Generator</p>
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
        deped_display = '<div class="logo-placeholder">DepEd<br>Region XI<br>Logo</div>'
    
    if school_logo_base64:
        school_display = f'<div class="logo-box"><img src="data:image/jpeg;base64,{school_logo_base64}" alt="School Logo"></div>'
    else:
        school_display = '<div class="logo-placeholder">Manual NHS<br>Logo</div>'
    
    st.markdown(header_html.format(
        deped_logo=deped_display,
        school_logo=school_display
    ), unsafe_allow_html=True)

# [REST OF YOUR CODE REMAINS THE SAME - AI GENERATOR, DOCX CREATOR, etc.]
# Just paste all the other functions from your original code here...
