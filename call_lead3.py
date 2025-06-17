import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import os
from dotenv import load_dotenv
import io

load_dotenv(override=True)

SMALLESTAI_AGENT_KEY = os.getenv("SMALLESTAI_AGENT_KEY")

# Agent IDs per use case
AGENT_IDS = {
    "Feedback Call for Customers Who Churned": "683bfa446a3886c925dbc2b4",
    "AI Demo & Onboarding Call Reminder": "683bfa8d6a3886c925dbc37d",
    "Pending Invoice Reminder Call": "683bfa7f6a3886c925dbc363"
}

# Initialize scheduler
scheduler = BackgroundScheduler()
if not scheduler.running:
    scheduler.start()

# Page configuration
st.set_page_config(
    page_title="AiSensy Voice Call Scheduler",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main app background */
    .main {
        background-color: #f5f7fa;
        padding: 0;
    }
    
    /* Hide default Streamlit styling */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling to match AiSensy */
    section[data-testid="stSidebar"] {
        background-color: #1b4f4f;
        width: 300px;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, #128c7e 0%, #25d366 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 15px;
        margin: 0 0 2rem 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-banner h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-banner p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border-left: 4px solid #128c7e;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .feature-card h3 {
        color: #1b4f4f;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        color: #666;
        font-size: 0.95rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #25d366 0%, #128c7e 100%);
        color: white;
        border: none;
        padding: 0.75rem 2.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: #128c7e;
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: #0f6b60;
        transform: translateY(-2px);
    }
    
    /* Select box complete styling */
    .stSelectbox {
        color: #1b4f4f !important;
    }
    
    .stSelectbox > label {
        color: #1b4f4f !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox > div > div {
        background-color: white !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        color: #1b4f4f !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #128c7e !important;
    }
    
    /* Force all select box text to be visible */
    .stSelectbox > div > div > div {
        color: #1b4f4f !important;
    }
    
    .stSelectbox > div > div > div > div {
        color: #1b4f4f !important;
    }
    
    /* Selectbox svg icon */
    .stSelectbox svg {
        fill: #1b4f4f !important;
    }
    
    /* The actual selected value text */
    div[data-baseweb="select"] {
        color: #1b4f4f !important;
    }
    
    div[data-baseweb="select"] > div {
        color: #1b4f4f !important;
        background-color: white !important;
    }
    
    div[data-baseweb="select"] > div > div {
        color: #1b4f4f !important;
    }
    
    div[data-baseweb="select"] > div > div > div {
        color: #1b4f4f !important;
    }
    
    /* All spans inside selectbox */
    .stSelectbox span {
        color: #1b4f4f !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="popover"] {
        background-color: white !important;
    }
    
    [role="listbox"] {
        background-color: white !important;
    }
    
    [role="option"] {
        color: #1b4f4f !important;
        background-color: white !important;
    }
    
    [role="option"]:hover {
        background-color: #e8f5f3 !important;
    }
    
    [role="option"][aria-selected="true"] {
        background-color: #e8f5f3 !important;
        font-weight: 600;
    }
    
    /* File uploader */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #f8f9fa;
        border: 2px dashed #128c7e;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
    }
    
    section[data-testid="stFileUploadDropzone"]:hover {
        background-color: #f0f8f7;
        border-color: #25d366;
    }
    
    /* Data frame */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    /* Success alert */
    .stSuccess {
        background-color: #d4f8e8;
        color: #0f6b60;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #25d366;
        font-weight: 500;
    }
    
    /* Warning alert */
    .stWarning {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        font-weight: 500;
    }
    
    /* Error alert */
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        font-weight: 500;
    }
    
    /* Info alert */
    .stInfo {
        background-color: #e8f4fc;
        color: #0c5460;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        font-weight: 500;
    }
    
    /* Sidebar content styling */
    .sidebar-header {
        color: white;
        padding: 1rem;
        text-align: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .sidebar-section {
        color: white;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-section h3 {
        color: white;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    .sidebar-section ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .sidebar-section li {
        padding: 0.5rem 0;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
    }
    
    .sidebar-section li:before {
        content: "→ ";
        color: #25d366;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #128c7e;
    }
    
    /* Tables */
    .stTable {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    /* Ensure text visibility */
    h1, h2, h3, h4, h5, h6 {
        color: #1b4f4f !important;
    }
    
    /* Make sure all text in main area is visible */
    .main p {
        color: #333 !important;
    }
    
    /* Override for specific elements that need dark text */
    .css-1v0mbdj > div > div > div > div > div {
        color: #1b4f4f !important;
    }
    
    .css-1aehpvj {
        color: #1b4f4f !important;
    }
    
    /* Ensure selected text in selectbox is always visible */
    div.css-1wa3eu0-placeholder {
        color: #1b4f4f !important;
    }
    
    div.css-1uccc91-singleValue {
        color: #1b4f4f !important;
    }
    
    /* Table text */
    .stTable td, .stTable th {
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

def generate_excel_template():
    sample_data = {
        "Name": ["Saurabh"],
        "Mobile Number": ["918709077106"],
        "Source": ["ORGANIC"],
        "Tags": ["New"],
        "Date": ["31/5/2025"],
        "Time": ["19:16"],
        "Description": ["entest"]
    }
    df_template = pd.DataFrame(sample_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Contacts')
    processed_data = output.getvalue()
    return processed_data

def make_call_smallestai(to_number, call_type, agent_id):
    url = "https://atoms-api.smallest.ai/api/v1/conversation/outbound"
    payload = {
        "agentId": agent_id,
        "phoneNumber": f"+{to_number}"
    }
    headers = {
        "Authorization": f"Bearer {SMALLESTAI_AGENT_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        st.write(f"📞 Called {to_number} ({call_type}): {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"❌ Error calling {to_number}: {e}")

def schedule_reminder_calls(df, agent_id, lead_time_minutes=9):
    scheduled = []
    skipped = []
    for _, row in df.iterrows():
        try:
            phone = str(row['Mobile Number']).strip()
            date_val = row['Date']
            time_val = row['Time']

            # Parse date
            if isinstance(date_val, datetime):
                date_part = date_val.date()
            else:
                date_part = datetime.strptime(str(date_val).strip(), "%d/%m/%Y").date()

            # Parse time
            if isinstance(time_val, datetime):
                time_part = time_val.time()
            else:
                time_part = datetime.strptime(str(time_val).strip(), "%H:%M").time()

            meeting_time = datetime.combine(date_part, time_part)
            call_time = meeting_time - timedelta(minutes=lead_time_minutes)

            if call_time < datetime.now():
                skipped.append({"Phone": phone, "Reason": "Call time passed"})
                continue

            job_id = f"{phone}-{call_time.strftime('%Y%m%d%H%M')}"
            scheduler.add_job(
                make_call_smallestai,
                'date',
                run_date=call_time,
                args=[phone, "Demo & Onboarding Reminder", agent_id],
                id=job_id,
                misfire_grace_time=60*5
            )
            scheduled.append({"Phone": phone, "Scheduled Call Time": call_time})
        except Exception as e:
            skipped.append({"Phone": row.get('Mobile Number', 'N/A'), "Reason": f"Parsing error: {e}"})
    return scheduled, skipped

def call_customers_immediately(df, call_type, agent_id):
    results = []
    for _, row in df.iterrows():
        phone = str(row['Mobile Number']).strip()
        try:
            make_call_smallestai(phone, call_type, agent_id)
            results.append({"Phone": phone, "Status": "✅ Called"})
        except Exception as e:
            results.append({"Phone": phone, "Status": f"❌ Failed: {e}"})
    return results

def main():
    # Main container
    container = st.container()
    
    with container:
        # Header banner
        st.markdown("""
        <div class="header-banner">
            <h1>🎯 AiSensy Voice Call Scheduler</h1>
            <p>Automate your voice calls with powerful AI</p>
        </div>
        """, unsafe_allow_html=True)

        # Create columns
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Template section
            st.markdown("""
            <div class="feature-card">
                <h3>📋 Download Template</h3>
                <p>Get started with our Excel template</p>
            </div>
            """, unsafe_allow_html=True)
            
            excel_template = generate_excel_template()
            st.download_button(
                label="⬇️ Download Contact Template",
                data=excel_template,
                file_name="AI_Sensy_Contacts_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with col2:
            # Call type selection
            st.markdown("""
            <div class="feature-card">
                <h3>📞 Select Call Campaign</h3>
                <p>Choose the type of call campaign you want to run</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a container with specific styling
            with st.container():
                call_type = st.selectbox(
                    "Select Campaign Type",
                    [
                        "Feedback Call for Customers Who Churned",
                        "AI Demo & Onboarding Call Reminder",
                        "Pending Invoice Reminder Call"
                    ],
                    index=0,  # Default to first option
                    key="campaign_selector"
                )
                
                # Display selected option clearly
                if call_type:
                    st.markdown(f"<p style='color: #128c7e; font-weight: 600; margin-top: 0.5rem;'>✓ Selected: {call_type}</p>", unsafe_allow_html=True)

        # File upload section
        st.markdown("""
        <div class="feature-card">
            <h3>📤 Upload Contacts</h3>
            <p>Upload your Excel file with contact information</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=["xlsx"],
            help="Upload an Excel file containing contact information"
        )

        if uploaded_file and call_type:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()

            required_cols = {'Name', 'Mobile Number', 'Date', 'Time'}
            if not required_cols.issubset(set(df.columns)):
                st.error(f"❌ Uploaded file must contain these columns: {', '.join(required_cols)}")
                return

            # Data preview
            st.markdown("""
            <div class="feature-card">
                <h3>👀 Data Preview</h3>
                <p>Review your uploaded contacts</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(df.head(), use_container_width=True)

            # Process button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Start Processing", use_container_width=True):
                    agent_id = AGENT_IDS.get(call_type)
                    
                    with st.spinner('🔄 Processing your contacts...'):
                        if call_type == "AI Demo & Onboarding Call Reminder":
                            scheduled, skipped = schedule_reminder_calls(df, agent_id)
                            
                            if scheduled:
                                st.success(f"✅ Successfully scheduled {len(scheduled)} reminder calls!")
                                with st.container():
                                    st.markdown("<h3 style='color: #1b4f4f;'>📅 Scheduled Calls</h3>", unsafe_allow_html=True)
                                    st.dataframe(pd.DataFrame(scheduled), use_container_width=True)
                            
                            if skipped:
                                st.warning(f"⚠️ Skipped {len(skipped)} contacts")
                                with st.container():
                                    st.markdown("<h3 style='color: #1b4f4f;'>⏭️ Skipped Contacts</h3>", unsafe_allow_html=True)
                                    st.dataframe(pd.DataFrame(skipped), use_container_width=True)
                        else:
                            results = call_customers_immediately(df, call_type, agent_id)
                            st.success(f"✅ Initiated {len(results)} calls!")
                            with st.container():
                                st.markdown("<h3 style='color: #1b4f4f;'>📊 Call Results</h3>", unsafe_allow_html=True)
                                st.dataframe(pd.DataFrame(results), use_container_width=True)

        # Footer info
        st.markdown("---")
        st.info("💡 **Note:** Keep this app running for scheduled calls to be executed. The app will automatically make calls at the scheduled times.")

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2 style="color: white; margin: 0;">🎯 AiSensy</h2>
        <p style="color: #ccc; margin: 0; font-size: 0.9rem;">Voice Call Automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <h3>📊 Features</h3>
        <ul>
            <li>Automated voice calls</li>
            <li>Schedule reminders</li>
            <li>Bulk call campaigns</li>
            <li>Real-time processing</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section">
        <h3>🔧 Call Types</h3>
        <ul>
            <li>Customer feedback</li>
            <li>Demo reminders</li>
            <li>Invoice reminders</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-section" style="text-align: center; margin-top: 3rem;">
        <p style="color: #888; font-size: 0.8rem;">Powered by SmallestAI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()