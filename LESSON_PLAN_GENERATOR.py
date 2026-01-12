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

# --- 3. FIXED IMAGE HANDLING ---
def get_image_base64(image_filename):
    """Get base64 encoded image or use placeholder"""
    try:
        if os.path.exists(image_filename):
            with open(image_filename, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        return None
    except:
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
        background-color: #800000;
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
        color: #FFD700;
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
        color: #FFD700;
        margin-top: 8px;
        font-style: italic;
        font-weight: bold;
    }
    .app-title {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        color: #800000;
        margin: 15px 0 25px 0;
        padding: 10px;
        border-bottom: 3px solid #800000;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get current directory files
    current_dir = os.listdir('.')
    
    # Find logos
    deped_logo_base64 = None
    school_logo_base64 = None
    
    # Look for DepEd logo
    for file in current_dir:
        if 'deped' in file.lower() and file.lower().endswith(('.png', '.jpg', '.jpeg')):
            deped_logo_base64 = get_image_base64(file)
            break
    
    # Look for school logo - check multiple patterns
    school_patterns = ['manual', 'nhs', 'school', 'logo', '393893242']
    for file in current_dir:
        file_lower = file.lower()
        if file_lower.endswith(('.png', '.jpg', '.jpeg')):
            if any(pattern in file_lower for pattern in school_patterns):
                school_logo_base64 = get_image_base64(file)
                break
    
    # If still no school logo, use first image that's not deped
    if not school_logo_base64:
        for file in current_dir:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')) and 'deped' not in file.lower():
                school_logo_base64 = get_image_base64(file)
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
        deped_display = f'<div class="logo-box"><img src="data:image/png;base64,{deped_logo_base64}"></div>'
    else:
        deped_display = '<div class="logo-placeholder">DEPED<br>REGION XI</div>'
    
    if school_logo_base64:
        school_display = f'<div class="logo-box"><img src="data:image/png;base64,{school_logo_base64}"></div>'
    else:
        school_display = '<div class="logo-placeholder">MANUAL<br>NATIONAL<br>HIGH SCHOOL</div>'
    
    # Display header
    st.markdown(header_html.format(
        deped_logo=deped_display,
        school_logo=school_display
    ), unsafe_allow_html=True)

# --- 4. AI GENERATOR ---
def generate_lesson_content(subject, grade, quarter, content_std, perf_std, competency, 
                           obj_cognitive=None, obj_psychomotor=None, obj_affective=None):
    try:
        genai.configure(api_key=EMBEDDED_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        if obj_cognitive and obj_psychomotor and obj_affective:
            prompt = f"""Create a lesson plan for {subject}, Grade {grade}, Quarter {quarter}.
            Content Standard: {content_std}
            Performance Standard: {perf_std}
            Learning Competency: {competency}
            
            Use these objectives:
            Cognitive: {obj_cognitive}
            Psychomotor: {obj_psychomotor}
            Affective: {obj_affective}
            
            Return JSON with: topic, integration_within, integration_across, resources (guide, materials, textbook, portal, other), 
            procedure (review, purpose_situation, visual_prompt, vocabulary, activity_main, explicitation, group_1, group_2, group_3, generalization),
            evaluation (assess_q1, assess_q2, assess_q3, assess_q4, assess_q5, assignment, remarks, reflection)"""
        else:
            prompt = f"""Create a lesson plan for {subject}, Grade {grade}, Quarter {quarter}.
            Content Standard: {content_std}
            Performance Standard: {perf_std}
            Learning Competency: {competency}
            
            Generate appropriate objectives and return JSON with: 
            obj_1 (cognitive), obj_2 (psychomotor), obj_3 (affective),
            topic, integration_within, integration_across, resources (guide, materials, textbook, portal, other), 
            procedure (review, purpose_situation, visual_prompt, vocabulary, activity_main, explicitation, group_1, group_2, group_3, generalization),
            evaluation (assess_q1, assess_q2, assess_q3, assess_q4, assess_q5, assignment, remarks, reflection)"""
        
        response = model.generate_content(prompt)
        text = response.text
        
        # Clean JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        return json.loads(text.strip())
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# --- 5. IMAGE FETCHER ---
def fetch_ai_image(keywords):
    if not keywords: 
        keywords = "classroom"
    clean_prompt = re.sub(r'[^\w\s]', '', keywords)
    encoded_prompt = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=600&height=400"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except:
        return None
    return None

# --- 6. DOCX CREATION FUNCTIONS ---
def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def format_text(paragraph, text):
    if not text:
        return
    paragraph.add_run(str(text))

def add_row(table, label, content, bold_label=True):
    row_cells = table.add_row().cells
    label_cell = row_cells[0].paragraphs[0]
    label_cell.add_run(label).bold = bold_label
    
    if isinstance(content, list):
        content_text = "\n".join([str(item) for item in content])
    else:
        content_text = str(content)
    
    format_text(row_cells[1].paragraphs[0], content_text)

def add_section_header(table, text):
    row = table.add_row()
    row.cells[0].merge(row.cells[1])
    cell = row.cells[0]
    cell.text = text
    cell.paragraphs[0].runs[0].bold = True
    set_cell_background(cell, "BDD7EE")

def create_docx(inputs, ai_data, teacher_name, principal_name, uploaded_image):
    doc = Document()
    
    # Page setup
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    
    # Header
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header.add_run("DEPARTMENT OF EDUCATION REGION XI\n").bold = True
    header.add_run("DIVISION OF DAVAO DEL SUR\n").bold = True
    header.add_run("MANUAL NATIONAL HIGH SCHOOL\n\n").bold = True
    header.add_run("Daily Lesson Plan (DLP) Generator\n").bold = True
    
    # Info table
    table_top = doc.add_table(rows=1, cols=4)
    table_top.style = 'Table Grid'
    row = table_top.rows[0]
    row.cells[0].text = "Subject Area:\n" + inputs['subject']
    row.cells[1].text = "Grade Level:\n" + inputs['grade']
    row.cells[2].text = "Quarter:\n" + inputs['quarter']
    row.cells[3].text = "Date:\n" + date.today().strftime('%B %d, %Y')
    
    # Main table
    table = doc.add_table(rows=0, cols=2)
    table.style = 'Table Grid'
    
    # Section I
    add_section_header(table, "I. CURRICULUM CONTENT, STANDARD AND LESSON COMPETENCIES")
    add_row(table, "A. Content Standard", inputs['content_std'])
    add_row(table, "B. Performance Standard", inputs['perf_std'])
    add_row(table, "C. Learning Competencies", inputs['competency'])
    
    objs = f"1. {ai_data.get('obj_1', '')}\n2. {ai_data.get('obj_2', '')}\n3. {ai_data.get('obj_3', '')}"
    add_row(table, "D. Objectives", objs)
    add_row(table, "E. Content", ai_data.get('topic', ''))
    
    # Section II
    add_section_header(table, "II. LEARNING RESOURCES")
    resources = ai_data.get('resources', {})
    add_row(table, "Teacher Guide", resources.get('guide', ''))
    add_row(table, "Learner's Materials", resources.get('materials', ''))
    add_row(table, "Textbooks", resources.get('textbook', ''))
    add_row(table, "LR Portal", resources.get('portal', ''))
    add_row(table, "Other Resources", resources.get('other', ''))
    
    # Section III
    add_section_header(table, "III. TEACHING AND LEARNING PROCEDURE")
    proc = ai_data.get('procedure', {})
    add_row(table, "A. Review", proc.get('review', ''))
    add_row(table, "B. Motivation", proc.get('purpose_situation', ''))
    
    # Section IV
    add_section_header(table, "IV. EVALUATING LEARNING")
    eval_sec = ai_data.get('evaluation', {})
    add_row(table, "Assessment", "\n".join([f"{i}. {eval_sec.get(f'assess_q{i}', '')}" for i in range(1, 6)]))
    add_row(table, "Assignment", eval_sec.get('assignment', ''))
    add_row(table, "Remarks", eval_sec.get('remarks', ''))
    
    # Signatures
    doc.add_paragraph("\n\n")
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.rows[0].cells[0].text = f"Prepared by:\n\n{teacher_name}\nTeacher III"
    sig_table.rows[0].cells[1].text = f"Noted by:\n\n{principal_name}\nPrincipal III"
    
    # Save
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 7. MAIN APP ---
def main():
    # Add header
    add_custom_header()
    
    # App title
    st.markdown('<p class="app-title">Daily Lesson Plan (DLP) Generator</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 User Information")
        teacher_name = st.text_input("Teacher Name", value="RICHARD P. SAMORANOS")
        principal_name = st.text_input("Principal Name", value="ROSALITA A. ESTROPIA")
        
        st.markdown("---")
        st.subheader("🏫 Upload Logos")
        uploaded_deped = st.file_uploader("DepEd Logo", type=['png', 'jpg', 'jpeg'])
        uploaded_school = st.file_uploader("School Logo", type=['png', 'jpg', 'jpeg'])
        uploaded_image = st.file_uploader("Lesson Image", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_deped:
            with open("deped_logo_temp.png", "wb") as f:
                f.write(uploaded_deped.getbuffer())
        
        if uploaded_school:
            with open("school_logo_temp.png", "wb") as f:
                f.write(uploaded_school.getbuffer())
        
        st.markdown("---")
        st.info("API Key is configured")
    
    # Main form
    col1, col2, col3 = st.columns(3)
    with col1:
        subject = st.text_input("Subject Area", placeholder="Mathematics")
    with col2:
        grade_options = ["Kinder", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
                        "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"]
        grade = st.selectbox("Grade Level", grade_options, index=6)
    with col3:
        quarter = st.selectbox("Quarter", ["I", "II", "III", "IV"], index=2)
    
    content_std = st.text_area("Content Standard", placeholder="The learner demonstrates understanding of...")
    perf_std = st.text_area("Performance Standard", placeholder="The learner is able to...")
    competency = st.text_area("Learning Competency", placeholder="Competency code and description...")
    
    # Optional objectives
    with st.expander("📝 Optional: Enter Lesson Objectives"):
        col_o1, col_o2, col_o3 = st.columns(3)
        with col_o1:
            obj_cognitive = st.text_area("Cognitive", height=80)
        with col_o2:
            obj_psychomotor = st.text_area("Psychomotor", height=80)
        with col_o3:
            obj_affective = st.text_area("Affective", height=80)
    
    # Generate button
    if st.button("🚀 Generate DLP", type="primary", use_container_width=True):
        if not all([subject, grade, quarter, content_std, perf_std, competency]):
            st.error("Please fill all required fields!")
            return
        
        with st.spinner("Generating lesson plan..."):
            ai_data = generate_lesson_content(
                subject, grade, quarter, content_std, perf_std, competency,
                obj_cognitive, obj_psychomotor, obj_affective
            )
        
        if ai_data:
            st.success("✅ Lesson plan generated!")
            
            # Show preview
            with st.expander("Preview Objectives"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Cognitive", ai_data.get('obj_1', 'N/A'))
                col2.metric("Psychomotor", ai_data.get('obj_2', 'N/A'))
                col3.metric("Affective", ai_data.get('obj_3', 'N/A'))
            
            # Create document
            inputs = {
                'subject': subject,
                'grade': grade,
                'quarter': quarter,
                'content_std': content_std,
                'perf_std': perf_std,
                'competency': competency
            }
            
            docx_buffer = create_docx(inputs, ai_data, teacher_name, principal_name, uploaded_image)
            
            # Download button
            st.download_button(
                label="📥 Download DLP (.docx)",
                data=docx_buffer,
                file_name=f"DLP_{subject}_{grade}_Q{quarter}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            st.balloons()

# Run the app
if __name__ == "__main__":
    main()
