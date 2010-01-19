import hashlib
import sqlite3
import urllib2
import os.path


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
        self.cacheLocation = 'cache'

    def clean(self):
        # FIXME implement cleaning the cache
        pass

    def _getCacheLocation(self, link):
        m = hashlib.md5()
        m.update(link)
        cacheLocation =  m.hexdigest() + '/'
        return os.path.join(self.cacheLocation, cacheLocation)

    def cacheWebPage(self, webPage):
        import datetime
        print ('caching webPage' + str(webPage))
        data = urllib2.urlopen(webPage.url)
        cacheLocation = str(self._getCacheLocation(webPage.url))
        print('Cache location for ' + address + ' is ' + cacheLocation)
        if not os.path.isdir(cacheLocation):
            dir = os.makedirs(cacheLocation)
        cacheLocation = os.path.join(cacheLocation, str(datetime.datetime.now().isoformat()))
        file = open(cacheLocation, 'w') 
        rawData = data.read()
        file.write(rawData)
        file.close()
        print('cached ' + str(webPage) + ' at ' + os.path.abspath(cacheLocation))
        return rawData

    def getCacheContentsForDiff(self, webPage):
        address = webPage
        cacheLocation = self._getCacheLocation(address)
        print('Diffing:' + cacheLocation)
        listOfFiles = os.listdir(self._getCacheLocation(address))
        listOfFiles.sort(reverse=True) 
        latestFile = os.path.join(cacheLocation, listOfFiles[0])
        olderFile = os.path.join(cacheLocation, listOfFiles[1])
        latestFileContents = [ line for line in open(latestFile)]
        olderFileContents = [ line for line in open(olderFile)]
        return (olderFileContents, latestFileContents)

    def getUnifiedDiff(self, webPage):
        olderFileContents, latestFileContents = self.getCacheContentsForDiff(webPage)
        return ''.join(difflib.unified_diff(olderFileConents, latestFileContents))

    def getDiffHtml(self, webPage):
        olderFileContents, latestFileContents = self.getCacheContentsForDiff(webPage)
        diff = difflib.HtmlDiff()
        htmlDiff = diff.make_table(olderFileContents, latestFileContents)
        print type(htmlDiff)
        print('Finished generating html diff')
        return htmlDiff
