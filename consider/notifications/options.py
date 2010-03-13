import exceptions

NOTIFICATION_TYPE_EMAIL = 'email'
NOTIFICATION_TYPE_CLIENT = 'client'
NOTIFICATION_TYPE_SMS = 'sms'
MAX_FREQUENCY = 3
MIN_FREQUENCY = 1
MIN_WC_THRESHOLD = 0
MAX_WC_THRESHOLD = 50

def getClientNotificationOption():
    notification = NotificationOptions([NOTIFICATION_TYPE_CLIENT])
    return notification

def getEmailNotificationOption():
    notification = NotificationOptions([NOTIFICATION_TYPE_EMAIL])
    return notification

def getSmsNotificationOption():
    notification = NotificationOptions([NOTIFICATION_TYPE_SMS])
    return notification

class NotificationOptions(object):
    def __init__(self, types = [], lastSeen = {}):
        '''

        types: a list of constants indicating the types of notification
        '''
        self._types = types
        self._frequency = 0
        self._lastSeen = lastSeen
        self._wcThreshold = 0

    def __str__(self):
        return 'Notifying using: ' + str(self._types)

    def setTypes(self, types):
        self._types = types

    def getNotificationTypes(self):
        return self._types

    def getFrequency(self):
        return self._frequency

    def setFrequency(self, frequency):
        if frequency < MIN_FREQUENCY:
            frequency = MIN_FREQUENCY
        if frequency > MAX_FREQUENCY:
            frequency = MAX_FREQUENCY
        self._frequency = frequency

    def getWCThreshold(self):
        return self._wcThreshold

    def setWCThreshold(self, minCount):
        if minCount < MIN_WC_THRESHOLD:
            minCount = MIN_WC_THRESHOLD
        elif minCount > MAX_WC_THRESHOLD:
            minCount = MAX_WC_THRESHOLD
        self._wcThreshold = minCount

    def getLastSeen(self, type):
        '''get the name of the last seen cache entry for some type of notification'''
        try:
            return self._lastSeen[type]
        except exceptions.KeyError, e:
            return None

    def setLastSeen(self, type, lastSeen):
        '''set the name of the last seen cache entry for the type of notification'''
        self._lastSeen[type] = lastSeen

