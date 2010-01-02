#!/usr/bin/env python

class WebCommunication:
    def __init__(self):
        pass

    def getWebPage(self, address):
        pass


    def authenticate(self, user, address):
        pass


class NotificationCommunication:
    def __init__(self):
        pass

    def notifyUser(self, user, notification):
        pass

class Notification(object):

    type = [ EMAIL, DESKTOP, SMS, PHONE_CALL ]

    def __init__(self):
        pass


class User(object):
    def __init__(self):
        self.id = ''
        self.name = ''
   
def startServer():

    


if __name__ == '__main__':
    print 'Starting server...'
    startServer()

