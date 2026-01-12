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
from PIL import Image

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

# --- 3. FIXED IMAGE HANDLING WITH DEBUGGING ---
def get_image_base64(image_filename):
    """Get base64 encoded image or use placeholder"""
    try:
        if os.path.exists(image_filename):
            with open(image_filename, "rb") as img_file:
                # Check if image is valid
                try:
                    img = Image.open(img_file)
                    img.verify()  # Verify it's a valid image
                    img_file.seek(0)  # Reset file pointer
                    return base64.b64encode(img_file.read()).decode('utf-8')
                except:
                    st.sidebar.warning(f"Invalid image file: {image_filename}")
                    return None
        else:
            return None
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
    
    # DEBUG: First, let's check what files are in the directory
    with st.sidebar.expander("🔍 Debug File Search", expanded=True):
        st.write("### Looking for logo files...")
        
        # List all files
        all_files = os.listdir('.')
        st.write(f"**Total files in directory:** {len(all_files)}")
        
        # Show all image files
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        image_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in image_extensions)]
        
        st.write("**Image files found:**")
        for img_file in image_files:
            st.write(f"- {img_file}")
        
        # Check for specific patterns
        st.write("**Files containing 'manual' or 'nhs':**")
        for file in all_files:
            if 'manual' in file.lower() or 'nhs' in file.lower():
                st.write(f"- {file}")
    
    # Try to get logos
    deped_logo_base64 = None
    school_logo_base64 = None
    
    # 1. FIRST: Check for uploaded files
    uploaded_files = {
        "deped": "deped_logo_uploaded.png",
        "school": "school_logo_uploaded.jpg"
    }
    
    # Check uploaded school logo first
    if os.path.exists(uploaded_files["school"]):
        school_logo_base64 = get_image_base64(uploaded_files["school"])
        if school_logo_base64:
            st.sidebar.success("✓ Using uploaded school logo")
    
    # Check uploaded DepEd logo
    if os.path.exists(uploaded_files["deped"]):
        deped_logo_base64 = get_image_base64(uploaded_files["deped"])
        if deped_logo_base64:
            st.sidebar.success("✓ Using uploaded DepEd logo")
    
    # 2. SECOND: If no uploaded files, try to find original files
    if not school_logo_base64:
        # Search for school logo with various patterns
        school_patterns = [
            "manual", "nhs", "school", "logo", 
            "393893242", "removebg", "preview"
        ]
        
        for file in all_files:
            if any(pattern in file.lower() for pattern in school_patterns):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    school_logo_base64 = get_image_base64(file)
                    if school_logo_base64:
                        st.sidebar.success(f"✓ Found school logo: {file}")
                        break
        
        # If still not found, try any image file
        if not school_logo_base64 and image_files:
            for img_file in image_files:
                # Skip deped logo files
                if 'deped' not in img_file.lower():
                    school_logo_base64 = get_image_base64(img_file)
                    if school_logo_base64:
                        st.sidebar.success(f"✓ Using image as school logo: {img_file}")
                        break
    
    if not deped_logo_base64:
        # Search for DepEd logo
        deped_patterns = ["deped", "logo"]
        for file in all_files:
            if any(pattern in file.lower() for pattern in deped_patterns):
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    deped_logo_base64 = get_image_base64(file)
                    if deped_logo_base64:
                        st.sidebar.success(f"✓ Found DepEd logo: {file}")
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
    
    # Determine logo display with proper MIME types
    if deped_logo_base64:
        # Try to determine MIME type
        deped_display = f'<div class="logo-box"><img src="data:image/png;base64,{deped_logo_base64}" alt="DepEd Logo"></div>'
    else:
        deped_display = '<div class="logo-placeholder">DEPED<br>REGION XI</div>'
    
    if school_logo_base64:
        # Try to determine MIME type for school logo
        school_display = f'<div class="logo-box"><img src="data:image/png;base64,{school_logo_base64}" alt="School Logo"></div>'
    else:
        school_display = '<div class="logo-placeholder">MANUAL<br>NATIONAL<br>HIGH SCHOOL</div>'
    
    # Display header
    st.markdown(header_html.format(
        deped_logo=deped_display,
        school_logo=school_display
    ), unsafe_allow_html=True)

# --- REST OF THE CODE CONTINUES THE SAME ---
# [Keep all the other functions exactly as they were: AI Generator, Image Fetcher, DOCX Helpers, etc.]
# Just replace the add_custom_header() function with the one above
