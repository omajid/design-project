#
# this class defines a user account

class UserAccount(object):
    def __init__(self, username='', email=''):
        self.name = username
        self.emailAddress = email
        # maps webpages to notifications
        self.webPages = { }

    def __eq__(self, other):
        try:
            return (self.name == other.name)
        except AttributeError, e:
            return 0

