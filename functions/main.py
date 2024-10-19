from firebase_functions import https_fn
from firebase_admin import initialize_app, firestore, messaging
from datetime import datetime, timezone, timedelta

# Initialize Firebase app
initialize_app()
db = firestore.client()

def send_notification(event_title, user_name, token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"Upcoming Event: {event_title}",
            body=f"Hi {user_name}, your event is starting in 5 minutes!",
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print('Error sending message:', str(e))

@https_fn.on_request()
def check_events_and_notify(req: https_fn.Request) -> https_fn.Response:
    try:
        events_ref = db.collection('events')
        now = datetime.now(timezone.utc)
        
        events = events_ref.get()
        a=0

        for event in events:
            a+=1
            event_data = event.to_dict()
            event_start_time = event_data.get('details', {}).get('eventDate', None)
            event_title = event_data.get('details', {}).get('title', 'Event')

            if not event_start_time:
                print(f"Event {event_title} has no start time, skipping.")
                continue

            # Convert the event time to UTC
            event_start_time = event_start_time.astimezone(timezone.utc)
            notify_time = event_start_time - timedelta(minutes=5)

            if now >= notify_time:
                users_ref = db.collection('users').get()
                for user in users_ref:
                    user_data = user.to_dict()
                    user_token = user_data.get('fcmId', '')
                    user_name = user_data.get('userName', '')

                    if user_token:
                        send_notification(event_title, user_name, user_token)

        return https_fn.Response(str(a)+"Function executed")

    except Exception as e:
        print(f"Error: {str(e)}")
        return https_fn.Response(f"Error occurred: {str(e)}", status=500)
