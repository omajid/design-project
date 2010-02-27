import xmlrpclib

from PyQt4.QtGui import QApplication, QDialog, QTextEdit, QVBoxLayout, QLabel, \
                        QDialogButtonBox, QPushButton
from PyQt4.QtCore import QString, SIGNAL, QRect, QTimer

from consider.settings import Settings
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
        self._view = UpdateCheckerView(self._application, self, self._model, self._systemTrayIcon)

    def checkForUpdates(self, forced):
        return self._model.checkForUpdates(forced)

    def showNotification(self, webPages):
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
        if debug.verbose:
            print('DEBUG: Check for updates')

        self.diff = {}
        server = xmlrpclib.Server(self.settings.serverAddress)
        webPages = self.settings.getWebPages();
        webPages = [ webPage for webPage in webPages 
                    if 'client' in self.settings.webPages[webPage].getNotificationTypes() ]
        for webPage in webPages:
            if debug.verbose:
                print('DEBUG: Checking ' + str(webPage))
            diff = server.getNewDiff(self.settings.username, webPage)
            if diff == None or diff == '':
                continue
            if debug.verbose:
                print('DEBUG: diff from server \n' +  diff)
            self.diff[webPage] = diff

        updatedWebPages = [ webPage for webPage in self.diff]

        if debug.verbose:
            print('DEBUG: Done checking for updates')
        return updatedWebPages


class UpdateCheckerView(QDialog):
    '''Displays a small notification indicating new updates have been received'''
    def __init__(self, application, controller, model, systemTrayIcon):
        QDialog.__init__(self)
        self._application = application
        self._controller = controller
        self._model = model 
        self._systemTrayIcon = systemTrayIcon
        self.diffDialog = None

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
        moreButton = QPushButton('More')
        moreButton.setMaximumWidth(50)
        self.connect(moreButton, SIGNAL('clicked()'), self.showDiffWindow)
        layout.addWidget(moreButton)

        self.setLayout(layout)

        if debug.verbose:
            print('DEBUG: Showing notification dialog')
        QDialog.show(self)

        QTimer.singleShot(0, self.fixPosition)

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
