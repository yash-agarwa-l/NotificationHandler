import sys
sys.path.append('./')
from firebase_functions import https_fn
from firebase_admin import initialize_app, credentials, firestore
# from notifications import send_general_notifications, send_event_specific_notifications
# from event_checker import check_events_and_notify

cred = credentials.Certificate("serviceKey.json")

initialize_app(cred)

db = firestore.client()

# to send notification to all users.
# body:{
    # "title":"Mirage",
    # "description":"desc",
    # "image_url":""
# }
@https_fn.on_request()
def http_send_general_notifications(req: https_fn.Request) -> https_fn.Response:
    return send_general_notifications(req)


# takes event id, and send notification to all users with that id in registerd events.
# POST /send_event_specific_notifications
# Content-Type: application/json
# {
#   "eventId": "abc123",
    # "title":"Mirage",
    # "description":"desc"
    # "image_url":"" optional parameter
# }
@https_fn.on_request()
def http_send_event_specific_notifications(req: https_fn.Request) -> https_fn.Response:
    return send_event_specific_notifications(req)

# 
@https_fn.on_request()
def http_check_events_and_notify(req: https_fn.Request) -> https_fn.Response:
    return check_events_and_notify(req)