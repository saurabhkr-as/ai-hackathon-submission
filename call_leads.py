import os
from dotenv import load_dotenv
load_dotenv(override=True)

SMALLESTAI_AGENT_KEY=os.getenv("SMALLESTAI_AGENT_KEY")
SMALLESTAI_AGENT_ID=os.getenv("SMALLESTAI_AGENT_ID")
async def make_call_smallestai(to_number):

    import requests
    url = "https://atoms-api.smallest.ai/api/v1/conversation/outbound"

    payload = {
        "agentId": SMALLESTAI_AGENT_KEY,
        "phoneNumber": "+918709077106"
    }
    headers = {
        "Authorization": f"Bearer {SMALLESTAI_AGENT_KEY}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.request("POST", url, json=payload, headers=headers)
    except Exception as e:
        print(f"error reqesting smaller.ai{e}")

    return response




