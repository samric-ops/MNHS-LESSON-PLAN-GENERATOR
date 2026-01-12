import streamlit as st
import json
from datetime import date
import io
import os
import base64
import requests
import urllib.parse
import random
import re

# Import with error handling
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    st.warning("Google Generative AI not available. Using sample data.")

try:
    from docx import Document
    from docx.shared import Inches, Pt, Mm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except:
    DOCX_AVAILABLE = False
    st.warning("python-docx not available. Cannot generate Word documents.")

# --- CONFIGURATION ---
st.set_page_config(page_title="DLP Generator", layout="centered")

# --- API KEY ---
EMBEDDED_API_KEY = "AIza......"  # REPLACE WITH YOUR ACTUAL KEY

# --- FIXED LOGO DISPLAY ---
def get_image_base64(image_filename):
    """Get base64 encoded image"""
    try:
        if os.path.exists(image_filename):
            with open(image_filename, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except:
        pass
    return None

def find_logo_files():
    """Find logo files in directory"""
    files = os.listdir('.')
    deped_logo = None
    school_logo = None
    
    # Look for DepEd logo
    for file in files:
        file_lower = file.lower()
        if 'deped' in file_lower and file_lower.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            deped_logo = file
            break
    
    # Look for school logo - check multiple patterns
    school_patterns = ['manual', 'nhs', 'school', 'logo', '393893242']
    for file in files:
        file_lower = file.lower()
        if file_lower.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # Check if it's NOT deped logo
            if 'deped' not in file_lower:
                # Check for school patterns
                if any(pattern in file_lower for pattern in school_patterns):
                    school_logo = file
                    break
    
    # If school logo still not found, use any non-deped image
    if not school_logo:
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                if 'deped' not in file_lower:
                    school_logo = file
                    break
    
    return deped_logo, school_logo

def add_custom_header():
    """Add custom header with maroon background and BOTH logos"""
    
    # Find logos
    deped_file, school_file = find_logo_files()
    
    # Get base64 images
    deped_base64 = get_image_base64(deped_file) if deped_file else None
    school_base64 = get_image_base64(school_file) if school_file else None
    
    # Debug info in sidebar
    with st.sidebar.expander("🔍 Logo Debug Info"):
        st.write("Files in directory:", os.listdir('.'))
        st.write("DepEd logo found:", deped_file)
        st.write("School logo found:", school_file)
        st.write("DepEd base64:", "Yes" if deped_base64 else "No")
        st.write("School base64:", "Yes" if school_base64 else "No")
    
    st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        margin-bottom: 25px;
        background-color: #800000;
        border-radius: 10px;
        color: white;
    }}
    .logo-box {{
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        border: 2px solid white;
        border-radius: 8px;
        padding: 5px;
    }}
    .logo-box img {{
        max-width: 90px;
        max-height: 90px;
        object-fit: contain;
    }}
    .logo-placeholder {{
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
    }}
    .center-content {{
        text-align: center;
        flex-grow: 1;
        padding: 0 25px;
    }}
    .dept-name {{
        font-size: 22px;
        font-weight: bold;
        color: white;
        margin: 0;
    }}
    .division-name {{
        font-size: 18px;
        font-weight: bold;
        color: #FFD700;
        margin: 8px 0;
    }}
    .school-name {{
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin: 8px 0;
        text-transform: uppercase;
    }}
    .header-subtext {{
        font-size: 13px;
        color: #FFD700;
        margin-top: 8px;
        font-style: italic;
    }}
    .app-title {{
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        color: #800000;
        margin: 15px 0 25px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #800000;
    }}
    </style>
    
    <div class="header-container">
        <!-- LEFT: DepEd Logo -->
        <div>
            {"<div class='logo-box'><img src='data:image/png;base64," + deped_base64 + "'></div>" 
             if deped_base64 else 
             "<div class='logo-placeholder'>DEPED<br>LOGO</div>"}
        </div>
        
        <!-- CENTER: Text -->
        <div class="center-content">
            <p class="dept-name">DEPARTMENT OF EDUCATION REGION XI</p>
            <p class="division-name">DIVISION OF DAVAO DEL SUR</p>
            <p class="school-name">MANUAL NATIONAL HIGH SCHOOL</p>
            <p class="header-subtext">Kiblawan North District</p>
        </div>
        
        <!-- RIGHT: School Logo -->
        <div>
            {"<div class='logo-box'><img src='data:image/png;base64," + school_base64 + "'></div>" 
             if school_base64 else 
             "<div class='logo-placeholder'>MANUAL NHS<br>LOGO</div>"}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SAMPLE DATA FOR TESTING ---
def get_sample_lesson_data():
    return {
        "obj_1": "Identify the basic parts of a plant",
        "obj_2": "Draw and label the parts of a plant",
        "obj_3": "Appreciate the importance of plants in our environment",
        "topic": "Parts of a Plant",
        "integration_within": "Science - Photosynthesis",
        "integration_across": "Values Education - Environmental Care",
        "resources": {
            "guide": "Teacher's Guide pp. 45-50",
            "materials": "LM pp. 30-35",
            "textbook": "Science for Daily Use pp. 25-30",
            "portal": "DepEd Commons",
            "other": "Real plants, charts"
        },
        "procedure": {
            "review": "Review previous lesson on living things",
            "purpose_situation": "Show a wilted plant and ask why it's important to care for plants",
            "visual_prompt": "Green Plant Parts",
            "vocabulary": "Root: Anchors plant\nStem: Supports plant\nLeaf: Makes food\nFlower: Produces seeds",
            "activity_main": "Group activity: Identify plant parts",
            "explicitation": "Discuss functions of each plant part",
            "group_1": "Identify roots and stems",
            "group_2": "Identify leaves and flowers",
            "group_3": "Draw a complete plant",
            "generalization": "Why are plants important?"
        },
        "evaluation": {
            "assess_q1": "What part of the plant anchors it to the ground?",
            "assess_q2": "Which part makes food for the plant?",
            "assess_q3": "What is the function of the stem?",
            "assess_q4": "Which part produces seeds?",
            "assess_q5": "Name three things plants give us.",
            "assignment": "Draw and label a plant at home",
            "remarks": "90% of students met the objectives",
            "reflection": "Students were engaged in hands-on activities"
        }
    }

# --- AI GENERATOR ---
def generate_lesson_content(subject, grade, quarter, content_std, perf_std, competency, 
                           obj_cognitive=None, obj_psychomotor=None, obj_affective=None):
    if not GEMINI_AVAILABLE:
        return get_sample_lesson_data()
    
    try:
        genai.configure(api_key=EMBEDDED_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Create a detailed lesson plan for {subject}, {grade}, Quarter {quarter}.
        Content Standard: {content_std}
        Performance Standard: {perf_std}
        Learning Competency: {competency}
        
        {"Use these specific objectives:" if obj_cognitive and obj_psychomotor and obj_affective else "Generate appropriate objectives:"}
        {f"Cognitive: {obj_cognitive}" if obj_cognitive else ""}
        {f"Psychomotor: {obj_psychomotor}" if obj_psychomotor else ""}
        {f"Affective: {obj_affective}" if obj_affective else ""}
        
        Return as valid JSON with these exact keys:
        - obj_1 (cognitive objective)
        - obj_2 (psychomotor objective) 
        - obj_3 (affective objective)
        - topic
        - integration_within
        - integration_across
        - resources (object with: guide, materials, textbook, portal, other)
        - procedure (object with: review, purpose_situation, visual_prompt, vocabulary, activity_main, explicitation, group_1, group_2, group_3, generalization)
        - evaluation (object with: assess_q1, assess_q2, assess_q3, assess_q4, assess_q5, assignment, remarks, reflection)"""
        
        response = model.generate_content(prompt)
        text = response.text
        
        # Clean JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        return json.loads(text.strip())
        
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
        return get_sample_lesson_data()

# --- DOCX CREATOR ---
def create_docx(inputs, ai_data, teacher_name, principal_name):
    if not DOCX_AVAILABLE:
        return None
    
    try:
        doc = Document()
        
        # Header
        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title.add_run("DAILY LESSON PLAN\n")
        title_run.bold = True
        title_run.font.size = Pt(14)
        
        # School info
        info = doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        info.add_run("DEPARTMENT OF EDUCATION REGION XI\n")
        info.add_run("DIVISION OF DAVAO DEL SUR\n")
        info.add_run("MANUAL NATIONAL HIGH SCHOOL\n\n")
        
        # Basic info table
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        row = table.rows[0]
        row.cells[0].text = "Subject Area:\n" + inputs['subject']
        row.cells[1].text = "Grade Level:\n" + inputs['grade']
        row.cells[2].text = "Quarter:\n" + inputs['quarter']
        row.cells[3].text = "Date:\n" + date.today().strftime('%B %d, %Y')
        
        # Content
        doc.add_paragraph("\nI. OBJECTIVES:").runs[0].bold = True
        doc.add_paragraph(f"1. {ai_data.get('obj_1', '')}")
        doc.add_paragraph(f"2. {ai_data.get('obj_2', '')}")
        doc.add_paragraph(f"3. {ai_data.get('obj_3', '')}")
        
        doc.add_paragraph("\nII. CONTENT:").runs[0].bold = True
        doc.add_paragraph(f"A. Topic: {ai_data.get('topic', '')}")
        doc.add_paragraph(f"B. Integration Within: {ai_data.get('integration_within', '')}")
        doc.add_paragraph(f"C. Integration Across: {ai_data.get('integration_across', '')}")
        
        # Resources
        doc.add_paragraph("\nIII. LEARNING RESOURCES:").runs[0].bold = True
        resources = ai_data.get('resources', {})
        for key, value in resources.items():
            doc.add_paragraph(f"{key.title()}: {value}")
        
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
        
    except Exception as e:
        st.error(f"Document Error: {str(e)}")
        return None

# --- MAIN APP ---
def main():
    # Add header with BOTH logos
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
        
        # Logo uploaders
        uploaded_deped = st.file_uploader("Upload DepEd Logo", type=['png', 'jpg', 'jpeg'])
        uploaded_school = st.file_uploader("Upload School Logo", type=['png', 'jpg', 'jpeg'])
        
        if uploaded_deped:
            with open("uploaded_deped_logo.png", "wb") as f:
                f.write(uploaded_deped.getbuffer())
            st.success("DepEd logo uploaded!")
            
        if uploaded_school:
            with open("uploaded_school_logo.png", "wb") as f:
                f.write(uploaded_school.getbuffer())
            st.success("School logo uploaded!")
        
        st.markdown("---")
        if not GEMINI_AVAILABLE:
            st.error("⚠️ Google AI not installed")
        if not DOCX_AVAILABLE:
            st.warning("⚠️ Word document support limited")
    
    # Main form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        subject = st.text_input("Subject Area", placeholder="e.g., Mathematics")
    
    with col2:
        grade_options = [
            "Kinder", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
            "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"
        ]
        grade = st.selectbox("Grade Level", grade_options, index=5)  # Default Grade 6
    
    with col3:
        quarter_options = ["I", "II", "III", "IV"]
        quarter = st.selectbox("Quarter", quarter_options, index=2)  # Default Quarter III
    
    content_std = st.text_area("Content Standard", placeholder="The learner demonstrates understanding of...", height=100)
    perf_std = st.text_area("Performance Standard", placeholder="The learner is able to...", height=100)
    competency = st.text_area("Learning Competency", placeholder="Competency code and description...", height=100)
    
    # Optional objectives
    with st.expander("📝 Optional: Enter Lesson Objectives"):
        col_o1, col_o2, col_o3 = st.columns(3)
        with col_o1:
            obj_cognitive = st.text_area("Cognitive", placeholder="e.g., Identify parts of a cell", height=80)
        with col_o2:
            obj_psychomotor = st.text_area("Psychomotor", placeholder="e.g., Draw and label", height=80)
        with col_o3:
            obj_affective = st.text_area("Affective", placeholder="e.g., Appreciate importance", height=80)
    
    # Generate button
    if st.button("🚀 Generate DLP", type="primary", use_container_width=True):
        if not all([subject, grade, quarter, content_std, perf_std, competency]):
            st.error("❌ Please fill all required fields!")
            return
        
        with st.spinner("Generating lesson plan..."):
            ai_data = generate_lesson_content(
                subject, grade, quarter, content_std, perf_std, competency,
                obj_cognitive, obj_psychomotor, obj_affective
            )
        
        st.success("✅ Lesson plan generated!")
        
        # Show objectives
        st.subheader("📋 Generated Objectives")
        col1, col2, col3 = st.columns(3)
        col1.info(f"**Cognitive**\n\n{ai_data.get('obj_1', 'N/A')}")
        col2.info(f"**Psychomotor**\n\n{ai_data.get('obj_2', 'N/A')}")
        col3.info(f"**Affective**\n\n{ai_data.get('obj_3', 'N/A')}")
        
        # Preview
        with st.expander("📄 Preview Full Lesson Plan"):
            st.json(ai_data)
        
        # Create and download document
        docx_buffer = create_docx(
            {
                'subject': subject,
                'grade': grade,
                'quarter': quarter,
                'content_std': content_std,
                'perf_std': perf_std,
                'competency': competency
            },
            ai_data,
            teacher_name,
            principal_name
        )
        
        if docx_buffer:
            st.download_button(
                label="📥 Download DLP (.docx)",
                data=docx_buffer,
                file_name=f"DLP_{subject}_{grade}_Q{quarter}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        else:
            st.info("Word document not available. Here's your lesson plan:")
            st.text_area("Lesson Plan", 
                       f"""SUBJECT: {subject}
GRADE: {grade}
QUARTER: {quarter}

OBJECTIVES:
1. {ai_data.get('obj_1', '')}
2. {ai_data.get('obj_2', '')}
3. {ai_data.get('obj_3', '')}

TOPIC: {ai_data.get('topic', '')}

PROCEDURE:
{ai_data.get('procedure', {}).get('activity_main', '')}

ASSESSMENT:
1. {ai_data.get('evaluation', {}).get('assess_q1', '')}
2. {ai_data.get('evaluation', {}).get('assess_q2', '')}
3. {ai_data.get('evaluation', {}).get('assess_q3', '')}""",
                       height=300)
        
        st.balloons()

# Run app
if __name__ == "__main__":
    main()
