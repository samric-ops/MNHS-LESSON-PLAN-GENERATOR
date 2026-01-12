import streamlit as st
import google.generativeai as genai
import json
from datetime import date
import io
import requests
import urllib.parse
import random
import re

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
EMBEDDED_API_KEY = "AIzaSyCjBusA4G4RdMOYLQUN__3YD77DrcbqZjA"  # REPLACE WITH YOUR ACTUAL KEY

# --- 3. SIMPLIFIED HEADER WITHOUT LOGOS ---
def add_custom_header():
    """Add custom header with maroon background (NO LOGOS)"""
    
    st.markdown("""
    <style>
    .header-container {
        text-align: center;
        padding: 20px;
        margin-bottom: 25px;
        background-color: #800000; /* MAROON BACKGROUND */
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(128, 0, 0, 0.3);
        color: white;
    }
    .dept-name {
        font-size: 24px;
        font-weight: bold;
        color: white;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    .division-name {
        font-size: 20px;
        font-weight: bold;
        color: #FFD700; /* Gold color for contrast */
        margin: 8px 0;
    }
    .school-name {
        font-size: 28px;
        font-weight: bold;
        color: white;
        margin: 8px 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .header-subtext {
        font-size: 15px;
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
    
    <div class="header-container">
        <p class="dept-name">DEPARTMENT OF EDUCATION REGION XI</p>
        <p class="division-name">DIVISION OF DAVAO DEL SUR</p>
        <p class="school-name">MANUAL NATIONAL HIGH SCHOOL</p>
        <p class="header-subtext">Kiblawan North District</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. AI GENERATOR ---
def generate_lesson_content(subject, grade, quarter, content_std, perf_std, competency, 
                           obj_cognitive=None, obj_psychomotor=None, obj_affective=None):
    try:
        # Use the embedded API key
        genai.configure(api_key=EMBEDDED_API_KEY)
        
        # Try multiple model options
        model_options = ['gemini-2.5-flash']
        model = None
        
        for model_name in model_options:
            try:
                model = genai.GenerativeModel(model_name)
                # Test with a simple prompt
                test_response = model.generate_content("Hello")
                if test_response:
                    st.sidebar.success(f"✓ Using model: {model_name}")
                    break
            except Exception as e:
                continue
        
        if not model:
            # Fallback to default
            model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Check if user provided objectives
        user_provided_objectives = obj_cognitive and obj_psychomotor and obj_affective
        
        if user_provided_objectives:
            # Use user-provided objectives in the prompt
            prompt = f"""
            You are an expert teacher from Manual National High School in the Division of Davao Del Sur, Region XI, Philippines.
            Create a JSON object for a Daily Lesson Plan (DLP).
            Subject: {subject}, Grade: {grade}, Quarter: {quarter}
            Content Standard: {content_std}
            Performance Standard: {perf_std}
            Learning Competency: {competency}

            USER-PROVIDED OBJECTIVES:
            - Cognitive: {obj_cognitive}
            - Psychomotor: {obj_psychomotor}
            - Affective: {obj_affective}

            IMPORTANT: Use these exact objectives provided by the user. Do NOT modify them.
            
            CRITICAL INSTRUCTION: You MUST generate exactly 5 distinct assessment questions.

            Return ONLY raw JSON. No markdown formatting.
            Structure:
            {{
                "obj_1": "{obj_cognitive}",
                "obj_2": "{obj_psychomotor}",
                "obj_3": "{obj_affective}",
                "topic": "The main topic (include math equations like 3x^2 if needed)",
                "integration_within": "Topic within same subject",
                "integration_across": "Topic across other subject",
                "resources": {{
                    "guide": "Teacher Guide reference",
                    "materials": "Learner Materials reference",
                    "textbook": "Textbook reference",
                    "portal": "Learning Resource Portal reference",
                    "other": "Other Learning Resources"
                }},
                "procedure": {{
                    "review": "Review activity",
                    "purpose_situation": "Real-life situation motivation description",
                    "visual_prompt": "A simple 3-word visual description. Example: 'Red Apple Fruit'. NO sentences.",
                    "vocabulary": "5 terms with definitions",
                    "activity_main": "Main activity description",
                    "explicitation": "Discussion details",
                    "group_1": "Group 1 task",
                    "group_2": "Group 2 task",
                    "group_3": "Group 3 task",
                    "generalization": "Reflection questions"
                }},
                "evaluation": {{
                    "assess_q1": "First quiz question (clear, measurable question)",
                    "assess_q2": "Second quiz question",
                    "assess_q3": "Third quiz question",
                    "assess_q4": "Fourth quiz question",
                    "assess_q5": "Fifth quiz question",
                    "assignment": "Assignment task",
                    "remarks": "Remarks",
                    "reflection": "Reflection"
                }}
            }}
            """
        else:
            # Generate objectives automatically
            prompt = f"""
            You are an expert teacher from Manual National High School in the Division of Davao Del Sur, Region XI, Philippines.
            Create a JSON object for a Daily Lesson Plan (DLP).
            Subject: {subject}, Grade: {grade}, Quarter: {quarter}
            Content Standard: {content_std}
            Performance Standard: {perf_std}
            Learning Competency: {competency}

            CRITICAL INSTRUCTION: You MUST generate exactly 5 distinct assessment questions.

            Return ONLY raw JSON. No markdown formatting.
            Structure:
            {{
                "obj_1": "Cognitive objective",
                "obj_2": "Psychomotor objective",
                "obj_3": "Affective objective",
                "topic": "The main topic (include math equations like 3x^2 if needed)",
                "integration_within": "Topic within same subject",
                "integration_across": "Topic across other subject",
                "resources": {{
                    "guide": "Teacher Guide reference",
                    "materials": "Learner Materials reference",
                    "textbook": "Textbook reference",
                    "portal": "Learning Resource Portal reference",
                    "other": "Other Learning Resources"
                }},
                "procedure": {{
                    "review": "Review activity",
                    "purpose_situation": "Real-life situation motivation description",
                    "visual_prompt": "A simple 3-word visual description. Example: 'Red Apple Fruit'. NO sentences.",
                    "vocabulary": "5 terms with definitions",
                    "activity_main": "Main activity description",
                    "explicitation": "Discussion details",
                    "group_1": "Group 1 task",
                    "group_2": "Group 2 task",
                    "group_3": "Group 3 task",
                    "generalization": "Reflection questions"
                }},
                "evaluation": {{
                    "assess_q1": "First quiz question (clear, measurable question)",
                    "assess_q2": "Second quiz question",
                    "assess_q3": "Third quiz question",
                    "assess_q4": "Fourth quiz question",
                    "assess_q5": "Fifth quiz question",
                    "assignment": "Assignment task",
                    "remarks": "Remarks",
                    "reflection": "Reflection"
                }}
            }}
            """
        
        response = model.generate_content(prompt)
        text = response.text
        # Clean potential markdown
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "")
        elif "```" in text:
            text = text.split("```")[1]
        
        # Additional cleaning
        text = text.strip()
        
        return json.loads(text)
        
    except json.JSONDecodeError as je:
        st.error(f"JSON Parsing Error: {je}")
        st.code(f"Raw response: {text[:500]}...", language="text")
        return None
    except Exception as e:
        st.error(f"AI Generation Error: {str(e)}")
        return None

# --- 5. IMAGE FETCHER ---
def fetch_ai_image(keywords):
    if not keywords: keywords = "school_classroom"
    clean_prompt = re.sub(r'[\n\r\t]', ' ', str(keywords))
    clean_prompt = re.sub(r'[^a-zA-Z0-9 ]', '', clean_prompt).strip()
    
    encoded_prompt = urllib.parse.quote(clean_prompt)
    seed = random.randint(1, 9999)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=600&height=350&nologo=true&seed={seed}"
    url = url.strip()
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except Exception:
        return None
    return None

# --- 6. DOCX HELPERS ---
def set_cell_background(cell, color_hex):
    """Sets the background color of a table cell."""
    shading_elm = parse_xml(r'<w:shd {} w:fill="{}"/>'.format(nsdecls('w'), color_hex))
    cell._tc.get_or_add_tcPr().append(shading_elm)

def format_text(paragraph, text):
    """
    Parses text for ^ (superscript) and _ (subscript).
    """
    if not text:
        return

    pattern = r"([^\^_]*)(([\^_])([0-9a-zA-Z\-]+))(.*)"
    current_text = str(text)
    
    if "^" not in current_text and "_" not in current_text:
        paragraph.add_run(current_text)
        return

    while True:
        match = re.match(pattern, current_text)
        if match:
            pre_text = match.group(1)
            marker = match.group(3)
            script_text = match.group(4)
            rest = match.group(5)
            
            if pre_text:
                paragraph.add_run(pre_text)
            
            run = paragraph.add_run(script_text)
            if marker == '^':
                run.font.superscript = True
            elif marker == '_':
                run.font.subscript = True
                
            current_text = rest
            if not current_text:
                break
        else:
            paragraph.add_run(current_text)
            break

def add_row(table, label, content, bold_label=True):
    """Adds a row and applies formatting to the content."""
    row_cells = table.add_row().cells
    
    # Label Column (Left)
    p_lbl = row_cells[0].paragraphs[0]
    run_lbl = p_lbl.add_run(label)
    if bold_label:
        run_lbl.bold = True
    
    # Content Column (Right)
    text_content = ""
    
    if isinstance(content, list):
        # Join list items with newlines for vertical stacking
        text_content = "\n".join([str(item) for item in content])
    else:
        text_content = str(content) if content else ""
    
    format_text(row_cells[1].paragraphs[0], text_content)

def add_section_header(table, text):
    """Adds a full-width section header with Blue background."""
    row = table.add_row()
    row.cells[0].merge(row.cells[1])
    cell = row.cells[0]
    cell.text = text
    cell.paragraphs[0].runs[0].bold = True
    set_cell_background(cell, "BDD7EE")

def add_assessment_row(table, label, eval_sec):
    """Special function to add assessment row with proper formatting."""
    row_cells = table.add_row().cells
    
    # Label Column (Left)
    p_lbl = row_cells[0].paragraphs[0]
    run_lbl = p_lbl.add_run(label)
    run_lbl.bold = True
    
    # Content Column (Right) - Build from scratch
    content_cell = row_cells[1]
    
    # Clear cell by removing all existing paragraphs
    for paragraph in content_cell.paragraphs:
        p = paragraph._element
        p.getparent().remove(p)
    
    # Create new content
    # 1. Header
    p_header = content_cell.add_paragraph()
    header_run = p_header.add_run("ASSESSMENT (5-item Quiz)")
    header_run.bold = True
    
    # 2. Directions
    p_dir = content_cell.add_paragraph()
    p_dir.add_run("DIRECTIONS: Read each question carefully. Choose and write the correct answer.")
    
    # 3. Empty line for spacing
    content_cell.add_paragraph()
    
    # 4. Questions
    for i in range(1, 6):
        question_key = f'assess_q{i}'
        raw_question = eval_sec.get(question_key, f'Question {i}')
        
        # Clean question text
        clean_q = str(raw_question).strip()
        
        # Remove any existing numbering patterns
        patterns_to_remove = [
            r'^\d+\.\s*',      # Matches "1. ", "2. ", etc.
            r'^\d+\)\s*',      # Matches "1) ", "2) ", etc.
            r'^Q\d+\.?\s*',    # Matches "Q1. ", "Q2 ", etc.
            r'^Question\s+\d+[\.\)]?\s*'  # Matches "Question 1. ", etc.
        ]
        
        for pattern in patterns_to_remove:
            if re.match(pattern, clean_q, re.IGNORECASE):
                clean_q = re.sub(pattern, '', clean_q)
                break
        
        # Create question paragraph
        p_question = content_cell.add_paragraph()
        
        # Add question number (bold)
        num_run = p_question.add_run(f"{i}. ")
        num_run.bold = True
        
        # Add question text with formatting
        if clean_q:
            format_text(p_question, clean_q)
        
        # Add spacing (except after last question)
        if i < 5:
            content_cell.add_paragraph()

# --- 7. DOCX CREATOR ---
def create_docx(inputs, ai_data, teacher_name, principal_name, uploaded_image):
    doc = Document()
    
    # --- SETUP A4 PAGE SIZE & MARGINS ---
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # --- HEADER FOR DOCUMENT ---
    # Add school header to document
    header_para = doc.add_paragraph()
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Department line
    dept_run = header_para.add_run("DEPARTMENT OF EDUCATION REGION XI\n")
    dept_run.bold = True
    dept_run.font.size = Pt(12)
    
    # Division line
    div_run = header_para.add_run("DIVISION OF DAVAO DEL SUR\n")
    div_run.bold = True
    div_run.font.size = Pt(11)
    
    # School line
    school_run = header_para.add_run("MANUAL NATIONAL HIGH SCHOOL\n\n")
    school_run.bold = True
    school_run.font.size = Pt(14)
    
    # Title - IN ONE LINE
    title = doc.add_paragraph("Daily Lesson Plan (DLP) Generator")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(14)

    # --- TOP INFO TABLE ---
    table_top = doc.add_table(rows=1, cols=4)
    table_top.style = 'Table Grid'
    table_top.autofit = False
    
    table_top.columns[0].width = Inches(2.5)
    table_top.columns[1].width = Inches(1.15)
    table_top.columns[2].width = Inches(1.15)
    table_top.columns[3].width = Inches(2.5)

    def fill_cell(idx, label, value):
        cell = table_top.rows[0].cells[idx]
        p = cell.paragraphs[0]
        p.add_run(label).bold = True
        p.add_run("\n")
        format_text(p, value)

    fill_cell(0, "Subject Area:", inputs['subject'])
    fill_cell(1, "Grade Level:", inputs['grade'])
    fill_cell(2, "Quarter:", inputs['quarter'])
    fill_cell(3, "Date:", date.today().strftime('%B %d, %Y'))

    # --- MAIN CONTENT TABLE ---
    table_main = doc.add_table(rows=0, cols=2)
    table_main.style = 'Table Grid'
    table_main.autofit = False
    
    table_main.columns[0].width = Inches(2.0)
    table_main.columns[1].width = Inches(5.3)

    # Process Data
    objs = f"1. {ai_data.get('obj_1','')}\n2. {ai_data.get('obj_2','')}\n3. {ai_data.get('obj_3','')}"
    r = ai_data.get('resources', {})
    proc = ai_data.get('procedure', {})
    eval_sec = ai_data.get('evaluation', {})

    # SECTION I
    add_section_header(table_main, "I. CURRICULUM CONTENT, STANDARD AND LESSON COMPETENCIES")
    add_row(table_main, "A. Content Standard", inputs['content_std'])
    add_row(table_main, "B. Performance Standard", inputs['perf_std'])
    
    row_comp = table_main.add_row().cells
    row_comp[0].paragraphs[0].add_run("C. Learning Competencies").bold = True
    p_comp = row_comp[1].paragraphs[0]
    p_comp.add_run("Competency: ").bold = True
    format_text(p_comp, inputs['competency'])
    p_comp.add_run("\n\nObjectives:\n").bold = True
    p_comp.add_run(objs)

    add_row(table_main, "D. Content", ai_data.get('topic', ''))
    add_row(table_main, "E. Integration", f"Within: {ai_data.get('integration_within','')}\nAcross: {ai_data.get('integration_across','')}")

    # SECTION II
    add_section_header(table_main, "II. LEARNING RESOURCES")
    add_row(table_main, "Teacher Guide", r.get('guide', ''))
    add_row(table_main, "Learner's Materials(LMs)", r.get('materials', ''))
    add_row(table_main, "Textbooks", r.get('textbook', ''))
    add_row(table_main, "Learning Resource (LR) Portal", r.get('portal', ''))
    add_row(table_main, "Other Learning Resources", r.get('other', ''))

    # SECTION III
    add_section_header(table_main, "III. TEACHING AND LEARNING PROCEDURE")
    add_row(table_main, "A. Activating Prior Knowledge", proc.get('review', ''))
    
    # --- IMAGE ROW ---
    row_img = table_main.add_row().cells
    row_img[0].paragraphs[0].add_run("B. Establishing Lesson Purpose").bold = True
    
    cell_img = row_img[1]
    format_text(cell_img.paragraphs[0], proc.get('purpose_situation', ''))
    cell_img.paragraphs[0].add_run("\n")
    
    img_data = None
    if uploaded_image:
        img_data = uploaded_image
    else:
        raw_prompt = proc.get('visual_prompt', 'school')
        img_data = fetch_ai_image(raw_prompt)
    
    if img_data:
        try:
            p_i = cell_img.add_paragraph()
            p_i.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_i = p_i.add_run()
            run_i.add_picture(img_data, width=Inches(3.5))
        except:
            cell_img.add_paragraph("[Image Error]")
    else:
        cell_img.add_paragraph("[No Image Available]")
        
    cell_img.add_paragraph(f"\nVocabulary:\n{proc.get('vocabulary','')}")

    # Rest of Section III
    add_row(table_main, "C. Developing Understanding", 
            f"Activity: {proc.get('activity_main','')}\n\nExplicitation: {proc.get('explicitation','')}\n\nGroup 1: {proc.get('group_1','')}\nGroup 2: {proc.get('group_2','')}\nGroup 3: {proc.get('group_3','')}")
    add_row(table_main, "D. Making Generalization", proc.get('generalization', ''))

    # SECTION IV - REVISED ASSESSMENT SECTION
    add_section_header(table_main, "IV. EVALUATING LEARNING")
    add_assessment_row(table_main, "A. Assessment", eval_sec)
    add_row(table_main, "B. Assignment", eval_sec.get('assignment', ''))
    add_row(table_main, "C. Remarks", eval_sec.get('remarks', ''))
    add_row(table_main, "D. Reflection", eval_sec.get('reflection', ''))

    doc.add_paragraph()

    # --- SIGNATORIES TABLE ---
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.autofit = False
    
    sig_table.columns[0].width = Inches(4.0)
    sig_table.columns[1].width = Inches(4.0)
    
    row = sig_table.rows[0]
    
    # LEFT COLUMN: TEACHER SIGNATURE
    teacher_cell = row.cells[0]
    
    teacher_header_p = teacher_cell.add_paragraph()
    teacher_header_run = teacher_header_p.add_run("Prepared by:")
    teacher_header_run.bold = True
    
    teacher_cell.add_paragraph()
    
    teacher_name_p = teacher_cell.add_paragraph()
    teacher_name_run = teacher_name_p.add_run(teacher_name)
    teacher_name_run.bold = True
    
    teacher_position_p = teacher_cell.add_paragraph()
    teacher_position_p.add_run("Teacher III")
    
    # RIGHT COLUMN: PRINCIPAL SIGNATURE
    principal_cell = row.cells[1]
    
    principal_header_p = principal_cell.add_paragraph()
    principal_header_run = principal_header_p.add_run("Noted by:")
    principal_header_run.bold = True
    
    principal_cell.add_paragraph()
    
    principal_name_p = principal_cell.add_paragraph()
    principal_name_run = principal_name_p.add_run(principal_name)
    principal_name_run.bold = True
    
    principal_position_p = principal_cell.add_paragraph()
    principal_position_p.add_run("Principal III")

    # Save to BytesIO
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 8. STREAMLIT UI ---
def main():
    # Add custom header with maroon background (NO LOGOS)
    add_custom_header()
    
    # App Title - IN ONE LINE with custom styling
    st.markdown('<p class="app-title">Daily Lesson Plan (DLP) Generator</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("📋 User Information")
        
        # Set default names to the required values
        teacher_name = st.text_input("Teacher Name", value="RICHARD P. SAMORANOS")
        principal_name = st.text_input("Principal Name", value="ROSALITA A. ESTROPIA")
        
        st.markdown("---")
        st.info("Upload an image (optional) for the lesson")
        uploaded_image = st.file_uploader("Choose an image for lesson", type=['png', 'jpg', 'jpeg'], key="lesson")
        
        st.markdown("---")
        st.success("✅ API Key is already configured in the application")
    
    # Form Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        subject = st.text_input("Subject Area", placeholder="e.g., Mathematics")
    
    with col2:
        # Grade Level Dropdown - Kinder to Grade 12
        grade_options = [
            "Kinder",
            "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
            "Grade 7", "Grade 8", "Grade 9", "Grade 10",
            "Grade 11", "Grade 12"
        ]
        grade = st.selectbox("Grade Level", grade_options, index=6)  # Default to Grade 7
    
    with col3:
        # Quarter Dropdown - Roman Numerals
        quarter_options = ["I", "II", "III", "IV"]
        quarter = st.selectbox("Quarter", quarter_options, index=2)  # Default to Quarter III
    
    content_std = st.text_area("Content Standard", placeholder="The learner demonstrates understanding of...")
    perf_std = st.text_area("Performance Standard", placeholder="The learner is able to...")
    competency = st.text_area("Learning Competency", placeholder="Competency code and description...")
    
    st.markdown("---")
    
    # --- OPTIONAL LESSON OBJECTIVES SECTION ---
    st.subheader("📝 Optional: Lesson Objectives")
    st.info("If you already have your lesson objectives, enter them below. Otherwise, leave blank and AI will generate them.")
    
    with st.expander("Enter Lesson Objectives (Optional)", expanded=False):
        col_obj1, col_obj2, col_obj3 = st.columns(3)
        
        with col_obj1:
            obj_cognitive = st.text_area(
                "Cognitive Objective",
                placeholder="e.g., Identify the parts of a cell",
                height=100,
                help="What students should know or understand"
            )
        
        with col_obj2:
            obj_psychomotor = st.text_area(
                "Psychomotor Objective",
                placeholder="e.g., Draw and label the parts of a cell",
                height=100,
                help="What students should be able to do"
            )
        
        with col_obj3:
            obj_affective = st.text_area(
                "Affective Objective",
                placeholder="e.g., Appreciate the complexity of living organisms",
                height=100,
                help="Values, attitudes, or emotions to develop"
            )
    
    st.markdown("---")
    
    # Generate Button
    if st.button("🚀 Generate DLP", type="primary", use_container_width=True):
        if not all([subject, grade, quarter, content_std, perf_std, competency]):
            st.error("Please fill all required fields")
            return
        
        # Check if user provided objectives
        user_provided_objectives = obj_cognitive and obj_psychomotor and obj_affective
        
        if user_provided_objectives:
            st.info("✅ Using your provided lesson objectives")
            with st.spinner("🤖 Generating lesson content with YOUR objectives..."):
                ai_data = generate_lesson_content(
                    subject, grade, quarter, 
                    content_std, perf_std, competency,
                    obj_cognitive, obj_psychomotor, obj_affective
                )
        else:
            st.info("🔧 AI will generate lesson objectives for you")
            with st.spinner("🤖 Generating complete lesson content with AI..."):
                ai_data = generate_lesson_content(
                    subject, grade, quarter, 
                    content_std, perf_std, competency
                )
            
        if ai_data:
            st.success("✅ AI content generated successfully!")
            
            # Show objectives preview
            st.subheader("📋 Generated Objectives")
            col_obj_pre1, col_obj_pre2, col_obj_pre3 = st.columns(3)
            
            with col_obj_pre1:
                st.info("**Cognitive**")
                st.write(ai_data.get('obj_1', 'N/A'))
            
            with col_obj_pre2:
                st.info("**Psychomotor**")
                st.write(ai_data.get('obj_2', 'N/A'))
            
            with col_obj_pre3:
                st.info("**Affective**")
                st.write(ai_data.get('obj_3', 'N/A'))
            
            # Full preview
            with st.expander("📄 Preview All Generated Content"):
                st.json(ai_data)
            
            # Create DOCX
            inputs = {
                'subject': subject,
                'grade': grade,
                'quarter': quarter,
                'content_std': content_std,
                'perf_std': perf_std,
                'competency': competency
            }
            
            with st.spinner("📄 Creating DOCX file..."):
                docx_buffer = create_docx(inputs, ai_data, teacher_name, principal_name, uploaded_image)
            
            # Download button
            st.download_button(
                label="📥 Download DLP (.docx)",
                data=docx_buffer,
                file_name=f"DLP_{subject}_{grade}_Q{quarter}_{date.today()}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
            # Display success message
            st.balloons()
            st.success(f"✅ DLP generated for {subject} - {grade} - Quarter {quarter}")

if __name__ == "__main__":
    main()
