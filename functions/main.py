from firebase_functions import https_fn
from firebase_admin import initialize_app, credentials,firestore, messaging
from datetime import datetime, timezone, timedelta

cred = credentials.Certificate("serviceKey.json")

initialize_app(cred)

db = firestore.client()

def send_event_notification(event_title, user_name, token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"Upcoming Event: {event_title}",
            body=f"Hi {user_name}, your event is starting in 5 minutes!",
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        print(f'Successfully sent ${event_title}  message: {user_name}', response)
    except Exception as e:
        print('Error sending message:', str(e))
        
def send_general_notification(title, desc, token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"{title}",
            body=f"{desc}",
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        print(f'Successfully sent', response)
    except Exception as e:
        print('Error sending message:', str(e))
        
def send_event_notification(event_title, event_description, user_name, token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"Event Update: {event_title}",
            body=f"Hi {user_name}, {event_description}",
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        print(f'Successfully sent notification for {event_title} to {user_name}', response)
        return True
    except Exception as e:
        print('Error sending message:', str(e))
        return False




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
    

# send a general notification to all the users.
@https_fn.on_request()
def send_general_notifications(req: https_fn.Request) -> https_fn.Response:
    try:
        request_json = req.get_json()
        
        if request_json and 'title' in request_json and 'description' in request_json:
            title = request_json['title']
            description = request_json['description']
        else:
            return https_fn.Response("Missing title or description in the request body", status=400)

        # Get all users from the database
        users_ref = db.collection('users').get()
        notification_count = 0

        for user in users_ref:
            user_data = user.to_dict()
            user_token = user_data.get('fcmId', '')

            if user_token:
                send_general_notification(title, description, user_token)
                notification_count += 1

        return https_fn.Response(f"Notifications sent to {notification_count} users", status=200)

    except Exception as e:
        print(f"Error: {str(e)}")
        return https_fn.Response(f"Error occurred: {str(e)}", status=500)


# takes event id, and send notification to all users with that id in registerd events.
# POST /send_event_specific_notifications
# Content-Type: application/json

# {
#   "eventId": "abc123",
    # "title":"Mirage",
    # "description":"desc"
# }
@https_fn.on_request()
def send_event_specific_notifications(req: https_fn.Request) -> https_fn.Response:
    try:
        # Parse the request body
        request_json = req.get_json()
        
        if request_json and 'eventId' and 'title' in request_json and 'description' in request_json:
            event_id = request_json['eventId']
            event_title=request_json['title']
            event_description=request_json['description']
            
        else:
            return https_fn.Response("Missing eventId in the request body", status=400)

        users_ref = db.collection('users').get()
        notification_count = 0

        for user in users_ref:
            user_data = user.to_dict()
            user_token = user_data.get('fcmId', '')
            user_name = user_data.get('userName', 'User')
            user_event_ids = user_data.get('eventUniqueIds', [])

            if user_token and event_id in user_event_ids:
                success = send_event_notification(event_title, event_description, user_name, user_token)
                if success:
                    notification_count += 1

        return https_fn.Response(f"Notifications sent to {notification_count} users for event {event_id}", status=200)

    except Exception as e:
        print(f"Error: {str(e)}")
        return https_fn.Response(f"Error occurred: {str(e)}", status=500)

