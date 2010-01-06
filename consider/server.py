
from twisted.application import service, internet
from twisted.internet import defer
from twisted.web import server
from twisted.python import log

from consider import rpcservice, storage
#from consider.webpage import WebPage

class MasterService(service.MultiService):
    def __init__(self):
        service.MultiService.__init__(self)

        self.rpcServerPort = 1055
        self.monitorService = MonitorService()
        self.rpcServer = internet.TCPServer(
                            self.rpcServerPort, 
                            server.Site(self.monitorService.getResource()))
        self.rpcServer.setServiceParent(self)


        
class MonitorService(service.Service):
    """A service for monitoring webpages

    The service is used to communicate with the client program

    """

    def __init__(self):

        # { user1: [ website1, website2], user2: [ website3, website4] ... }
        self.users = { }
        self.cache = storage.WebPageCache()

    def getResource(self):
        return rpcservice.XmlRpcUsers(self)

    def getUsers(self):
        return defer.succeed(self.users.keys())

    def addUser(self, user):
        if not user in self.users:
            self.users[user] = []
            return defer.succeed([])
        else:
            return defer.succeed([])

    def removeUser(self, user):
        if not user in self.user:
            return defer.fail(user)
        else:
            del self.users[user]
            return defer.succeed(self.user.keys())
    
    def getWebPages(self, user):
        if user in self.users:
            print(str(self.users[user]))
            return defer.succeed(self.users[user])
        else:
            return defer.succeed([])

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
            
    def getWebPageContent(self, user, webpage):
        return defer.succeed(self.cache.cacheWebPage(webpage))

    def getWebPageDiff(self, user, webpage):
        return defer.succeed(self.cache.getDiffHtml(webpage))
