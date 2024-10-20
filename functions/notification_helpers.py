from firebase_admin import messaging

def send_general_notification(title, desc, token,image=None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"{title}",
            body=f"{desc}",
            image=f"{image}"
        ),
        token=token,
    )
    try:
        response = messaging.send(message)
        print(f'Successfully sent', response)
        return True
    except Exception as e:
        print('Error sending message:', str(e))
        return False
    

def send_event_notification(event_title, event_description, user_name, token, image_url=None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"Event Update: {event_title}",
            body=f"Hi {user_name}, {event_description}",
            image=image_url 
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