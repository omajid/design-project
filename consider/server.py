
from twisted.application import service, internet
from twisted.internet import defer
from twisted.web import server
from twisted.python import log

from consider import rpcservice, storage

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
        log.msg('REQUEST: getUsers')
        log.msg('Returning: ' + str(self.users.keys()))
        return defer.succeed(self.users.keys())

    def addUser(self, user):
        log.msg('REQUEST: addUser(' + str(user) + ')' )
        if not user in self.users:
            log.msg('added user with no list of websites')
            self.users[user] = []
            return defer.succeed([])
        else:
            return defer.succeed([])

    def removeUser(self, user):
        log.msg('REQUEST: removeUser(' +  str(removeUser) + ')')
        if not user in self.user:
            log.msg('No such user')
            return defer.fail(user)
        else:
            del self.users[user]
            log.msg('Removed user')
            return defer.succeed(self.user.keys())
    
    def getWebPages(self, user):
        log.msg('REQUEST: getWebPages(' + str(user) + ')')
        if user in self.users:
            log.msg('Returning: ' + str(self.users[user]))
            return defer.succeed(self.users[user])
        else:
            return defer.succeed([])

    def addWebPage(self, user, webPage):
        log.msg('REQUEST: addWebPage(' + str(user) + ', ' + str(webPage) + ')')
        webPages = self.users[user]
        if not webPage in webPages:
            log.msg('Added web page')
            webPages.append(webPage)
        return defer.succeed(webPages)

    def removeWebPage(self, user, webPage):
        log.msg('REQUEST: removeWebPage(' + str(user) + ', ' + str(webPage) + ')')
        if user in self.users:
            if webPage in self.users[user]:
                self.users[user].remove(webPage)
                log.msg('Removed web page for user')
                return defer.succeed([])
            return defer.fail([])
        return defer.fail([])
            
    def getWebPageContent(self, user, webPage):
        log.msg('REQUEST: getWebPageContent(' + str(user) + ', ' + str(webPage) + ')')
        return defer.succeed(self.cache.cacheWebPage(webPage))

    def getWebPageDiff(self, user, webPage):
        log.msg('REQUEST: getWebPageDiff')
        log.msg('Returning: ' + str(self.users.keys()))
        return defer.succeed(self.cache.getDiffHtml(webPage))

    def getDiff(self, user, webPage):
        log.msg('REQUEST: getDiff(' + str(user) + ', ' + str(webPage) + ')')
        log.msg('Returning: ' + str(self.users.keys()))
        return defer.succeed(self.cache.getUnifiedDiff(webPage))

