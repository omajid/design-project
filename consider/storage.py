import hashlib
import sqlite3
import os.path

from twisted.python import log

from consider import debug
from consider.notifications import options

class UserSettingsStorage:
    """ Stores settings for users

    """

    def __init__(self):
        self.__data = []
        self.userSettingsDatabase = 'user.settings'
        self._userTable = 'users'
        self._webPagesTable = 'webpages'

    # FIXME switch to twisted's async db api
    def store(self, users):
        '''store information on users in a database'''

        connection = sqlite3.connect(self.userSettingsDatabase)
        cursor = connection.cursor()
        log.msg('UserSettingsStorage.store(): Clearing previous entries')
        try:
            cursor.execute('DROP TABLE ' + self._webPagesTable)
        except sqlite3.OperationalError:
            log.msg('Error clearing previous entries')

        log.msg('UserSettingsStorage.store(): Creating users table')
        try:
            cursor.execute('''CREATE TABLE ''' + self._userTable + ''' 
                (id INTEGER PRIMARY KEY ASC,
                user TEXT,
                password TEXT,
                email TEXT
                )''')
        except sqlite3.OperationalError:
            log.msg('UserSettingsStorage.store(): Table already exists')

        log.msg('UserSettingsStorage.store(): Creating webpages table')
        try:
            cursor.execute('''CREATE TABLE ''' + self._webPagesTable + ''' 
                (id INTEGER PRIMARY KEY ASC,
                userId INTEGER,
                webPage TEXT,
                notifyClient INTEGER,
                notifyEmail INTEGER,
                notifySms INTEGER,
                frequency INTEGER
                )''')
        except sqlite3.OperationalError:
            log.msg('UserSettingsStorage.store(): Table already exists')

        log.msg('UserSettingsStorage.store(): Storing entries')
        try:
            for user in users:
                t = (unicode(user.name), unicode(user.password), user.emailAddress)
                cursor.execute('INSERT INTO ' + self._userTable + ' (id, user, password, email) VALUES (NULL, ?, ?, ?)', t)
                t = (unicode(user.name),)
                result = cursor.execute('SELECT * FROM ' + self._userTable + ' WHERE user=?', t)
                userId = result.fetchone()[0]
                for webPage in user.webPages:
                    notificationOptions = user.webPages[webPage]
                    notifyClient = options.NOTIFICATION_TYPE_CLIENT in notificationOptions.getNotificationTypes()
                    notifyEmail = options.NOTIFICATION_TYPE_EMAIL in notificationOptions.getNotificationTypes()
                    notifySms = options.NOTIFICATION_TYPE_SMS in notificationOptions.getNotificationTypes()
                    t = (userId, unicode(webPage), notifyClient, notifyEmail, notifySms, notificationOptions.getFrequency())
                    cursor.execute('INSERT INTO ' + self._webPagesTable + ' ' +
                            '(id, userId, webPage, notifyClient, notifyEmail, notifySms, frequency)' + 
                            ' ' + 'VALUES (NULL, ?, ?, ?, ?, ?, ?)', t)
            connection.commit()
            log.msg('UserSettingsStorage.store(): all user settings saved')
        except sqlite3.OperationalError, e:
            log.msg('UserSettingsStorage.store(): error saving user settings' + str(e))
        finally:
            cursor.close()

    def load(self):
        ''' returns a list of user objects ready to be used'''

        from consider import account

        connection = sqlite3.connect(self.userSettingsDatabase)
        users = []
        try:
            cursor = connection.cursor()
            log.msg('UserSettingsStorage.store(): Reading database')
            rows = cursor.execute('SELECT * FROM ' + self._userTable)

            for row in rows: 
                # (id, user, password, email)
                user = account.UserAccount()
                userId = row[0]
                user.name = row[1]
                user.password = row[2]
                user.emailAddress = row[3]

                webPageRows = cursor.execute('SELECT * FROM ' + self._webPagesTable + ' WHERE userId=?', (userId,))
                for webPageRow in webPageRows:
                    # (id, userId, webPage, notifyClient, notifyEmail, notifySms, frequency)
                    notificationOptions = options.NotificationOptions()
                    notificationTypes = []
                    webPage = str(webPageRow[2])
                    if (webPageRow[3] != 0):
                        notificationTypes.append(options.NOTIFICATION_TYPE_CLIENT)
                    if (webPageRow[4] != 0):
                        notificationTypes.append(options.NOTIFICATION_TYPE_EMAIL)
                    if (webPageRow[5] != 0):
                        notificationTypes.append(options.NOTIFICATION_TYPE_SMS)
                    notificationOptions.setTypes(notificationTypes)
                    notificationOptions.setFrequency(webPageRow[6])
                    user.webPages[webPage] = notificationOptions
                users.append(user)
        except sqlite3.OperationalError, e:
            log.msg('UserSettingsStorage.store(): Error reading database: ' + str(e))
        return users


class WebPageCache:
    """Caches web pages on disk

    """

    def __init__(self):
        log.msg('initializing !!! WebPageCache !!!')
        self.cacheLocation = 'cache'
        path = os.path.join('./' + self.cacheLocation)
        
        #self.separator = '\nNEXT ADDITION\n'
        self.separator = '-'*25

        try:
            log.msg('WebPageCache.__init__(): creating cache dir: ' + path)
            os.makedirs(path)
        except OSError:
            pass    # directory already exists
                    # FIXME or can not be created

    def clean(self):
        # FIXME implement cleaning the cache
        pass

    def _getCacheLocation(self, link):
        m = hashlib.md5()
        m.update(link)
        cacheLocation =  m.hexdigest() + '/'
        location = os.path.join(self.cacheLocation, cacheLocation)
        log.msg('WebPageCache._getCacheLocation: ' + str(link) + ' -> ' + str(location))
        return location

    def cacheWebPage(self, webPage):
        if debug.noUpdateCache:
            return

        import datetime
        from BeautifulSoup import BeautifulSoup
        from twisted.web.client import downloadPage

        log.msg('WebPageCache.cacheWebPage(): caching webPage' + str(webPage))
        #data = urllib2.urlopen(webPage)
        cacheLocation = str(self._getCacheLocation(webPage))
        log.msg('Cache location for ' + webPage + ' is ' + cacheLocation)
        if not os.path.isdir(cacheLocation):
            dir = os.makedirs(cacheLocation)
        cacheLocation = os.path.join(cacheLocation, str(datetime.datetime.now().isoformat()))
        #file = open(cacheLocation, 'w') 
        #rawData = data.read()
        ##soup = BeautifulSoup(rawData)
        ##processedData = rawData
        ##processedData = soup.prettify()
        #file.write(processedData)
        #file.close()
        webPage = str(webPage)
        downloadPage (webPage, open( str(cacheLocation), 'w'))

        log.msg('WebPageCache.cacheWebPage(): cached ' + str(webPage) + ' at ' + os.path.abspath(cacheLocation))
        return

    def startCaching(self, webPage):
        from twisted.internet import reactor
        reactor.callLater(0, self.cacheWebPage, webPage)

    def getEntries(self, webPage):
        '''Returns a list of cache entries for this webpage'''
        cacheLocation = self._getCacheLocation(webPage)
        entries = os.listdir(cacheLocation)
        entries.sort(reverse=True)
        log.msg('WebPageCache.getCacheEntries(): caching entries are ' + str(entries))
        return entries

    def getContentsForEntry(self, webPage, entry):
        cacheLocation = self._getCacheLocation(webPage)
        path = os.path.join(cacheLocation, entry)
        contents = [ line for line in open(path)]
        return contents

    def getContentsForDiff(self, website):
        address = website
        cacheLocation = self._getCacheLocation(address)
        log.msg('Diffing:' + cacheLocation)
        listOfFiles = os.listdir(self._getCacheLocation(address))
        listOfFiles.sort(reverse=True) 
        try:
            latestFile = os.path.join(cacheLocation, listOfFiles[0])
            olderFile = os.path.join(cacheLocation, listOfFiles[1])
            latestFileContents = [ line for line in open(latestFile)]
            olderFileContents = [ line for line in open(olderFile)]
            return (olderFileContents, latestFileContents)
        except IndexError:
            # no older file found; no diff
            return ([''], [''])

    def _extractTextFromHtml(self, content, webPage):
        from BeautifulSoup import BeautifulSoup
        import re
        import urlparse

        from consider.rules import inputrules

        unprocessedSoup = BeautifulSoup(''.join(content))

        soup = BeautifulSoup(unprocessedSoup.prettify())
        
        tagsToStrip = ['script', 'style', 'menu']
        for currentTag in tagsToStrip:
            junkTags = soup.body.findAll(currentTag)
            [junkSection.extract() for junkSection in junkTags]
        
        stylesToStrip = ['display:none', 'display: none']
        for currentStyle in stylesToStrip:
            junk = soup.body.findAll(style=currentStyle)
            [junkSection.extract() for junkSection in junk]

        hostname = urlparse.urlparse(webPage).hostname
        for rule in inputrules.nameRules: 
            result = re.search(rule, hostname)
            if result:
                soup = inputrules.nameRules[rule](soup)

        processedContent = soup.body(text = True)
        return processedContent

    def _removeBlanks(self, content):
        processedContent = [line.strip() for line in content if len(line.strip()) != 0]
        return processedContent

    def _processInputText(self, content, webPage):
        processedContent = content
        processedContent = self._extractTextFromHtml(processedContent, webPage)
        processedContent = self._removeBlanks(processedContent)

        return processedContent

    def _extractNewItems(self, content):
        from textwrap import TextWrapper

        additions = []
        skipLines = 0
        for line in content:
            skipLines = skipLines+1
            if line[0]=='@':
                break
        
        linesAdded = 0
        for line in content[skipLines:]:
            if line[0]=='+':
                additions += [line[1:]]
                linesAdded += 1
            if line[0]=='@':
                if linesAdded:
                    additions += [self.separator]
                linesAdded = 0
        
        #wrapper = TextWrapper()
        #wrapper.width = 80
        #wrapper.replace_whitespace = False
        #additions = wrapper.wrap('\n'.join(additions))
        
        return additions

    def _minWordCountFilter(self, content, minCount = 1):
        #requires _extractNewItems to be run on content before being passed to this function

        if not content:
            return content

        firstLineNum = 0
        currentLineNum = 0
        changePairs = []
        separatorLocations = []

        for line in content:
            if line == self.separator:
                changePairs += [[firstLineNum, currentLineNum]]
                firstLineNum = currentLineNum + 1
            currentLineNum += 1
        changePairs += [[firstLineNum, currentLineNum]]
        changePairs.reverse()

        filteredResult = content
        filteredResult += [self.separator]
        for pair in changePairs:
            currentAdd = ' '.join(filteredResult[pair[0]:pair[1]])
            numWords = len(currentAdd.split())
            if numWords < minCount:
                lineRange = range(pair[0], pair[1]+1)
                lineRange.reverse()
                for lineToRemove in lineRange:
                    filteredResult.pop(lineToRemove)

        lastLine = filteredResult.pop()
        if lastLine != self.separator :
            filteredResult += lastLine

        return filteredResult

    def _processOutputText(self, content, wcThreshold):
        processedOutput = content
        processedOutput = self._extractNewItems(processedOutput)
        processedOutput = self._minWordCountFilter(processedOutput, wcThreshold)
        return processedOutput

    def getContentDiff(self, webPage, olderEntry, newerEntry, wcThreshold):
        '''returns a tuple (content, last entry seen)'''
        
        import difflib
        from textwrap import TextWrapper

        #olderFileContents, latestFileContents = self.getCacheContentsForDiff(webPage)
        olderFileContents = self.getContentsForEntry(webPage, olderEntry)
        latestFileContents = self.getContentsForEntry(webPage, newerEntry)

        processedOldContent = self._processInputText(olderFileContents, webPage)
        processedNewContent = self._processInputText(latestFileContents, webPage)

        if debug.verbose:
            fileOldText = open ('oldtext.txt', 'w')
            fileOldText.write('\n'.join(processedOldContent))
            fileOldText.close()
            fileNewText = open ('newtext.txt', 'w')
            fileNewText.write('\n'.join(processedNewContent))
            fileNewText.close()

        diff_generator = difflib.unified_diff(processedOldContent, processedNewContent, n = 0)
        diff = [line for line in diff_generator]
        processedDiff = self._processOutputText(diff, wcThreshold)
        processedDiff = '\n'.join(processedDiff)

        return processedDiff
