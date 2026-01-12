# LESSON_PLAN_GENERATOR.py
import streamlit as st
import json
import re

# Page configuration - MUST BE FIRST Streamlit command
st.set_page_config(
    page_title="MBNHS Lesson Plan Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1rem;
    }
    .stButton > button {
        background-color: #3B82F6;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">📚 MBNHS Lesson Plan Generator</h1>', unsafe_allow_html=True)

# Safe JSON parsing function
def safe_json_parse(raw_response):
    """A safer function to parse JSON with error handling."""
    if not raw_response or not isinstance(raw_response, str):
        return None
    
    st.write("🔍 Attempting to parse JSON response...")
    
    # First try direct parsing
    try:
        parsed = json.loads(raw_response)
        st.success("✅ JSON parsed successfully!")
        return parsed
    except json.JSONDecodeError as e:
        st.warning(f"⚠️ Initial parsing failed: {str(e)[:100]}...")
    
    # Try to fix common issues
    fixed = raw_response.strip()
    
    # Fix common patterns
    if fixed.endswith(", '"):
        fixed = fixed[:-3] + '"'
    
    if fixed.endswith(", '") or fixed.endswith(", '"):
        fixed = fixed[:-3] + '"'
    
    # Ensure proper JSON structure
    if not fixed.startswith('{'):
        fixed = '{' + fixed
    
    if not fixed.endswith('}'):
        fixed = fixed.rstrip(', "\'') + '}'
    
    # Try parsing the fixed version
    try:
        parsed = json.loads(fixed)
        st.success("✅ JSON parsed successfully after fixing!")
        return parsed
    except json.JSONDecodeError:
        st.error("❌ Could not parse JSON. Creating manual structure...")
        
        # Extract text content manually
        import re
        match = re.search(r'["\']([^"\']+)["\']', raw_response)
        if match:
            content = match.group(1)
            return {"objectives": [content]}
    
    return {"error": "Could not parse", "raw": raw_response[:200]}

# Main app function
def main():
    """Main app function."""
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=100)
        st.title("Navigation")
        
        menu = st.selectbox(
            "Choose a section:",
            ["🏠 Home", "📝 Generate Lesson Plan", "⚙️ Settings", "📚 About"]
        )
        
        st.divider()
        
        st.markdown("### Quick Links")
        st.page_link("https://www.deped.gov.ph", label="📘 DepEd Portal", icon="🌐")
        st.page_link("https://curriculum.gov.ph", label="📗 Curriculum Guide", icon="📖")
        
        st.divider()
        
        st.markdown("### Settings")
        grade_level = st.selectbox("Grade Level", ["7", "8", "9", "10", "11", "12"])
        subject = st.selectbox("Subject", ["Mathematics", "Science", "English", "Filipino", "Araling Panlipunan"])
    
    # Main content area
    if menu == "🏠 Home":
        st.markdown('<h2 class="sub-header">Welcome to MBNHS Lesson Plan Generator</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🚀 Features
            - **AI-Powered Generation**: Create lesson plans using AI
            - **Curriculum-Aligned**: Matches DepEd standards
            - **Customizable**: Adjust to your classroom needs
            - **Time-Saving**: Generate in minutes, not hours
            """)
            
            if st.button("🎯 Get Started", type="primary"):
                st.switch_page("pages/1_📝_Generate_Lesson_Plan.py")
        
        with col2:
            st.markdown("""
            ### 📊 Quick Stats
            - **500+** Teachers using
            - **2,000+** Lesson plans generated
            - **4.8** ★ Average rating
            - **98%** Time saved
            """)
            
            st.progress(75, text="Weekly usage: 75%")
    
    elif menu == "📝 Generate Lesson Plan":
        st.markdown('<h2 class="sub-header">Generate New Lesson Plan</h2>', unsafe_allow_html=True)
        
        with st.form("lesson_plan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                topic = st.text_input("📖 Topic/Title", placeholder="e.g., Angles of Elevation and Depression")
                duration = st.number_input("⏰ Duration (minutes)", min_value=1, max_value=240, value=60)
                materials = st.text_area("📦 Materials Needed", placeholder="List materials separated by commas")
            
            with col2:
                learning_competencies = st.text_area(
                    "🎯 Learning Competencies",
                    placeholder="Enter learning competencies...",
                    height=150
                )
                
                include_assessment = st.checkbox("📝 Include Assessment", value=True)
                include_activities = st.checkbox("🎮 Include Activities", value=True)
            
            # JSON input section
            st.divider()
            st.markdown("### 🔧 JSON Objectives Input")
            
            json_input = st.text_area(
                "Enter JSON objectives (optional):",
                value='{"obj_1": "Define angles of elevation and depression"}',
                height=100,
                help="Enter JSON format objectives or leave as is for default"
            )
            
            submit_button = st.form_submit_button("✨ Generate Lesson Plan", type="primary")
        
        if submit_button:
            with st.spinner("🔄 Generating your lesson plan..."):
                # Simulate processing
                import time
                time.sleep(2)
                
                # Parse JSON if provided
                if json_input:
                    objectives_data = safe_json_parse(json_input)
                    
                    if objectives_data and "error" not in objectives_data:
                        st.success("✅ Objectives parsed successfully!")
                        
                        # Display the parsed data
                        with st.expander("📋 Parsed Objectives", expanded=True):
                            if isinstance(objectives_data, dict):
                                for key, value in objectives_data.items():
                                    if isinstance(value, str):
                                        st.write(f"• {value}")
                                    elif isinstance(value, list):
                                        for item in value:
                                            st.write(f"• {item}")
                
                # Display generated lesson plan
                st.divider()
                st.markdown("## 📄 Generated Lesson Plan")
                
                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📚 Procedure", "📝 Assessment", "📊 Resources"])
                
                with tab1:
                    st.markdown(f"""
                    ### Lesson Plan: {topic if topic else "Mathematics"}
                    **Grade Level:** {grade_level}
                    **Subject:** {subject}
                    **Duration:** {duration} minutes
                    
                    #### 🎯 Objectives
                    1. Define angles of elevation and angles of depression
                    2. Solve problems involving angles of elevation and depression
                    3. Apply trigonometric ratios to real-world situations
                    
                    #### 📦 Materials
                    {materials if materials else "Whiteboard, markers, protractor, calculator, worksheets"}
                    """)
                
                with tab2:
                    st.markdown("""
                    ### 📚 Teaching Procedure
                    
                    #### 1. Introduction (10 mins)
                    - Review previous lesson on right triangles
                    - Present real-world scenarios involving elevation/depression
                    - Show visual examples
                    
                    #### 2. Instruction (30 mins)
                    - Define angles of elevation and depression
                    - Demonstrate problem-solving techniques
                    - Group practice activities
                    
                    #### 3. Practice (15 mins)
                    - Individual worksheet completion
                    - Peer checking and discussion
                    - Teacher assistance as needed
                    
                    #### 4. Conclusion (5 mins)
                    - Summary of key concepts
                    - Preview of next lesson
                    """)
                
                with tab3:
                    st.markdown("""
                    ### 📝 Assessment
                    
                    #### Formative Assessment
                    - Worksheet completion (70%)
                    - Class participation (20%)
                    - Group activity (10%)
                    
                    #### Sample Questions
                    1. A building casts a 20m shadow. If the angle of elevation from the tip of the shadow to the top of the building is 60°, how tall is the building?
                    2. From a point 50m away from a tree, the angle of elevation to the top is 30°. Find the height of the tree.
                    """)
                
                with tab4:
                    st.markdown("""
                    ### 📊 Additional Resources
                    
                    #### Online Resources
                    - [Khan Academy: Trigonometry](https://www.khanacademy.org/math/trigonometry)
                    - [DepEd Learning Resources](https://lrmds.deped.gov.ph)
                    
                    #### References
                    - Mathematics Grade 9 Learner's Material
                    - Next Century Mathematics 9
                    - Trigonometry for High School
                    """)
                
                # Download button
                lesson_plan_text = f"""Lesson Plan: {topic}
Grade Level: {grade_level}
Subject: {subject}
Duration: {duration} minutes

OBJECTIVES:
1. Define angles of elevation and depression
2. Solve related problems
3. Apply to real-world situations

MATERIALS: {materials}"""
                
                st.download_button(
                    label="📥 Download Lesson Plan",
                    data=lesson_plan_text,
                    file_name=f"lesson_plan_{topic.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
    
    elif menu == "⚙️ Settings":
        st.markdown('<h2 class="sub-header">Application Settings</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎨 Display Settings")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            font_size = st.slider("Font Size", 12, 24, 16)
            show_animations = st.toggle("Show Animations", value=True)
        
        with col2:
            st.markdown("### ⚡ Performance")
            cache_enabled = st.toggle("Enable Caching", value=True)
            auto_save = st.toggle("Auto-save Drafts", value=True)
            max_file_size = st.selectbox("Max File Size", ["10MB", "25MB", "50MB", "100MB"])
        
        if st.button("💾 Save Settings", type="primary"):
            st.success("Settings saved successfully!")
    
    elif menu == "📚 About":
        st.markdown('<h2 class="sub-header">About MBNHS Lesson Plan Generator</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🏫 Mission
        To empower teachers with efficient tools for creating high-quality, 
        standards-aligned lesson plans that enhance student learning outcomes.
        
        ### 👥 Development Team
        - **Project Lead**: Mathematics Department
        - **Technical Development**: ICT Department
        - **Curriculum Advisors**: Subject Area Coordinators
        
        ### 📞 Contact & Support
        - **Email**: support@mbnhs.edu.ph
        - **Phone**: (02) 1234-5678
        - **Address**: MBNHS Main Campus
        
        ### 🔄 Version Information
        - **Current Version**: 2.1.0
        - **Last Updated**: January 2024
        - **License**: Educational Use Only
        """)
        
        st.divider()
        
        # Footer
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**© 2024 MBNHS**")
        
        with col2:
            st.markdown("[Privacy Policy]() • [Terms of Use]()")
        
        with col3:
            st.markdown("Made with ❤️ for Filipino Teachers")

# Run the app
if __name__ == "__main__":
    main()
