from firebase_functions import https_fn
from firebase_admin import initialize_app, credentials, firestore
from notifications import send_general_notifications, send_event_specific_notifications
from event_checker import check_events_and_notify

cred = credentials.Certificate("serviceKey.json")

initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Define HTTP functions using decorators
@https_fn.on_request()
def http_send_general_notifications(req: https_fn.Request) -> https_fn.Response:
    return send_general_notifications(req)

@https_fn.on_request()
def http_send_event_specific_notifications(req: https_fn.Request) -> https_fn.Response:
    return send_event_specific_notifications(req)

@https_fn.on_request()
def http_check_events_and_notify(req: https_fn.Request) -> https_fn.Response:
    return check_events_and_notify(req)