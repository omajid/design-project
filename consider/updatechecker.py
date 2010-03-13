import xmlrpclib

from PyQt4.QtGui import QApplication, QDialog, QTextEdit, QVBoxLayout, QLabel, \
                        QDialogButtonBox, QPushButton
from PyQt4.QtCore import QString, SIGNAL, QRect, QTimer

from consider.settings import Settings
from consider.notifications import options
from consider import debug

class UpdateCheckerController:
    '''This class is responsible for controlling the updater and the update notififer '''
    def __init__(self, application = None, systemTrayIcon = None, settingsModel = None):
        self._systemTrayIcon = systemTrayIcon
        self._application = application
        if settingsModel == None:
            settingsModel = Settings()
        self.settings = settingsModel
        self._model = UpdateCheckerModel(settingsModel)
        self._view = None

    def checkForUpdates(self, forced):
        return self._model.checkForUpdates(forced)

    def showNotification(self, webPages):
        self._view = UpdateCheckerView(self._application, self, self._model, self._systemTrayIcon)
        if self._view.isVisible():
            self._view.reject()
        self._view.show(webPages)

    def getWebPageDiff(self, webpage):
        diff = ''
        if webpage in self._model.diff:
            diff = self._model.diff[webpage]
        return diff

class UpdateCheckerModel:
    '''Maintains the update model.

    checks for and caches updates recieved from the server'''
    def __init__(self, settingsModel = None):
        self.cacheLocation = 'cache'
        if settingsModel:
            self.settings = settingsModel
        else:
            self.settings = Settings()
        # { webPage : diff }
        self.diff = {}

    def checkForUpdates(self, forced):
        from time import time

        if debug.verbose:
            print('DEBUG: Check for updates')

        oldDiff = self.diff
        self.diff = {}

        server = xmlrpclib.Server(self.settings.serverAddress)
        webPages = self.settings.getWebPages();
        webPagesToCheck = [ webPage for webPage in webPages
                    if options.NOTIFICATION_TYPE_CLIENT in self.settings.webPages[webPage].getNotificationTypes() ]
        for webPage in webPagesToCheck:
            if debug.verbose:
                print('DEBUG: last seen = ' + 
                        str(webPages[webPage].getLastSeenTimestamp(options.NOTIFICATION_TYPE_CLIENT)))
            lastSeen = webPages[webPage].getLastSeenTimestamp(options.NOTIFICATION_TYPE_CLIENT)
            frequency = webPages[webPage].getFrequency()
            if debug.verbose:
                print('DEBUG: frequency: ' + str(frequency))
            if lastSeen != None:
                # only check if we havent checked it for a while
                # finout out from user's options how much delay
                if (int(time()) - int(lastSeen)) <  options.getDelayForFrequency(frequency):
                    continue
            webPages[webPage].setLastSeenTimestamp(options.NOTIFICATION_TYPE_CLIENT, time())
            if debug.verbose:
                print('DEBUG: Checking ' + str(webPage))
            diff = server.getNewDiff(self.settings.username, webPage)
            if diff == None or diff == '':
                continue
            if debug.verbose:
                print('DEBUG: diff from server \n' +  diff)
            self.diff[webPage] = diff

        updatedWebPages = [ webPage for webPage in self.diff]

        # keep the older entries, but replace the newer entries 
        newDiff = self.diff
        self.diff = oldDiff
        for webPage in newDiff:
            self.diff[webPage] = newDiff[webPage]

        if debug.verbose:
            print('DEBUG: Done checking for updates')
        return updatedWebPages


class UpdateCheckerView(QDialog):
    '''Displays a small notification indicating new updates have been received'''
    def __init__(self, application, controller, model, systemTrayIcon, timeout = 10000):
        QDialog.__init__(self)
        self._application = application
        self._controller = controller
        self._model = model 
        self._systemTrayIcon = systemTrayIcon
        self.diffDialog = None
        self._timeout = timeout

    def _truncate(self, string, length = 40, suffix = '...'):
        if len(string) > length:
            string = string[:length] + suffix
        return string

    def show(self, webPages):
        settings = Settings()
        server = xmlrpclib.Server(settings.serverAddress)

        self.setWindowTitle('updates')

        layout = self.layout()
        if layout == None:
            layout = QVBoxLayout()

        label = QLabel('Some Web Pages have changed:')
        layout.addWidget(label)

        for webPage in webPages:
            label = QLabel('<a href=' + webPage + '>' + self._truncate(webPage) + '</a>' )
            label.setOpenExternalLinks(True)
            layout.addWidget(label)

        #buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        moreButton = QPushButton('More...')
        moreButton.setMaximumWidth(60)
        self.connect(moreButton, SIGNAL('clicked()'), self.showDiffWindow)
        layout.addWidget(moreButton)

        self.setLayout(layout)

        if debug.verbose:
            print('DEBUG: Showing notification dialog')
        QDialog.show(self)

        QTimer.singleShot(0, self.fixPosition)
        QTimer.singleShot(self._timeout, self.hide)

    def reject(self):
        QDialog.reject(self)
        for widget in self.children():
            widget.deleteLater()
        import sip
        sip.delete(self.layout())

    def showDiffWindow(self):
        from consider.updatedisplay import UpdateDisplayController
        if self.diffDialog == None:
            self.diffDialog = UpdateDisplayController(updateChecker = self._controller)
        self.diffDialog.show()

    def fixPosition(self):
        self.move(self._systemTrayIcon.geometry().x(), self._systemTrayIcon.geometry().y() - self.height() - 30)
        self.raise_()
        self.update()
