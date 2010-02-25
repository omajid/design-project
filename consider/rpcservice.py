from twisted.web import xmlrpc

class XmlRpcUsers(xmlrpc.XMLRPC):
    """An xml rpc service for users to interact with

    """

    def __init__(self, service):
        xmlrpc.XMLRPC.__init__(self)
        self.service = service

    # FIXME:
    # - need to sanitize input to deal with security issues
    # - implement authentication to ensure the use is the right
    #   user

    def xmlrpc_getUsers(self):
        return self.service.getUsers()
    def xmlrpc_addUser(self, user):
        return self.service.addUser(user)
    def xmlrpc_removeUser(self, user):
        return self.service.removeUser(user)

    def xmlrpc_setEmailAddress(self, user, emailAddress):
        return self.service.setEmailAddress(user, emailAddress)
    def xmlrpc_getEmailAddress(self, user):
        return self.service.getEmailAddress(user)

    def xmlrpc_getWebPages(self, user):
        return self.service.getWebPages(user)
    def xmlrpc_addWebPage(self, user, webPage, notificationTypes, frequency):
        return self.service.addWebPage(user, webPage, notificationTypes, frequency)
    def xmlrpc_getNotificationTypes(self, user, webPage):
        return self.service.getNotificationTypes(user, webPage)
    def xmlrpc_getFrequency(self, user, webPage):
        return self.service.getFrequency(user, webPage)
    def xmlrpc_removeWebPage(self, user, webPage):
        return self.service.removeWebPage(user, webPage)

    def xmlrpc_getNewDiff(self, user, webPage):
        return self.service.getNewDiff(user, webPage)
