
NOTIFICATION_TYPE_EMAIL = 'email'
NOTIFICATION_TYPE_CLIENT = 'client'
NOTIFICATION_TYPE_SMS = 'sms'

def getClientNotificationOption():
    notifcation = NotificationOptions([NOTIFICATION_TYPE_CLIENT])
    return notification

def getEmailNotificationOption():
    notifcation = NotificationOptions([NOTIFICATION_TYPE_EMAIL])
    return notification

def getSmsNotificationOption():
    notifcation = NotificationOptions([NOTIFICATION_TYPE_SMS])
    return notification

class NotificationOptions(object):
    def __init__(self, types = []):
        '''

        types: a list of constants indicating the types of notification
        '''
        self.types = types

    def __str__(self):
        return 'Notifying using: ' + str(self.types)

    def setTypes(self, types):
        self.types = types

    def getTypes(self):
        return self.types
