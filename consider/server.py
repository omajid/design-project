
from twisted.application import service, internet
from twisted.internet import defer, task
from twisted.web import server
from twisted.python import log

from consider import rpcservice, storage, configuration, account

class MasterService(service.MultiService):
    def __init__(self):
        service.MultiService.__init__(self)
        serverConfig = configuration.ServerConfiguration()
        self.rpcServerPort = serverConfig.getPort()
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

        self.users = []
        self.cache = storage.WebPageCache()

        MINUTES = 60.0
        self.updater = task.LoopingCall(self.updateCache)
        self.updater.start(2 * MINUTES)

        self.notifier = task.LoopingCall(self.sendNotifications)
        self.notifier.start(4 * MINUTES)

    def updateCache(self):
        log.msg("MonitorService.updateCache(): started updating cache...");
        allWebPages = []
        for user in self.users:
            for webPage in user.webPages.keys():
                allWebPages.append(webPage)
        listOfUniqueWebPages = list(set(allWebPages))
        log.msg('Caching: '  + str(listOfUniqueWebPages))

        for webPage in listOfUniqueWebPages:
            self.cache.startCaching(webPage)

    def sendNotifications(self):
        log.msg("MonitorService.sendNotifications(): Sending out notifications");

    def getResource(self):
        return rpcservice.XmlRpcUsers(self)

    def getUsers(self):
        log.msg('REQUEST: getUsers')
        usernames = [ user.name for user in self.users]
        log.msg('Returning: ' + usernames)
        return defer.succeed(usernames)

    def addUser(self, username):
        log.msg('REQUEST: addUser(' + str(username) + ')' )
        user = account.UserAccount(username)
        if not user in self.users:
            log.msg('added user with no list of websites')
            self.users.append(user)
        else:
            log.msg('user already exists')
        return defer.succeed(user)

    def removeUser(self, username):
        log.msg('REQUEST: removeUser(' +  str(removeUser) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            log.msg('No such user')
            return defer.fail([])
        else:
            del self.users[id]
            log.msg('Removed user')
            return defer.succeed([])
    
    def getWebPages(self, username):
        log.msg('REQUEST: getWebPages(' + str(username) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            log.msg('No web pages found')
            return defer.succeed([])
        else:
            webPages = [webPage for webPage in self.users[id].webPages] 
            log.msg('Returning: ' + str(webPages))
            return defer.succeed(webPages)

    def addWebPage(self, username, webPage, notificationTypes):
        log.msg('REQUEST: addWebPage(' + str(username) + ', ' + str(webPage) + 
                ', ' +  str(notificationTypes) + ')')

        from consider.notifications import options

        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        webPages = {}
        notificationOptions = options.NotificationOptions()
        notificationOptions.setTypes(notificationTypes)
        if id == None:
            log.msg('Invalid user')
        else:
            webPages = self.users[id].webPages
            webPages[webPage] = notificationOptions
            self.cache.cacheWebPage(webPage)
            if not webPage in webPages:
                log.msg('Added web page')
            else:
                log.msg('web page already exists')
        return defer.succeed([])

    def removeWebPage(self, username, webPage):
        log.msg('REQUEST: removeWebPage(' + str(username) + ', ' + str(webPage) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            return defer.fail([])
        else:
            if webPage in self.users[id].webPages:
                self.users[id].remove(webPage)
                log.msg('Removed web page for user')
                return defer.succeed([])
            return defer.fail([])

    def getNotificationTypes(self, username, webPage):
        log.msg('REQUEST: getNotificationTypes(' + str(username) +
                ', ' + str(webPage) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            return defer.fail('user not found')

        if webPage not in self.users[id].webPages:
            return defer.fail('Web page not found')

        types = self.users[id].webPages[webPage].getTypes()
        log.msg('Returning: ' + str(types))
        return types
            
    def getWebPageContent(self, username, webPage):
        log.msg('REQUEST: getWebPageContent(' + str(username) + ', ' + str(webPage) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        return defer.succeed(self.cache.cacheWebPage(webPage))

    def getWebPageDiff(self, username, webPage):
        log.msg('REQUEST: getWebPageDiff')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        return defer.succeed(self.cache.getDiffHtml(webPage))

    def getDiff(self, username, webPage):
        log.msg('REQUEST: getDiff(' + str(username) + ', ' + str(webPage) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        return defer.succeed(self.cache.getUnifiedDiff(webPage))

    def _getIdForUser(self, user):
        id = None;
        for i in range(0, len(self.users)):
            if self.users[i] == user:
                id = i
                break
        return id

