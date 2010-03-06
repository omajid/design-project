import hashlib
import sqlite3
import os.path

from twisted.python import log
from consider import debug

class Settings:
    """ Stores settings for users

    """

    def __init__(self):
        self.__data = []
        self.userSettingsDatabase = 'user.settings'

    # FIXME switch to twisted's async db api
    def store(self):

        connection = sqlite3.connect(self.userSettingsDatabase)
        cursor = connection.cursor()
        print('Clearing previous entries')
        try:
            cursor.execute('''DROP TABLE Websites''')
        except:
            print('Error clearing previous entries')

        print('Creating table')
        try:
            cursor.execute('''CREATE TABLE Websites 
                (id INTEGER PRIMARY KEY ASC,
                user TEXT,
                url TEXT
                )''')
        except sqlite3.OperationalError:
            print('Table already exists')
        connection.commit()

        print('Storing entries')
        for user, webPage in self.data:
            print(str(webPage))
            t = (unicode(user), unicode(webPage))
            cursor.execute('INSERT INTO Websites (id, user, url) VALUES (NULL, ?, ?)', t)
        connection.commit()
        cursor.close()

    def load(self):
        connection = sqlite3.connect(self.userSettingsDatabase)
        try:
            cursor = connection.cursor()
            print('Reading database')
            rows = cursor.execute('''SELECT user, link FROM Websites''')
            for row in rows:
                webPage = row[1]
                user = row[0]
                self.data.append((user, webPage))
        except:
            print('Error reading database')


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
        print('Cache location for ' + webPage + ' is ' + cacheLocation)
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
        downloadPage (webPage, open(cacheLocation, 'w'))

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

    def _extractTextFromHtml(self, content):
        from BeautifulSoup import BeautifulSoup
       
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

        processedContent = soup.body(text = True)
        return processedContent

    def _removeBlanks(self, content):
        processedContent = [line.strip() for line in content if len(line.strip()) != 0]
        return processedContent

    def _processInputText(self, content):
        processedContent = content
        processedContent = self._extractTextFromHtml(processedContent)
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
            print (numWords)
            if numWords < minCount:
                lineRange = range(pair[0], pair[1]+1)
                lineRange.reverse()
                for lineToRemove in lineRange:
                    filteredResult.pop(lineToRemove)

        lastLine = filteredResult.pop()
        if lastLine != self.separator :
            filteredResult += lastLine

        return filteredResult


    def _processOutputText(self, content):
        processedOutput = content
        processedOutput = self._extractNewItems(processedOutput)
        processedOutput = self._minWordCountFilter(processedOutput, 2)
        return processedOutput

    def getContentDiff(self, webPage, olderEntry, newerEntry):
        '''returns a tuple (content, last entry seen)'''
        import difflib
        from textwrap import TextWrapper

        #olderFileContents, latestFileContents = self.getCacheContentsForDiff(webPage)
        olderFileContents = self.getContentsForEntry(webPage, olderEntry)
        latestFileContents = self.getContentsForEntry(webPage, newerEntry)

        processedOldContent = self._processInputText(olderFileContents)
        processedNewContent = self._processInputText(latestFileContents)

        #TODO: Remove debug outputs
        fileOldText = open ('oldtext.txt', 'w')
        fileOldText.write('\n'.join(processedOldContent))
        fileOldText.close()
        fileNewText = open ('newtext.txt', 'w')
        fileNewText.write('\n'.join(processedNewContent))
        fileNewText.close()

        diff_generator = difflib.unified_diff(processedOldContent, processedNewContent, n = 0)
        diff = [line for line in diff_generator]
        processedDiff = self._processOutputText(diff)
        processedDiff = '\n'.join(processedDiff)

        return processedDiff
