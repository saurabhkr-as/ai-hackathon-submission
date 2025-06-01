import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import os
from dotenv import load_dotenv
import io

load_dotenv(override=True)

SMALLESTAI_AGENT_KEY = st.secrets["SMALLESTAI_AGENT_KEY"]

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

def generate_excel_template():
    sample_data = {
        "Name": ["Himadri"],
        "Mobile Number": ["918274988339"],
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
        st.write(f"Called {to_number} ({call_type}): {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error calling {to_number}: {e}")

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
            results.append({"Phone": phone, "Status": "Called"})
        except Exception as e:
            results.append({"Phone": phone, "Status": f"Failed: {e}"})
    return results

def main():
    st.title("AI Sensy Voice Call Scheduler")

    st.markdown("### Download Excel Template")
    excel_template = generate_excel_template()
    st.download_button(
        label="Download Contact Upload Template",
        data=excel_template,
        file_name="AI_Sensy_Contacts_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    call_type = st.selectbox(
        "Select Call Type",
        [
            "Feedback Call for Customers Who Churned",
            "AI Demo & Onboarding Call Reminder",
            "Pending Invoice Reminder Call"
        ]
    )

    uploaded_file = st.file_uploader("Upload Excel file with contacts", type=["xlsx"])

    if uploaded_file and call_type:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        required_cols = {'Name', 'Mobile Number', 'Date', 'Time'}
        if not required_cols.issubset(set(df.columns)):
            st.error(f"Uploaded file must contain these columns: {required_cols}")
            return

        st.write("Preview of uploaded data:")
        st.dataframe(df.head())

        if st.button("Start Processing"):
            agent_id = AGENT_IDS.get(call_type)
            print("agentid ",agent_id)

            if call_type == "AI Demo & Onboarding Call Reminder":
                scheduled, skipped = schedule_reminder_calls(df, agent_id)
                st.success(f"Scheduled {len(scheduled)} reminder calls.")
                if scheduled:
                    st.table(pd.DataFrame(scheduled))
                if skipped:
                    st.warning(f"Skipped {len(skipped)} contacts.")
                    st.table(pd.DataFrame(skipped))
            else:
                results = call_customers_immediately(df, call_type, agent_id)
                st.success(f"Initiated {len(results)} calls.")
                st.table(pd.DataFrame(results))

    st.info("Note: Keep this app running for scheduled calls to be executed.")

if __name__ == "__main__":
    main()

