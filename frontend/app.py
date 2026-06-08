import streamlit as st
import requests
import json
import time

# ─── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="ReqIntel AI — Requirement Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Backend URL (hidden from UI) ───────────────────────────────────────────
BASE_URL = "http://127.0.0.1:5000"

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font Import ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ──────────────────────────────────────────────── */
:root {
    --primary: #6C63FF;
    --primary-dark: #5A52D5;
    --accent: #00D2FF;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --bg-dark: #0E1117;
    --card-bg: rgba(30, 34, 45, 0.7);
    --card-border: rgba(108, 99, 255, 0.15);
    --text-primary: #E8E8ED;
    --text-muted: #9CA3AF;
}

/* ── Global Styles ───────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(145deg, #0E1117 0%, #1A1D29 50%, #0E1117 100%);
}

/* ── Header / Branding ───────────────────────────────────────────── */
.brand-header {
    text-align: center;
    padding: 2rem 0 1rem;
}
.brand-header h1 {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #00D2FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
    letter-spacing: -0.5px;
}
.brand-header p {
    color: var(--text-muted);
    font-size: 1.05rem;
    font-weight: 400;
}

/* ── Auth Card ───────────────────────────────────────────────────── */
.auth-card {
    max-width: 440px;
    margin: 2rem auto;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.auth-card h2 {
    color: var(--text-primary);
    font-weight: 700;
    font-size: 1.5rem;
    margin-bottom: 0.3rem;
}
.auth-card p {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* ── Metric Cards ────────────────────────────────────────────────── */
.metric-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 24px rgba(108,99,255,0.15);
}
.metric-card .metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
    line-height: 1;
}
.metric-card .metric-label {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 0.4rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ── Status Badges ───────────────────────────────────────────────── */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.status-uploaded  { background: rgba(245,158,11,0.15); color: #F59E0B; border: 1px solid rgba(245,158,11,0.3); }
.status-processing { background: rgba(108,99,255,0.15); color: #6C63FF; border: 1px solid rgba(108,99,255,0.3); }
.status-clarified { background: rgba(16,185,129,0.15); color: #10B981; border: 1px solid rgba(16,185,129,0.3); }
.status-error     { background: rgba(239,68,68,0.15);  color: #EF4444; border: 1px solid rgba(239,68,68,0.3);  }

/* ── History Row ─────────────────────────────────────────────────── */
.history-row {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: border-color 0.2s ease;
}
.history-row:hover {
    border-color: var(--primary);
}
.history-row .doc-name {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.95rem;
}
.history-row .doc-date {
    color: var(--text-muted);
    font-size: 0.8rem;
}

/* ── Requirement Card ────────────────────────────────────────────── */
.req-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.req-card h4 {
    color: var(--text-primary);
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.req-card .req-desc {
    color: var(--text-muted);
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 0.8rem;
}
.req-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}
.req-meta-item {
    background: rgba(108,99,255,0.08);
    border: 1px solid rgba(108,99,255,0.12);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.8rem;
    color: var(--text-muted);
}
.req-meta-item strong {
    color: var(--text-primary);
}

/* ── Clarity Score Bar ───────────────────────────────────────────── */
.clarity-bar-bg {
    background: rgba(255,255,255,0.08);
    border-radius: 8px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin-top: 4px;
}
.clarity-bar-fill {
    height: 100%;
    border-radius: 8px;
    transition: width 0.6s ease;
}

/* ── Section Title ───────────────────────────────────────────────── */
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-subtitle {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* ── Sidebar Customization ───────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161B22 0%, #0E1117 100%) !important;
    border-right: 1px solid rgba(108,99,255,0.1);
}
section[data-testid="stSidebar"] .stRadio > label {
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 1px;
}

/* ── Buttons ─────────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(108,99,255,0.25) !important;
}
div[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, #6C63FF, #5A52D5) !important;
    color: white !important;
    padding: 0.6rem 1.5rem !important;
    font-size: 1rem !important;
    border-radius: 10px !important;
    border: none !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 500;
}

/* ── File Uploader ───────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed rgba(108,99,255,0.3) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}

/* ── Divider ─────────────────────────────────────────────────────── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(108,99,255,0.3), transparent);
    margin: 1.5rem 0;
}

/* ── Question list ───────────────────────────────────────────────── */
.question-item {
    background: rgba(0,210,255,0.06);
    border-left: 3px solid var(--accent);
    padding: 8px 14px;
    margin-bottom: 6px;
    border-radius: 0 8px 8px 0;
    font-size: 0.88rem;
    color: var(--text-muted);
}

/* ── Profile Card ────────────────────────────────────────────────── */
.profile-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    backdrop-filter: blur(12px);
}
.profile-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6C63FF, #00D2FF);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem;
    font-size: 2rem;
    color: white;
}

/* ── Empty State ─────────────────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--text-muted);
}
.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "selected_doc" not in st.session_state:
    st.session_state.selected_doc = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"


# ─── Helper Functions ────────────────────────────────────────────────────────
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def get_status_badge(status: str) -> str:
    status_lower = status.lower()
    css_class = "status-uploaded"
    if status_lower == "processing":
        css_class = "status-processing"
    elif status_lower == "clarified":
        css_class = "status-clarified"
    elif status_lower in ("error", "failed"):
        css_class = "status-error"
    return f'<span class="status-badge {css_class}">{status}</span>'


def get_clarity_color(score: float) -> str:
    if score >= 0.7:
        return "#10B981"
    elif score >= 0.4:
        return "#F59E0B"
    return "#EF4444"


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH PAGES (Login / Register)
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.token:
    st.markdown("""
    <div class="brand-header">
        <h1>🧠 ReqIntel AI</h1>
        <p>Turn messy emails & PDFs into structured, actionable requirements</p>
    </div>
    """, unsafe_allow_html=True)

    # Centered auth container
    col_spacer_l, col_auth, col_spacer_r = st.columns([1, 1.5, 1])
    with col_auth:

        # Toggle between Login and Register
        auth_tab = st.radio(
            "Select action",
            ["Sign In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # ── Sign In ──────────────────────────────────────────────────────
        if auth_tab == "Sign In":
            st.markdown("""
            <div style="margin-bottom:1.2rem">
                <h2 style="color:#E8E8ED;font-weight:700;margin-bottom:4px">Welcome back</h2>
                <p style="color:#9CA3AF;font-size:0.9rem">Sign in to access your requirement projects</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                login_email = st.text_input("Email", placeholder="you@example.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")
                login_submit = st.form_submit_button("Sign In")

            if login_submit:
                if not login_email or not login_password:
                    st.error("Please enter both email and password.")
                else:
                    try:
                        resp = requests.post(
                            f"{BASE_URL}/login",
                            json={"email": login_email, "password": login_password},
                            timeout=10,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.token = data["access_token"]
                            st.session_state.user_id = data["user_id"]
                            st.success("✅ Login successful! Redirecting…")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(resp.json().get("error", "Login failed. Please try again."))
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to the backend server. Is it running?")

        # ── Create Account ───────────────────────────────────────────────
        else:
            st.markdown("""
            <div style="margin-bottom:1.2rem">
                <h2 style="color:#E8E8ED;font-weight:700;margin-bottom:4px">Create your account</h2>
                <p style="color:#9CA3AF;font-size:0.9rem">Start analyzing requirements with AI in seconds</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("register_form"):
                reg_email = st.text_input("Email", placeholder="you@example.com")
                reg_password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                reg_submit = st.form_submit_button("Create Account")

            if reg_submit:
                if not reg_email or not reg_password:
                    st.error("Please fill in all fields.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.warning("Password should be at least 6 characters.")
                else:
                    try:
                        resp = requests.post(
                            f"{BASE_URL}/register",
                            json={"email": reg_email, "password": reg_password},
                            timeout=10,
                        )
                        if resp.status_code == 201:
                            st.success("🎉 Account created! You can now sign in.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(resp.json().get("error", "Registration failed."))
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to the backend server. Is it running?")

    st.stop()  # Don't render the rest until authenticated


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATED — MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
headers = get_headers()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
        <span style="font-size:1.6rem;font-weight:800;background:linear-gradient(135deg,#6C63FF,#00D2FF);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">🧠 ReqIntel AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATION",
        ["📊 Dashboard", "📤 Upload & Analyze", "📂 History", "🔍 Document Details", "👤 Profile"],
        label_visibility="visible",
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # User info
    st.markdown(
        f'<p style="color:#9CA3AF;font-size:0.8rem;text-align:center">User ID: {st.session_state.user_id}</p>',
        unsafe_allow_html=True,
    )

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.user_id = None
        st.session_state.selected_doc = None
        st.rerun()


# ─── Page Router ─────────────────────────────────────────────────────────────

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("""
    <div class="brand-header" style="padding:1rem 0 0.5rem">
        <h1>📊 Dashboard</h1>
        <p>Overview of your requirement analysis workspace</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch history for metrics
    try:
        resp = requests.get(f"{BASE_URL}/api/history", headers=headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("history", [])
            total = len(history)
            uploaded = sum(1 for d in history if d["status"].upper() == "UPLOADED")
            processing = sum(1 for d in history if d["status"].upper() == "PROCESSING")
            completed = sum(1 for d in history if d["status"].upper() == "CLARIFIED")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total}</div>
                    <div class="metric-label">Total Documents</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{uploaded}</div>
                    <div class="metric-label">Uploaded</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{processing}</div>
                    <div class="metric-label">Processing</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{completed}</div>
                    <div class="metric-label">Completed</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

            # Recent documents
            st.markdown('<div class="section-title">🕐 Recent Documents</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">Your latest uploads and analyses</div>', unsafe_allow_html=True)

            if history:
                for doc in history[:5]:
                    badge = get_status_badge(doc["status"])
                    st.markdown(f"""
                    <div class="history-row">
                        <div>
                            <div class="doc-name">📄 {doc['filename']}</div>
                            <div class="doc-date">{doc['created_at']}</div>
                        </div>
                        <div>{badge}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="icon">📭</div>
                    <p>No documents yet. Start by uploading one!</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Could not load dashboard data.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to the backend server.")


# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD & ANALYZE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload & Analyze":
    st.markdown("""
    <div class="section-title">📤 Upload & Analyze</div>
    <div class="section-subtitle">Upload a document or paste text for AI-powered requirement extraction</div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Paste Text"])

    with tab1:
        st.markdown("**Supported formats:** PDF, TXT")
        uploaded_file = st.file_uploader(
            "Drag & drop your file here",
            type=["pdf", "txt"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            st.info(f"📎 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

            if st.button("🚀 Upload & Process", use_container_width=True):
                with st.spinner("Uploading and extracting text…"):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        resp = requests.post(f"{BASE_URL}/api/upload", files=files, headers=headers, timeout=30)
                        if resp.status_code == 202:
                            doc_id = resp.json().get("document_id")
                            st.success(f"✅ File uploaded! Document ID: **{doc_id}**")

                            # Trigger processing
                            with st.spinner("Starting AI analysis pipeline…"):
                                process_resp = requests.post(
                                    f"{BASE_URL}/api/process/{doc_id}", headers=headers, timeout=15
                                )
                                if process_resp.status_code in [200, 202]:
                                    st.info("🤖 AI analysis started in background. Check **History** for progress.")
                                else:
                                    st.warning(f"Upload succeeded but processing returned: {process_resp.json()}")
                        else:
                            st.error(f"Upload failed: {resp.json()}")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to the backend server.")

    with tab2:
        raw_text = st.text_area(
            "Paste email, meeting notes, or any raw requirement text",
            height=280,
            placeholder="e.g. 'The system should allow users to reset their password via email…'",
        )
        if raw_text and st.button("🧠 Analyze Text", use_container_width=True):
            with st.spinner("Processing your text…"):
                try:
                    resp = requests.post(
                        f"{BASE_URL}/api/upload", json={"text": raw_text}, headers=headers, timeout=15
                    )
                    if resp.status_code == 202:
                        doc_id = resp.json().get("document_id")
                        st.success(f"✅ Text received! Document ID: **{doc_id}**")

                        process_resp = requests.post(
                            f"{BASE_URL}/api/process/{doc_id}", headers=headers, timeout=15
                        )
                        if process_resp.status_code in [200, 202]:
                            st.info("🤖 AI analysis started. Check **History** for results.")
                        else:
                            st.warning(f"Processing response: {process_resp.json()}")
                    else:
                        st.error(f"Upload failed: {resp.json()}")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Cannot connect to the backend server.")


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📂 History":
    st.markdown("""
    <div class="section-title">📂 Analysis History</div>
    <div class="section-subtitle">Browse all your past document analyses</div>
    """, unsafe_allow_html=True)

    try:
        resp = requests.get(f"{BASE_URL}/api/history", headers=headers, timeout=10)
        if resp.status_code == 200:
            history = resp.json().get("history", [])
            if history:
                for doc in history:
                    badge = get_status_badge(doc["status"])
                    col1, col2, col3 = st.columns([4, 2, 1.5])
                    with col1:
                        st.markdown(f"""
                        <div style="padding:0.5rem 0">
                            <div class="doc-name" style="font-weight:600;color:#E8E8ED">📄 {doc['filename']}</div>
                            <div class="doc-date" style="color:#9CA3AF;font-size:0.8rem">{doc['created_at']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div style="padding-top:0.8rem">{badge}</div>', unsafe_allow_html=True)
                    with col3:
                        if st.button("View →", key=f"view_{doc['id']}"):
                            st.session_state.selected_doc = doc["id"]
                            st.rerun()

                    st.markdown('<div class="custom-divider" style="margin:0.5rem 0"></div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="icon">📭</div>
                    <p>No documents found. Head over to <strong>Upload & Analyze</strong> to get started!</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Failed to fetch history.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Cannot connect to the backend server.")


# ══════════════════════════════════════════════════════════════════════════════
# DOCUMENT DETAILS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Document Details":
    st.markdown("""
    <div class="section-title">🔍 Document Details</div>
    <div class="section-subtitle">Dive deep into AI-extracted requirements and clarity analysis</div>
    """, unsafe_allow_html=True)

    doc_id_input = st.number_input(
        "Enter Document ID",
        min_value=1,
        value=st.session_state.get("selected_doc", 1) or 1,
        step=1,
    )

    if st.button("🔎 Load Document", use_container_width=True):
        with st.spinner("Fetching document details…"):
            try:
                resp = requests.get(f"{BASE_URL}/api/document/{doc_id_input}", headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()

                    # Document header
                    badge = get_status_badge(data["status"])
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                        <span style="font-size:1.2rem;font-weight:700;color:#E8E8ED">Document #{data['document_id']}</span>
                        {badge}
                    </div>
                    """, unsafe_allow_html=True)

                    # Raw text snippet
                    if data.get("raw_text_snippet"):
                        with st.expander("📝 Raw Text Preview", expanded=False):
                            st.caption(data["raw_text_snippet"])

                    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

                    # Requirements
                    requirements = data.get("requirements", [])
                    if requirements:
                        st.markdown(
                            f'<div class="section-title">📋 Extracted Requirements ({len(requirements)})</div>',
                            unsafe_allow_html=True,
                        )

                        for req in requirements:
                            clarity = req.get("clarity_score")
                            clarity_display = f"{clarity:.0%}" if clarity is not None else "N/A"
                            clarity_color = get_clarity_color(clarity) if clarity else "#9CA3AF"
                            clarity_width = f"{clarity * 100:.0f}%" if clarity else "0%"

                            st.markdown(f"""
                            <div class="req-card">
                                <h4>🔹 {req['feature']}</h4>
                                <div class="req-desc">{req.get('description', 'No description')}</div>
                                <div class="req-meta">
                                    <div class="req-meta-item">🎯 <strong>Priority:</strong> {req.get('priority', 'N/A')}</div>
                                    <div class="req-meta-item">⚙️ <strong>Feasibility:</strong> {req.get('feasibility', 'N/A')}</div>
                                    <div class="req-meta-item">📊 <strong>Clarity:</strong> <span style="color:{clarity_color}">{clarity_display}</span></div>
                                </div>
                                <div style="margin-top:0.6rem">
                                    <div class="clarity-bar-bg">
                                        <div class="clarity-bar-fill" style="width:{clarity_width};background:{clarity_color}"></div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Risks
                            if req.get("risks"):
                                with st.expander("⚠️ Risks"):
                                    st.write(req["risks"])

                            # Ambiguous terms
                            if req.get("ambiguous_terms"):
                                with st.expander("🔶 Ambiguous Terms"):
                                    for term in req["ambiguous_terms"]:
                                        st.markdown(f"- `{term}`")

                            # Missing info
                            if req.get("missing_info"):
                                with st.expander("❓ Missing Information"):
                                    for info in req["missing_info"]:
                                        st.markdown(f"- {info}")

                            # Clarification questions
                            cq = req.get("clarification_questions", [])
                            if cq:
                                with st.expander("💬 Clarification Questions"):
                                    for q in cq:
                                        st.markdown(
                                            f'<div class="question-item">{q}</div>',
                                            unsafe_allow_html=True,
                                        )
                    else:
                        st.markdown("""
                        <div class="empty-state">
                            <div class="icon">⏳</div>
                            <p>No requirements extracted yet. The document may still be processing.</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("📛 Document not found or you don't have access.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to the backend server.")


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Profile":
    st.markdown("""
    <div class="section-title">👤 My Profile</div>
    <div class="section-subtitle">Your account information and session details</div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        # Fetch profile from /api/me
        try:
            resp = requests.get(f"{BASE_URL}/api/me", headers=headers, timeout=10)
            if resp.status_code == 200:
                profile = resp.json()
                user_id = profile.get("your_user_id", st.session_state.user_id)

                st.markdown(f"""
                <div class="profile-card">
                    <div class="profile-avatar">👤</div>
                    <h3 style="color:#E8E8ED;margin-bottom:0.3rem">User #{user_id}</h3>
                    <p style="color:#9CA3AF;font-size:0.9rem">{profile.get("message", "Authenticated")}</p>
                    <div class="custom-divider"></div>
                    <div style="display:flex;justify-content:center;gap:2rem;margin-top:1rem">
                        <div>
                            <div style="color:#6C63FF;font-size:1.5rem;font-weight:700">{user_id}</div>
                            <div style="color:#9CA3AF;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px">User ID</div>
                        </div>
                        <div>
                            <div style="color:#10B981;font-size:1.5rem;font-weight:700">●</div>
                            <div style="color:#9CA3AF;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.5px">Active</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Could not fetch profile. Your session may have expired.")
                if st.button("🔄 Re-login"):
                    st.session_state.token = None
                    st.rerun()
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to the backend server.")

        # Fetch document stats
        st.markdown("")
        try:
            resp = requests.get(f"{BASE_URL}/api/history", headers=headers, timeout=10)
            if resp.status_code == 200:
                history = resp.json().get("history", [])
                total = len(history)
                completed = sum(1 for d in history if d["status"].upper() == "CLARIFIED")

                st.markdown(f"""
                <div class="metric-card" style="margin-top:1rem">
                    <div style="display:flex;justify-content:space-around">
                        <div>
                            <div class="metric-value">{total}</div>
                            <div class="metric-label">Documents</div>
                        </div>
                        <div>
                            <div class="metric-value" style="color:#10B981">{completed}</div>
                            <div class="metric-label">Analyzed</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            pass