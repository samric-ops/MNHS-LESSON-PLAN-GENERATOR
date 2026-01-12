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

# --- HEADER WITH LOGOS ---
def add_custom_header():
    """Add custom header with maroon background"""
    
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
        color: white;
        text-align: center;
    }
    .logo-box {
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        border-radius: 8px;
        padding: 5px;
    }
    .center-content {
        flex-grow: 1;
        padding: 0 20px;
    }
    .dept-name {
        font-size: 20px;
        font-weight: bold;
        color: white;
        margin: 0;
    }
    .division-name {
        font-size: 16px;
        font-weight: bold;
        color: #FFD700;
        margin: 5px 0;
    }
    .school-name {
        font-size: 22px;
        font-weight: bold;
        color: white;
        margin: 5px 0;
        text-transform: uppercase;
    }
    .app-title {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        color: #800000;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create header
    header_html = """
    <div class="header-container">
        <div class="logo-box">
            <div style="color: #800000; font-size: 12px; text-align: center;">
                DEPED<br>LOGO
            </div>
        </div>
        <div class="center-content">
            <p class="dept-name">DEPARTMENT OF EDUCATION REGION XI</p>
            <p class="division-name">DIVISION OF DAVAO DEL SUR</p>
            <p class="school-name">MANUAL NATIONAL HIGH SCHOOL</p>
        </div>
        <div class="logo-box">
            <div style="color: #800000; font-size: 12px; text-align: center;">
                SCHOOL<br>LOGO
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

# --- SAMPLE DATA FOR TESTING ---
def get_sample_lesson_data():
    """Return sample data for testing"""
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

# --- MAIN APP ---
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
        
        if not GEMINI_AVAILABLE:
            st.error("⚠️ Google AI not installed. Using sample data.")
        if not DOCX_AVAILABLE:
            st.error("⚠️ Word document support not available.")
        
        st.info("Fill in the form and click Generate DLP")
    
    # Main form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        subject = st.text_input("Subject Area", placeholder="e.g., Science")
    
    with col2:
        grade_options = [
            "Kinder", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
            "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"
        ]
        grade = st.selectbox("Grade Level", grade_options, index=6)
    
    with col3:
        quarter_options = ["I", "II", "III", "IV"]
        quarter = st.selectbox("Quarter", quarter_options, index=2)
    
    content_std = st.text_area("Content Standard", placeholder="The learner demonstrates understanding of...", height=100)
    perf_std = st.text_area("Performance Standard", placeholder="The learner is able to...", height=100)
    competency = st.text_area("Learning Competency", placeholder="Competency code and description...", height=100)
    
    # Optional objectives
    with st.expander("📝 Optional: Enter Lesson Objectives (Leave blank for AI to generate)"):
        col_o1, col_o2, col_o3 = st.columns(3)
        with col_o1:
            obj_cognitive = st.text_area("Cognitive Objective", placeholder="What students should know", height=80)
        with col_o2:
            obj_psychomotor = st.text_area("Psychomotor Objective", placeholder="What students should be able to do", height=80)
        with col_o3:
            obj_affective = st.text_area("Affective Objective", placeholder="Values/attitudes to develop", height=80)
    
    # Generate button
    if st.button("🚀 Generate DLP", type="primary", use_container_width=True):
        if not all([subject, grade, quarter, content_std, perf_std, competency]):
            st.error("❌ Please fill all required fields!")
            return
        
        with st.spinner("Generating lesson plan..."):
            if GEMINI_AVAILABLE:
                try:
                    genai.configure(api_key=EMBEDDED_API_KEY)
                    model = genai.GenerativeModel('gemini-pro')
                    
                    prompt = f"""Create a lesson plan for {subject}, {grade}, Quarter {quarter}.
                    Content: {content_std}
                    Performance: {perf_std}
                    Competency: {competency}
                    
                    Return as JSON with these keys: obj_1, obj_2, obj_3, topic, integration_within, 
                    integration_across, resources (as dict with guide, materials, textbook, portal, other),
                    procedure (as dict with review, purpose_situation, visual_prompt, vocabulary, 
                    activity_main, explicitation, group_1, group_2, group_3, generalization),
                    evaluation (as dict with assess_q1, assess_q2, assess_q3, assess_q4, assess_q5, 
                    assignment, remarks, reflection)"""
                    
                    response = model.generate_content(prompt)
                    text = response.text
                    
                    # Extract JSON
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0]
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0]
                    
                    ai_data = json.loads(text.strip())
                    st.success("✅ AI-generated lesson plan created!")
                    
                except Exception as e:
                    st.warning(f"Using sample data. AI error: {str(e)}")
                    ai_data = get_sample_lesson_data()
            else:
                ai_data = get_sample_lesson_data()
                st.info("📋 Using sample lesson plan data")
        
        # Show results
        st.subheader("📋 Generated Objectives")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**Cognitive**")
            st.write(ai_data.get('obj_1', 'N/A'))
        with col2:
            st.info("**Psychomotor**")
            st.write(ai_data.get('obj_2', 'N/A'))
        with col3:
            st.info("**Affective**")
            st.write(ai_data.get('obj_3', 'N/A'))
        
        # Preview
        with st.expander("📄 Preview Full Lesson Plan"):
            st.json(ai_data)
        
        # Create Word document if possible
        if DOCX_AVAILABLE:
            try:
                # Create simple document
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
                info.add_run("Manual National High School\n")
                info.add_run("Division of Davao Del Sur\n")
                info.add_run("Department of Education Region XI\n\n")
                
                # Basic info
                doc.add_paragraph(f"Subject: {subject}")
                doc.add_paragraph(f"Grade: {grade}")
                doc.add_paragraph(f"Quarter: {quarter}")
                doc.add_paragraph(f"Date: {date.today().strftime('%B %d, %Y')}")
                
                # Objectives
                doc.add_paragraph("\nOBJECTIVES:").runs[0].bold = True
                doc.add_paragraph(f"1. {ai_data.get('obj_1', '')}")
                doc.add_paragraph(f"2. {ai_data.get('obj_2', '')}")
                doc.add_paragraph(f"3. {ai_data.get('obj_3', '')}")
                
                # Topic
                doc.add_paragraph(f"\nTOPIC: {ai_data.get('topic', '')}")
                
                # Save to buffer
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                
                # Download button
                st.download_button(
                    label="📥 Download DLP (.docx)",
                    data=buffer,
                    file_name=f"DLP_{subject}_{grade}_Q{quarter}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error creating document: {str(e)}")
                # Show data as text
                st.text_area("Lesson Plan Text", 
                           f"""SUBJECT: {subject}
GRADE: {grade}
QUARTER: {quarter}

OBJECTIVES:
1. {ai_data.get('obj_1', '')}
2. {ai_data.get('obj_2', '')}
3. {ai_data.get('obj_3', '')}

TOPIC: {ai_data.get('topic', '')}

RESOURCES: {ai_data.get('resources', {})}

PROCEDURE: {ai_data.get('procedure', {})}""",
                           height=300)
        else:
            # Show data as text
            st.text_area("Lesson Plan", 
                       f"""SUBJECT: {subject}
GRADE: {grade}
QUARTER: {quarter}

OBJECTIVES:
1. {ai_data.get('obj_1', '')}
2. {ai_data.get('obj_2', '')}
3. {ai_data.get('obj_3', '')}

TOPIC: {ai_data.get('topic', '')}""",
                       height=200)
        
        st.balloons()
        st.success(f"✅ DLP ready for {subject} - {grade} - Quarter {quarter}")

# Run app
if __name__ == "__main__":
    main()
