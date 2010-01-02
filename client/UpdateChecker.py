from Settings import SettingsModel
import os.path
import urllib2
import hashlib
import difflib
from subprocess import PIPE, Popen
from PyQt4.QtGui import QDialog, QTextEdit, QHBoxLayout
from PyQt4.QtCore import QString

class UpdateCheckerController:
    def __init__(self, systemTrayIcon = None, settingsModel = None):
        self._systemTrayIcon = systemTrayIcon
        if settingsModel == None:
            settingsModel = SettingsModel()
            settingsModel._loadSettings()
        self._model = UpdateCheckerModel(settingsModel)
        self._view = UpdateCheckerView(self, self._model)

    def checkForUpdates(self):
        return self._model.checkForUpdates()

    def showNotificationForWebsite(self, website):
        self._view.show(website)

class UpdateCheckerModel:
    def __init__(self, settingsModel = None):
        self.cacheLocation = 'cache'
        self.settingsModel = settingsModel

    def _getCacheLocation(self, link):
        m = hashlib.md5()
        m.update(link)
        cacheLocation =  m.hexdigest() + '/'
        return os.path.join(self.cacheLocation, cacheLocation)

    def cacheWebsite(self, website):
        import datetime
        print ('caching website' + str(website))
        address = website[1]
        data = urllib2.urlopen(address)
        cacheLocation = str(self._getCacheLocation(address))
        print('Cache location for ' + address + ' is ' + cacheLocation)
        if not os.path.isdir(cacheLocation):
            dir = os.makedirs(cacheLocation)
        cacheLocation = os.path.join(cacheLocation, str(datetime.datetime.now().isoformat()))
        file = open(cacheLocation, 'w') 
        file.write(data.read())
        file.close()
        print('cached ' + str(website) + ' at ' + os.path.abspath(cacheLocation))
    
    def checkForUpdates(self):
        print('Check for updates')
        for website in self.settingsModel.getWebsiteList():
            print('Checking ' + str(website))
            self.cacheWebsite(website)
        print('Done checking for updates')
        return self.settingsModel.getWebsiteList()

    def getDiffHtml(self, website):
        address = website[1]
        cacheLocation = self._getCacheLocation(address)
        print('Diffing:' + cacheLocation)
        listOfFiles = os.listdir(self._getCacheLocation(address))
        listOfFiles.sort(reverse=True) 
        latestFile = os.path.join(cacheLocation, listOfFiles[0])
        olderFile = os.path.join(cacheLocation, listOfFiles[1])
        latestFileContents = [ line for line in open(latestFile)]
        olderFileContents = [ line for line in open(olderFile)]
        print('Diffing: ' + str(olderFile) + ' and ' + str(latestFile))
        diff = difflib.HtmlDiff()
        htmlDiff = diff.make_table(olderFileContents, latestFileContents)
        print type(htmlDiff)
        print('Finished generating html diff')
        return htmlDiff

class UpdateCheckerView:
    def __init__(self, controller, model):
        self._controller = controller
        self._model = model 

    def show(self, website):
        self.notificationDialog = QDialog()
        diffTextEdit = QTextEdit()
        htmlDiff = self._model.getDiffHtml(website)
        print(htmlDiff)
        print(type(htmlDiff))
        diffTextEdit.setHtml(QString(htmlDiff))
        simpleLayout = QHBoxLayout()
        simpleLayout.addWidget(diffTextEdit)
        self.notificationDialog.setLayout(simpleLayout)
        print('Showing notification dialog')
        self.notificationDialog.show()
