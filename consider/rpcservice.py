from twisted.internet import defer
from twisted.application import service
from twisted.web import xmlrpc
from twisted.python import log

class XmlRpcUsers(xmlrpc.XMLRPC):
    """An xml rpc service for users to interact with

    """

    def __init__(self, service):
        xmlrpc.XMLRPC.__init__(self)
        self.service = service

    def xmlrpc_getUsers(self):
        return self.service.getUsers()
    def xmlrpc_addUser(self, user):
        return self.service.addUser(user)
    def xmlrcp_removeUser(self, user):
        return self.service.removeUser(user)

    def xmlrpc_getWebPages(self, user):
        return self.service.getWebPages(user)
    def xmlrpc_addWebPage(self, user, webpage):
        return self.service.addWebPage(user, webpage)
    def xmlrpc_removeWebPage(self, user, webpage):
        return self.service.removeWebPage(user, webpage)

class MonitorService(service.Service):
    """A service for monitoring webpages

    The service is used to communicate with the client program

    """

    def __init__(self):

        # { user1: [ website1, website2], user2: [ website3, website4] ... }
        self.users = { }

    def getResource(self):
        return XmlRpcUsers(self)

    def getUsers(self):
        return defer.succeed(self.users.keys())

    def addUser(self, user):
        if not user in self.users:
            self.users[user] = []
            return defer.succeed([])
        else:
            return defer.fail([])

    def removeUser(self, user):
        if not user in self.user:
            return defer.fail(user)
        else:
            del self.users[user]
            return defer.succeed(self.user.keys())
    
    def getWebPages(self, user):
        if user in self.users:
            return defer.succeed(self.users[user])
        else:
            return defer.fail([])

    def addWebPage(self, user, webpage):
        webpages = self.users[user]
        if not webpage in webpages:
            webpages.append(webpage)
        return defer.succeed(webpages)

    def removeWebPage(self, user, webpage):
        if user in self.users:
            if webpage in self.users[user]:
                self.users[user].remove(webpage)
                return defer.succeed([])
            return defer.fail([])
        return defer.fail([])
            
