
NOTIFICATION_TYPE_EMAIL = 'email'
NOTIFICATION_TYPE_CLIENT = 'client'
NOTIFICATION_TYPE_SMS = 'sms'

def getClientNotificationOption():
    notifcation = NotificationOptions(NOTIFICATION_TYPE_CLIENT)
    return notification

def getEmailNotificationOption():
    notifcation = NotificationOptions(NOTIFICATION_TYPE_EMAIL)
    return notification

def getSmsNotificationOption():
    notifcation = NotificationOptions(NOTIFICATION_TYPE_SMS)
    return notification

class NotificationOptions:
    def __init__(self, type):
        self.type = str(type)

    def __str__():
        return 'Notifying using: ' + self.type

    def getType():
        return self.text
