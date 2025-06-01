import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import time

load_dotenv(override=True)

SMALLESTAI_AGENT_KEY = os.getenv("SMALLESTAI_AGENT_KEY")
SMALLESTAI_AGENT_ID = os.getenv("SMALLESTAI_AGENT_ID")

def make_call_smallestai(to_number):
    import requests
    url = "https://atoms-api.smallest.ai/api/v1/conversation/outbound"
    payload = {
        "agentId": SMALLESTAI_AGENT_ID,  # Use AGENT_ID here, not AGENT_KEY
        "phoneNumber": f"+{to_number}"
    }
    headers = {
        "Authorization": f"Bearer {SMALLESTAI_AGENT_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Called {to_number}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error requesting smallest.ai: {e}")

def schedule_calls_from_excel(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # Remove accidental spaces from column headers

    for _, row in df.iterrows():
        name = row['Name']
        phone = str(row['Mobile Number'])
        date_val = row['Date']
        time_val = row['Time']

        # --- Parse date ---
        if isinstance(date_val, datetime):
            date_part = date_val.date()
        elif isinstance(date_val, str):
            try:
                date_part = datetime.strptime(date_val.strip(), "%d/%m/%Y").date()
            except Exception:
                date_part = datetime.strptime(date_val.strip(), "%Y-%m-%d").date()
        else:
            # fallback if it's a date object (rare, but possible)
            date_part = date_val

        # --- Parse time ---
        if isinstance(time_val, datetime):
            time_part = time_val.time()
        elif isinstance(time_val, str):
            try:
                time_part = datetime.strptime(time_val.strip(), "%H:%M").time()
            except Exception:
                # fallback to HH:MM:SS
                time_part = datetime.strptime(time_val.strip(), "%H:%M:%S").time()
        else:
            # fallback if it's already a time object
            time_part = time_val

        meeting_time = datetime.combine(date_part, time_part)
        call_time = meeting_time - timedelta(minutes=9)  # Change to 15min if needed

        if call_time < datetime.now():
            print(f"Skipping {name}, call time already passed: {call_time}")
            continue

        # Schedule the call
        scheduler.add_job(
            make_call_smallestai,
            'date',
            run_date=call_time,
            args=[phone],
            id=f"{phone}-{call_time}",
            misfire_grace_time=60*5  # 5 minutes grace period
        )
        print(f"Scheduled call to {name} ({phone}) at {call_time.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.start()

    EXCEL_FILE_PATH = "analysis/client_data.xlsx"  # Change if needed
    schedule_calls_from_excel(EXCEL_FILE_PATH)

    # Keep the script alive
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
