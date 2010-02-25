
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

        from consider.notifications import options, email, sms

        for user in self.users:
            for webPage in user.webPages:
                notificationOptions = user.webPages[webPage]
                log.msg(str(notificationOptions))
                notificationTypes = notificationOptions.getTypes()
                if options.NOTIFICATION_TYPE_EMAIL in notificationTypes:
                    log.msg('Notifying ' + user.name + ' about ' +
                            str(webPage) + ' through email ' + str(user.emailAddress))
                    emailNotification = email.EmailNotification()
                    emailNotification.setText('This is a test of this program. Please ignore this message')
                    emailNotification.setDestination([user.emailAddress])
                    emailNotification.username = 'consider.project@gmail.com'
                    emailNotification.password = ''
                    emailNotification.notify()
                if options.NOTIFICATION_TYPE_SMS in notificationTypes:
                    log.msg('Notifying ' + user.name + ' about ' +
                            str(webPage) + ' through sms')

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
        log.msg('REQUEST: removeUser(' +  str(username) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            log.msg('No such user')
            return defer.succeed([])
        else:
            del self.users[id]
            log.msg('Removed user')
            return defer.succeed([])

    def setEmailAddress(self, username, emailAddress):
        log.msg('REQUEST: setEmailAddress(' + str(username) +
                ', ' + str(emailAddress) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            log.msg('No such user')
            return defer.fail([])

        user = self.users[id]
        user.emailAddress = emailAddress
        return defer.succeed([])

    def getEmailAddress(self, username):
        log.msg('REQUEST: getEmailAddress(' + str(username) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            return defer.fail([])

        user = self.users[id]
        email = user.emailAddress
        log.msg('Returning: ' + email)
        return defer.succeed(email)
    
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

    def addWebPage(self, username, webPage, notificationTypes, frequency):
        log.msg('REQUEST: addWebPage(' + str(username) + ', ' + str(webPage) + 
                ', ' +  str(notificationTypes) + ', ' + str(frequency) +  ')')

        from consider.notifications import options

        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        webPages = {}
        notificationOptions = options.NotificationOptions()
        notificationOptions.setTypes(notificationTypes)
        notificationOptions.setFrequency(frequency)
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

    def getFrequency(self, username, webPage):
        log.msg('REQUEST: getFrequency(' + str(username) + ', ' + 
                str(webPage) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        if id == None:
            return defer.fail('user not found')

        if webPage not in self.users[id].webPages:
            return defer.fail('web page not found')

        frequency = self.users[id].webPages[webPage].getFrequency()
        log.msg('Returning ' + str(frequency))
        return frequency

    def getNewDiff(self, username, webPage):
        log.msg('REQUEST: getNewDiff(' + str(username) + ', ' + str(webPage) + ')')
        user = account.UserAccount(username)
        id = self._getIdForUser(user)
        user = self.users[id]
        entries = self.cache.getEntries(webPage)
        lastSeenEntry = user.webPages[webPage].getLastSeen()
        log.msg('last seen entry: ' + str(lastSeenEntry))
        if (lastSeenEntry == None) or (lastSeenEntry == '') or (not lastSeenEntry in entries):
            log.msg('last seen entry not found, no diff computed')
            if len(entries) > 0:
                user.webPages[webPage].setLastSeen(entries[0])
            return defer.succeed('')
        if not len(entries) > 1:
            log.msg('not enough entries cached to compute a diff')
            return defer.succeed('')
        # mark the web page as last seen now
        latestEntry = entries[0]
        user.webPages[webPage].setLastSeen(latestEntry)
        if latestEntry == lastSeenEntry:
            return defer.succeed('')
        log.msg('getting diff between ' + str(lastSeenEntry) + ' and ' + str(latestEntry))
        return defer.succeed(self.cache.getContentDiff(webPage, lastSeenEntry, latestEntry))

    def _getIdForUser(self, user):
        id = None;
        for i in range(0, len(self.users)):
            if self.users[i] == user:
                id = i
                break
        return id

