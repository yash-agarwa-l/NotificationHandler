from firebase_functions import https_fn
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta
from notification_helpers import send_event_notification

def check_events_and_notify(req: https_fn.Request) -> https_fn.Response:
    db = firestore.client() 
    try:
        events_ref = db.collection('events')
        now = datetime.now(timezone.utc)
        
        events = events_ref.get()
        event_count = 0

        for event in events:
            event_count += 1
            event_data = event.to_dict()
            event_start_time = event_data.get('details', {}).get('eventDate', None)
            event_title = event_data.get('details', {}).get('title', 'Event')

            if not event_start_time:
                print(f"Event {event_title} has no start time, skipping.")
                continue
            
            event_start_time = event_start_time.astimezone(timezone.utc)
            notify_time = event_start_time - timedelta(minutes=5)

            if now >= notify_time:
                users_ref = db.collection('users').get()
                for user in users_ref:
                    user_data = user.to_dict()
                    user_token = user_data.get('fcmId', '')
                    user_name = user_data.get('userName', '')

                    if user_token:
                        send_event_notification(event_title, "Your event is starting in 5 minutes!", user_name, user_token)

        return https_fn.Response(f"{event_count} events checked and notifications sent")

    except Exception as e:
        print(f"Error: {str(e)}")
        return https_fn.Response(f"Error occurred: {str(e)}", status=500)
