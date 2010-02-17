import hashlib
import sqlite3
import urllib2
import os.path

from twisted.python import log


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

    def getCacheContentsForDiff(self, website):
        import difflib
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
            return ('', '')

    def getUnifiedDiff(self, webPage):
        import difflib
        olderFileContents, latestFileContents = self.getCacheContentsForDiff(webPage)
        return ''.join(difflib.unified_diff(olderFileContents, latestFileContents))

    def getDiffHtml(self, webPage):
        import difflib
        olderFileContents, latestFileContents = self.getCacheContentsForDiff(webPage)
        diff = difflib.HtmlDiff()
        htmlDiff = diff.make_table(olderFileContents, latestFileContents)
        log.msg('Finished generating html diff')
        return htmlDiff

    def getContentDiff(self, webPage):
        import difflib
        from BeautifulSoup import BeautifulSoup
        #import html2text

        olderFileContents, latestFileContents = self.getCacheContentsForDiff(webPage)
        olderFileContents = ''.join(olderFileContents)
        latestFileContents = ''.join(latestFileContents)

        newSoup = BeautifulSoup(latestFileContents)
        oldSoup = BeautifulSoup(olderFileContents)

        tagsToStrip = ['script', 'style', 'menu']
        for currentTag in tagsToStrip:
            section_oldSoup = oldSoup.body.findAll(currentTag)
            [section_old.extract() for section_old in section_oldSoup]
            section_newSoup = newSoup.body.findAll(currentTag)
            [section_new.extract() for section_new in section_newSoup]

        oldSoupText = oldSoup.body(text = True)
        newSoupText = newSoup.body(text = True)
        
        ##oldSoupText = html2text.html2text(''.join(olderFileContents))
        ##newSoupText = html2text.html2text(''.join(latestFileContents))

        ##TODO: rewrite so that temp files not required
        ##oldSoupText = ''.join(oldSoupText.encode('utf-8'))
        ##newSoupText = ''.join(newSoupText.encode('utf-8'))

        oldSoupText = [line.strip() for line in oldSoupText if len(line.strip()) != 0]
        newSoupText = [line.strip() for line in newSoupText if len(line.strip()) != 0]

        fileOldText = open ('oldtext.txt', 'w')
        fileOldText.write('\n'.join(oldSoupText))
        fileOldText.close()
        fileNewText = open ('newtext.txt', 'w')
        fileNewText.write('\n'.join(newSoupText))
        fileNewText.close()

        ##newSoupText = [ line for line in open('newtext.txt')]
        ##oldSoupText = [ line for line in open('oldtext.txt')]

        diff_generator = difflib.unified_diff(oldSoupText, newSoupText, n = 0)
        diff = [line for line in diff_generator]
        diff = '\n'.join(diff)

        return diff
