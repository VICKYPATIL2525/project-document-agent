"""
Streamlit Web Interface - Student Project Documentation Generator
Provides a user-friendly form for inputs and handles document generation.
"""
import os
import json
import time
import threading
import streamlit as st
from datetime import datetime
from pipeline import run_pipeline, get_tracker
from config import OUTPUT_DIR, TRACKING_DIR, MAX_PAGES, MIN_PAGES


# ─── Page Configuration ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Project Doc Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #e0e0e0;
        font-size: 1.1rem;
    }
    .stButton>button {
        width: 100%;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .info-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    .tracking-step {
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-radius: 5px;
    }
    .step-completed { background: #d4edda; }
    .step-running { background: #fff3cd; }
    .step-pending { background: #f8f9fa; }
    .step-failed { background: #f8d7da; }
</style>
""", unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>📄 Project Documentation Generator</h1>
    <p>Generate your final year project Black Book / Synopsis / Thesis in minutes</p>
</div>
""", unsafe_allow_html=True)


# ─── Session State Init ──────────────────────────────────────────────────────

if "generation_started" not in st.session_state:
    st.session_state.generation_started = False
if "result" not in st.session_state:
    st.session_state.result = None
if "job_id" not in st.session_state:
    st.session_state.job_id = None

# ─── Test Data (auto-fill) ────────────────────────────────────────────────────

_TEST_DATA = {
    "project_title": "Smart Attendance System using Face Recognition",
    "tech_stack": "Python, OpenCV, Flask, SQLite, HTML/CSS, JavaScript",
    "target_pages": 60,
    "project_summary": (
        "The Smart Attendance System is an AI-powered application that automates "
        "student attendance tracking using real-time face recognition. The system "
        "captures live video from a webcam, detects faces using Haar Cascade classifiers, "
        "and recognizes students by comparing facial embeddings generated with the "
        "dlib/face_recognition library against a pre-enrolled database stored in SQLite. "
        "Once a student is identified, their attendance is automatically logged with "
        "a timestamp. The backend is built with Flask and exposes REST APIs for "
        "enrollment, attendance retrieval, and report generation. The frontend is a "
        "responsive web dashboard built with HTML, CSS, and JavaScript that allows "
        "teachers to view attendance records, generate class-wise and date-wise reports, "
        "and export data as CSV/PDF. Key modules include: Face Detection Module, "
        "Face Recognition & Encoding Module, Attendance Logger, Admin Dashboard, "
        "and Report Generator. The system solves the problem of proxy attendance and "
        "manual errors in traditional roll-call methods, improving accuracy and saving time."
    ),
    "additional_info": (
        "Database schema: students(id, name, roll_no, department, face_encoding), "
        "attendance(id, student_id, timestamp, status). "
        "API endpoints: POST /enroll, GET /attendance, GET /report. "
        "Uses face_recognition library with 128-dimensional encodings. "
        "Threshold for match: 0.6 Euclidean distance."
    ),
    "project_code": (
        '# app.py - Main Flask Application\n'
        'from flask import Flask, render_template, request, jsonify\n'
        'import face_recognition, cv2, sqlite3, os\n'
        'from datetime import datetime\n\n'
        'app = Flask(__name__)\n\n'
        'def get_db():\n'
        '    conn = sqlite3.connect("attendance.db")\n'
        '    return conn\n\n'
        '@app.route("/")\n'
        'def index():\n'
        '    return render_template("dashboard.html")\n\n'
        '@app.route("/enroll", methods=["POST"])\n'
        'def enroll_student():\n'
        '    name = request.form["name"]\n'
        '    roll_no = request.form["roll_no"]\n'
        '    image = request.files["photo"]\n'
        '    img = face_recognition.load_image_file(image)\n'
        '    encoding = face_recognition.face_encodings(img)[0]\n'
        '    db = get_db()\n'
        '    db.execute("INSERT INTO students (name, roll_no, face_encoding) VALUES (?, ?, ?)",\n'
        '              (name, roll_no, encoding.tobytes()))\n'
        '    db.commit()\n'
        '    return jsonify({"status": "enrolled"})\n\n'
        '@app.route("/mark_attendance")\n'
        'def mark_attendance():\n'
        '    cap = cv2.VideoCapture(0)\n'
        '    ret, frame = cap.read()\n'
        '    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)\n'
        '    face_locations = face_recognition.face_locations(rgb)\n'
        '    face_encs = face_recognition.face_encodings(rgb, face_locations)\n'
        '    # Compare with enrolled students...\n'
        '    cap.release()\n'
        '    return jsonify({"marked": len(face_encs)})\n'
    ),
    "college_format": "",
    "student_name": "Rahul Sharma",
    "roll_number": "CS-2022-042",
    "college_name": "Mumbai Institute of Technology",
    "department": "Department of Computer Science & Engineering",
    "guide_name": "Prof. Anita Deshmukh",
    "year": "2025-2026",
}


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    test_mode = st.toggle("🧪 Auto-fill Test Data", value=False, help="Fill all fields with sample data for quick testing")
    st.markdown("---")
    
    st.markdown("### 📊 How It Works")
    st.markdown("""
    1. **Fill in your project details**
    2. **Upload code** or paste summary
    3. **Set page count** (10-250)
    4. **Click Generate** and wait
    5. **Download** your formatted `.docx`
    """)
    
    st.markdown("---")
    st.markdown("### 📈 Capabilities")
    st.markdown("""
    - ✅ Up to 250 pages
    - ✅ Professional formatting
    - ✅ Auto-adjusted content
    - ✅ Code blocks with syntax
    - ✅ Diagram placeholders
    - ✅ Table of Contents
    - ✅ References (IEEE format)
    - ✅ Title & Certificate pages
    """)
    
    st.markdown("---")
    st.markdown("### 🔍 Previous Jobs")
    
    # List previous tracking files
    if os.path.exists(TRACKING_DIR):
        tracking_files = sorted(
            [f for f in os.listdir(TRACKING_DIR) if f.endswith(".json")],
            reverse=True,
        )[:5]
        for tf in tracking_files:
            with open(os.path.join(TRACKING_DIR, tf), "r") as f:
                data = json.load(f)
            status_emoji = "✅" if data["status"] == "completed" else "❌" if data["status"] == "failed" else "⏳"
            st.text(f"{status_emoji} {data['job_id']}")
    else:
        st.text("No previous jobs")


# ─── Main Form ────────────────────────────────────────────────────────────────

if not st.session_state.generation_started:

    tab1, tab2 = st.tabs(["📝 Project Details", "🎓 Student & College Info"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            project_title = st.text_input(
                "📌 Project Title *",
                value=_TEST_DATA["project_title"] if test_mode else "",
                placeholder="e.g., Online Examination System using MERN Stack",
            )

            tech_stack = st.text_input(
                "🛠️ Technology Stack *",
                value=_TEST_DATA["tech_stack"] if test_mode else "",
                placeholder="e.g., React, Node.js, MongoDB, Express.js",
            )

            target_pages = st.slider(
                "📄 Number of Pages",
                min_value=MIN_PAGES,
                max_value=MAX_PAGES,
                value=_TEST_DATA["target_pages"] if test_mode else 60,
                step=5,
                help="Total pages including title, certificate, TOC, chapters, and references",
            )

        with col2:
            project_summary = st.text_area(
                "📋 Project Summary / Description *",
                value=_TEST_DATA["project_summary"] if test_mode else "",
                placeholder="Describe your project in detail: what it does, features, modules, "
                "how it works, problem it solves, etc. The more detail you provide, "
                "the better the output.",
                height=200,
            )

        additional_info = st.text_area(
            "📎 Additional Information (Optional)",
            value=_TEST_DATA["additional_info"] if test_mode else "",
            placeholder="Any extra details: specific requirements, methodologies used, "
            "database schema, API endpoints, etc.",
            height=100,
        )

        # Code Upload
        st.markdown("#### 💻 Project Code (Optional)")
        code_upload_method = st.radio(
            "How would you like to provide your code?",
            ["Paste Code", "Upload File", "No Code"],
            horizontal=True,
        )

        project_code = ""
        if code_upload_method == "Paste Code":
            project_code = st.text_area(
                "Paste your main code here",
                value=_TEST_DATA["project_code"] if test_mode else "",
                placeholder="Paste your important source code files here...",
                height=300,
            )
        elif code_upload_method == "Upload File":
            uploaded_files = st.file_uploader(
                "Upload source code files",
                type=["py", "js", "ts", "java", "cpp", "c", "html", "css", "jsx", "tsx", "php", "rb", "go", "rs", "kt"],
                accept_multiple_files=True,
            )
            if uploaded_files:
                code_parts = []
                for uf in uploaded_files:
                    content = uf.read().decode("utf-8", errors="ignore")
                    code_parts.append(f"// ===== File: {uf.name} =====\n{content}\n")
                project_code = "\n".join(code_parts)
                st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

        # College format
        st.markdown("#### 📐 College Format Template (Optional)")
        college_format = st.text_area(
            "Paste your college's document format/structure if any",
            value=_TEST_DATA["college_format"] if test_mode else "",
            placeholder="e.g., Chapter 1 must be Introduction with sections: "
            "1.1 Background, 1.2 Problem Statement...",
            height=100,
        )

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            student_name = st.text_input("👤 Student Name", value=_TEST_DATA["student_name"] if test_mode else "Student Name")
            roll_number = st.text_input("🔢 Roll Number", value=_TEST_DATA["roll_number"] if test_mode else "000")
            college_name = st.text_input("🏫 College Name", value=_TEST_DATA["college_name"] if test_mode else "University")

        with col2:
            department = st.text_input(
                "🎓 Department", value=_TEST_DATA["department"] if test_mode else "Department of Computer Science"
            )
            guide_name = st.text_input("👨‍🏫 Guide / Mentor Name", value=_TEST_DATA["guide_name"] if test_mode else "Prof. Guide")
            year = st.text_input("📅 Academic Year", value=_TEST_DATA["year"] if test_mode else "2025-2026")

    # ─── Generate Button ──────────────────────────────────────────────────────

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Documentation", type="primary", use_container_width=True):
            # Validation
            if not project_title:
                st.error("❌ Please enter a project title.")
            elif not project_summary:
                st.error("❌ Please provide a project summary / description.")
            elif not tech_stack:
                st.error("❌ Please specify the technology stack.")
            elif len(project_summary.split()) < 20:
                st.error("❌ Please provide a more detailed project summary (at least 20 words).")
            else:
                st.session_state.generation_started = True
                st.session_state.inputs = {
                    "project_title": project_title,
                    "project_summary": project_summary,
                    "project_code": project_code,
                    "tech_stack": tech_stack,
                    "target_pages": target_pages,
                    "college_format": college_format,
                    "additional_info": additional_info,
                    "student_name": student_name,
                    "roll_number": roll_number,
                    "college_name": college_name,
                    "department": department,
                    "guide_name": guide_name,
                    "year": year,
                }
                st.rerun()


# ─── Generation in Progress ──────────────────────────────────────────────────

else:
    if st.session_state.result is None:
        st.markdown("### ⏳ Generating Your Documentation...")
        st.markdown("This may take **2-10 minutes** depending on the page count.")

        progress_bar = st.progress(0, text="Starting pipeline...")

        inputs = st.session_state.inputs

        # Show what we're generating
        with st.expander("📋 Generation Details", expanded=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("Target Pages", inputs["target_pages"])
            col2.metric("Summary Words", len(inputs["project_summary"].split()))
            col3.metric("Code Provided", "Yes" if inputs["project_code"] else "No")

        # Debug log console
        st.markdown("#### 🖥️ Live Debug Console")
        log_container = st.empty()

        # Run pipeline in a thread so we can poll logs
        pipeline_result = [None]
        pipeline_error = [None]

        def _run():
            try:
                pipeline_result[0] = run_pipeline(
                    project_title=inputs["project_title"],
                    project_summary=inputs["project_summary"],
                    project_code=inputs["project_code"],
                    tech_stack=inputs["tech_stack"],
                    target_pages=inputs["target_pages"],
                    college_format=inputs["college_format"],
                    additional_info=inputs["additional_info"],
                    student_name=inputs["student_name"],
                    roll_number=inputs["roll_number"],
                    college_name=inputs["college_name"],
                    department=inputs["department"],
                    guide_name=inputs["guide_name"],
                    year=inputs["year"],
                )
            except Exception as exc:
                pipeline_error[0] = exc

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()

        # Poll for live log updates
        prev_log_count = 0
        while worker.is_alive():
            time.sleep(1)
            # Find the tracker for the latest job
            from pipeline import _trackers
            tracker = None
            if _trackers:
                tracker = list(_trackers.values())[-1]
            if tracker:
                logs = tracker.get_logs()
                if len(logs) != prev_log_count:
                    prev_log_count = len(logs)
                    log_text = "\n".join(logs)
                    log_container.code(log_text, language="text")
                # Update progress bar
                progress = tracker.get_progress()
                pct = min(progress.get("progress_pct", 0), 95)
                elapsed = progress.get("duration_seconds", 0)
                progress_bar.progress(
                    max(5, pct),
                    text=f"{progress.get('current_step', 'Processing')} — {elapsed:.0f}s elapsed",
                )

        worker.join()

        # Final log update
        from pipeline import _trackers
        tracker = list(_trackers.values())[-1] if _trackers else None
        if tracker:
            log_text = "\n".join(tracker.get_logs())
            log_container.code(log_text, language="text")

        if pipeline_error[0]:
            st.error(f"❌ Generation failed: {str(pipeline_error[0])}")
            st.session_state.generation_started = False
        elif pipeline_result[0]:
            progress_bar.progress(100, text="✅ Generation Complete!")
            st.session_state.result = pipeline_result[0]
            st.rerun()

    # ─── Results Display ──────────────────────────────────────────────────────

    else:
        result = st.session_state.result

        if result["status"] == "completed":
            st.success("🎉 Documentation generated successfully!")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Status", "✅ Complete")
            col2.metric("Total Tokens", f"{result.get('total_tokens', {}).get('total', 0):,}")
            col3.metric("Cost (USD)", f"${result.get('cost_usd', 0):.4f}")
            col4.metric("Duration", f"{result.get('duration_seconds', 0):.1f}s")

            # Download button
            output_file = result.get("output_file", "")
            if output_file and os.path.exists(output_file):
                with open(output_file, "rb") as f:
                    file_data = f.read()

                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label="📥 Download Your Document (.docx)",
                        data=file_data,
                        file_name=f"{st.session_state.inputs['project_title'].replace(' ', '_')}_Report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                    )

            # Show tracking details
            tracking_file = result.get("tracking_file", "")
            if tracking_file and os.path.exists(tracking_file):
                with st.expander("📊 Generation Tracking Details", expanded=False):
                    with open(tracking_file, "r") as f:
                        tracking_data = json.load(f)

                    st.json(tracking_data)

                    # Step-by-step breakdown
                    st.markdown("#### Step-by-Step Breakdown")
                    for step in tracking_data.get("steps", []):
                        status_emoji = {
                            "completed": "✅",
                            "failed": "❌",
                            "in_progress": "⏳",
                        }.get(step["status"], "⬜")

                        st.markdown(
                            f"""<div class="tracking-step step-{'completed' if step['status'] == 'completed' else 'failed' if step['status'] == 'failed' else 'running'}">
                            {status_emoji} <strong>{step['step_name']}</strong> — 
                            Tokens: {step['tokens']['total']:,} | 
                            Duration: {step['duration_seconds']}s | 
                            LLM Calls: {step['llm_calls']}
                            </div>""",
                            unsafe_allow_html=True,
                        )

            # Show debug log
            logs = result.get("logs", [])
            if logs:
                with st.expander("🖥️ Debug Console Log", expanded=False):
                    st.code("\n".join(logs), language="text")

        else:
            st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")

        # Reset button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Generate Another Document", use_container_width=True):
                st.session_state.generation_started = False
                st.session_state.result = None
                st.session_state.job_id = None
                st.rerun()
