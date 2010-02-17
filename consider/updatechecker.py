import xmlrpclib
import os.path
import urllib2
import hashlib
import difflib
from subprocess import PIPE, Popen

from PyQt4.QtGui import QDialog, QTextEdit, QHBoxLayout
from PyQt4.QtCore import QString

from consider.settings import Settings
from consider import debug

class UpdateCheckerController:
    def __init__(self, systemTrayIcon = None, settingsModel = None):
        self._systemTrayIcon = systemTrayIcon
        if settingsModel == None:
            settingsModel = Settings()
            settingsModel.loadSettings()
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
    
    def checkForUpdates(self):
        import xmlrpclib
        settings = Settings()
        server = xmlrpclib.Server(settings.serverAddress)
        if debug.verbose:
            print('DEBUG: Check for updates')
        webPages = server.getWebPages(settings.username)
        for webPage in webPages:
            if debug.verbose:
                print('DEBUG: Checking ' + str(webPage))
            #self.cacheWebsite(webPage)
        if debug.verbose:
            print('DEBUG: Done checking for updates')
        return webPages


class UpdateCheckerView:
    def __init__(self, controller, model):
        self._controller = controller
        self._model = model 

    def show(self, webPage):
        settings = Settings()
        server = xmlrpclib.Server(settings.serverAddress)
        if debug.verbose:
            print('DEBUG: diff from server \n' +  server.getDiff(settings.username, webPage))
        return
        self.notificationDialog = QDialog()
        diffTextEdit = QTextEdit()
        htmlDiff = self._model.getDiffHtml(website)
        if debug.verbose:
            print(htmlDiff)
            print(type(htmlDiff))
        diffTextEdit.setHtml(QString(htmlDiff))
        simpleLayout = QHBoxLayout()
        simpleLayout.addWidget(diffTextEdit)
        self.notificationDialog.setLayout(simpleLayout)
        if debug.verbose:
            print('DEBUG: Showing notification dialog')
        self.notificationDialog.show()
