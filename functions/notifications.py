from firebase_functions import https_fn
from firebase_admin import firestore
from notification_helpers import send_general_notification, send_event_notification


def send_general_notifications(req: https_fn.Request) -> https_fn.Response:
    db = firestore.client()
    try:
        request_json = req.get_json()
        
        if request_json and 'title' in request_json and 'description' in request_json:
            title = request_json['title']
            description = request_json['description']
            image_url = request_json.get('image_url') 
        else:
            return https_fn.Response("Missing title or description in the request body", status=400)

        users_ref = db.collection('users').get()
        notification_count = 0

        for user in users_ref:
            user_data = user.to_dict()
            user_token = user_data.get('fcmId', '')

            if user_token:
                send_general_notification(title, description, user_token, image_url)
                notification_count += 1

        return https_fn.Response(f"Notifications sent to {notification_count} users", status=200)

    except Exception as e:
        print(f"Error: {str(e)}")
        return https_fn.Response(f"Error occurred: {str(e)}", status=500)


def send_event_specific_notifications(req: https_fn.Request) -> https_fn.Response:
    db = firestore.client()
    try:
        request_json = req.get_json()
        
        if request_json and 'eventId' and 'title' and 'description' in request_json:
            event_id = request_json['eventId']
            event_title = request_json.get('title')
            event_description = request_json.get('description')
            image_url = request_json.get('image_url')
        else:
            return https_fn.Response("Missing eventId in the request body", status=400)

        # Fetch imageurl if not provideed.
        if not image_url:
            event_doc = db.collection('event').document('sat24').collection('events').document(event_id).get()
            if event_doc.exists:
                event_data = event_doc.to_dict()
                image_url = image_url or event_data.get('imageUrl')
            else:
                return https_fn.Response(f"Event with ID {event_id} not found", status=404)
            
        users_ref = db.collection('users').get()
        notification_count = 0

        for user in users_ref:
            user_data = user.to_dict()
            user_token = user_data.get('fcmId', '')
            user_name = user_data.get('userName', 'User')
            user_event_ids = user_data.get('eventUniqueIds', [])

            if user_token and event_id in user_event_ids:
                success = send_event_notification(event_title, event_description, user_name, user_token, image_url)
                if success:
                    notification_count += 1

        return https_fn.Response(f"Notifications sent to {notification_count} users for event {event_id}", status=200)

    except Exception as e:
        print(f"Error: {str(e)}")
        return https_fn.Response(f"Error occurred: {str(e)}", status=500)

