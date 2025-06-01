# Download the helper library from https://www.twilio.com/docs/python/install
# import os
# from twilio.rest import Client
# import json

# # Find your Account SID and Auth Token at twilio.com/console
# # and set the environment variables. See http://twil.io/secure
# account_sid = os.environ["TWILIO_ACCOUNT_SID"]
# auth_token = os.environ["TWILIO_AUTH_TOKEN"]
# client = Client(account_sid, auth_token)

# message = client.messages.create(
#     content_sid="HXXXXXXXXX",
#     to="whatsapp:+18551234567",
#     from_="whatsapp:+15005550006",
#     content_variables=json.dumps({"1": "Name"}),
#     messaging_service_sid="MGXXXXXXXX",
# )

# print(message.body)