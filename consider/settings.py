from PyQt4.QtCore import SIGNAL, SLOT, QTimer, Qt
from PyQt4.QtGui import QDialog, QMessageBox, QDialogButtonBox, QLabel, \
    QLineEdit, QPushButton, QGridLayout, QHBoxLayout, QCheckBox, QSlider, \
    QSpinBox

import xmlrpclib
import socket

from consider import designpatterns
from consider.debug import verbose

""" A MVC system for the settings dialog shown to the user

"""

class SettingsController(object):
    """ The controller in the MCV model for settings

    """
    def __init__(self):
        self._model = Settings()
        self._view = SettingsView(self, self._model)

    def setEmailAddress(self, emailAddress):
        self._model.setEmailAddress(emailAddress)

    def addWebPage(self, webPage, options):
        self._model.addWebPage(webPage, options)

    def removeWebPage(self, webPage):
        self._model.removeWebPage(webPage)

    def getWebPageOptions(self, webPage):
        return self._model.getWebPageOptions(webPage)

    def setWebPageOptions(self, webPage, options):
        self._model.setWebPageOptions(webPage, options)

    def getModel(self):
        return self._model

    def show(self):
        self._view.show()


class Settings(designpatterns.Borg):
    """ Defines a model for the user's settings

    """

    def __init__(self):
        # load state when the state of the first borg is initialized
        if 'username' not in self.__dict__:
            from consider.configuration import ClientConfiguration
            clientConfiguration = ClientConfiguration()
            self.username = 'test'
            self.password = 'test'
            self.emailAddress = 'someone@somewhere'
            self.serverAddress = 'http://' + clientConfiguration.getServer()
            if verbose:
                print('DEBUG: Connecting to server: ' + self.serverAddress)
            self.observers = []
            # { webpage1 : options1, webpage2: options2 }
            self.webPages = {}
            self.loadSettings

    def loadSettings(self):
        if verbose:
            print('DEBUG: loading settings from the server')

        from consider.notifications import options

        server = xmlrpclib.Server(self.serverAddress)
        self.emailAddress = server.getEmailAddress(self.username)
        pages = server.getWebPages(self.username)
        self.webPages = {}
        # FIXME get the right notification options
        for page in pages:
            notificationOptions = options.NotificationOptions()
            notificationOptions.setTypes(server.getNotificationTypes(self.username, page))
            notificationOptions.setFrequency(server.getFrequency(self.username, page))
            notificationOptions.setWCThreshold(server.getWCThreshold(self.username, page))
            self.webPages[page] = notificationOptions
        
        self._notifyObservers()

    def saveSettings(self):
        if verbose:
            print('DEBUG: saving settings to the server')
        server = xmlrpclib.Server(self.serverAddress)
        server.removeUser(self.username)
        server.addUser(self.username)
        server.setEmailAddress(self.username, self.emailAddress)
        # FIXME
        for webPage in self.webPages:
            server.addWebPage(self.username, unicode(webPage), self.webPages[webPage].getNotificationTypes(), self.webPages[webPage].getFrequency(), self.webPages[webPage].getWCThreshold())

    def getViewTitle(self):
        return 'Settings for ' + self.username

    def addObserver(self, observer):
        self.observers.append(observer)
        self._notifyObservers()

    def _notifyObservers(self):
        for observer in self.observers:
            observer.notify()

    def getUsername(self):
        return self.username

    def _saveUser(self):
        if verbose:
            print('DEBUG: settings username with the server')
        server = xmlrpclib.Server(self.serverAddress)
        server.addUser(self.username)

    def setUsername(self, username):
        oldUsername = username
        try:
            self.username = username
            self._saveUser()
            self.loadSettings()
        except socket.gaierror, e:
            self.username = oldUsername
            raise ConnectionError()
        self._notifyObservers()

#    def getPassword(self):
#        return self.password
#
#    def setPassword(self, password):
#        self.password = password
#        self.saveSettings()
#        self._notifyObservers()

    def setEmailAddress(self, emailAddress):
        self.emailAddress = emailAddress
        if verbose:
            print('DEBUG: setting email address to: ' + str(self.emailAddress)) 
        self._notifyObservers()

    def getEmailAddress(self):
        return self.emailAddress

    def getWebPages(self):
        return self.webPages

    def addWebPage(self, webPage, options):
        '''Add a web page to the model

        raises httplib.InvalidURL if the web page is invalid'''

        webPage = self._cleanURL(webPage)

        self.webPages[webPage] = options
        self._notifyObservers()

    def _cleanURL(self, webPage):
        '''Cleans ands checks a url for reachability

        raises httplib.InvalidURL on error'''
        import httplib
        import urlparse

        webPage = webPage.lower()
        print('DEBUG: Settings._cleanURL(): checking url: ' + str(webPage))
        if not webPage.startswith('http://') and not webPage.startswith('https://'):
            webPage = 'http://' + webPage
        url = urlparse.urlparse(webPage)

        try:
            connection = httplib.HTTPConnection(url.netloc)
            connection.request('HEAD', url.path)
            #TODO: Doesn't work for some sites, replace with GET
            #also check response code
            response = connection.getresponse()
            return webPage
        except socket.gaierror, e:
            raise httplib.InvalidURL

    def getWebPageOptions(self, webPage):
        return self.webPages[webPage]

    def setWebPageOptions(self, webPage, options):
        self.webPages[webPage] = options

    def containsWebPage(self, webPage):
        return webPage in self.webPages

    def removeWebPage(self, webPage):
        del self.webPages[webPage]
        self._notifyObservers()

class SettingsView(QDialog):
    def __init__(self, controller=None, model=None):
        super(QDialog, self).__init__(None)
        self.setMinimumWidth(500)
        self.newWebPageName = None
        self.newWebPageLink = None
        self.controller = controller
        self.model = model
        self.model.addObserver(self)
        self.model.loadSettings()

    def notify(self):
        self.updateUi()

    def addNewWebPage(self):
        '''Add a web page to the settings model'''
        webPage = str(self.newWebPageLink.text())
        # update the model
        self.controller.setEmailAddress(str(self.emailLineEdit.text()))
        from consider.notifications import options
        notificationOptions = options.NotificationOptions()
        import httplib
        try:
            self.controller.addWebPage(webPage, notificationOptions)
        except httplib.InvalidURL, e:
            msg = QMessageBox.warning(self,
                    'Invalid URL',
                    'Unable to retrieve url, please check for typos')

    def removeWebPageBuilder(self, webPage):
        def removeWebPage():
            self.controller.setEmailAddress(str(self.emailLineEdit.text()))
            storedWebPage = webPage
            self.controller.removeWebPage(webPage)
        return removeWebPage

    def checkBoxHandlerBuilder(self, webPage, notificationTypeHandled):
        def function(checkStatus):
            notificationOptions = self.controller.getWebPageOptions(webPage)
            currentNotificationTypes = notificationOptions.getNotificationTypes()
            if checkStatus:
                if not notificationTypeHandled in currentNotificationTypes:
                    currentNotificationTypes.append(notificationTypeHandled)
                    notificationOptions.setTypes(currentNotificationTypes)
            else:
                if notificationTypeHandled in currentNotificationTypes:
                    optionTypes = [type for type in currentNotificationTypes 
                                    if not type == notificationTypeHandled]
                    notificationOptions.setTypes(optionTypes)
            if verbose:
                print('DEBUG: updated options: ' + str(notificationOptions))
        return function

    def sliderChangeBuilder(self, webPage):
        def function(value):
            self.controller.getWebPageOptions(webPage).setFrequency(value)
        return function

    def spinboxChangeBuilder(self, webPage):
        def function(value):
            self.controller.getWebPageOptions(webPage).setWCThreshold(value)
        return function

    def changeEmailCallback(self):
        if verbose:
            print('DEBUG: setting email address to : ' + self.emailLineEdit.text())
        self.controller.setEmailAddress(str(self.emailLineEdit.text()))

    def addWebPageListToLayout(self, gridLayout, startingRow):
        """Returns the next row that can be used in the grid layout"""

        from consider.notifications import options

        webPages = self.model.getWebPages()

        if verbose:
            print('DEBUG: current web pages: ' + str(webPages))
        row = startingRow

        webPageLabel = QLabel('WebPage:')
        gridLayout.addWidget(webPageLabel, row, 0, 1, 4)

        clientLabel = QLabel('Client')
        gridLayout.addWidget(clientLabel, row, 4)
        emailLabel = QLabel('Email')
        gridLayout.addWidget(emailLabel, row, 5)
        #smsLabel = QLabel('SMS')
        #gridLayout.addWidget(smsLabel, row, 6)
        frequencyLabel = QLabel('Frequency')
        gridLayout.addWidget(frequencyLabel, row, 7)
        minWordLabel = QLabel('Sensitivity')
        gridLayout.addWidget(minWordLabel, row, 8)

        for webPage in webPages:
            row = row + 1
            linkLineEdit = QLineEdit(webPage)
            gridLayout.addWidget(linkLineEdit, row, 0, 1, 4)

            clientCheck = QCheckBox()
            if options.NOTIFICATION_TYPE_CLIENT in webPages[webPage].getNotificationTypes():
                clientCheck.setChecked(1)
            self.connect(clientCheck,
                    SIGNAL('stateChanged(int)'),
                    self.checkBoxHandlerBuilder(webPage, options.NOTIFICATION_TYPE_CLIENT))
            gridLayout.addWidget(clientCheck, row, 4)

            emailCheck = QCheckBox()
            if options.NOTIFICATION_TYPE_EMAIL in webPages[webPage].getNotificationTypes():
                emailCheck.setChecked(1)
            self.connect(emailCheck,
                    SIGNAL('stateChanged(int)'),
                    self.checkBoxHandlerBuilder(webPage, options.NOTIFICATION_TYPE_EMAIL))
            gridLayout.addWidget(emailCheck, row, 5)

            #smsCheck = QCheckBox()
            #if options.NOTIFICATION_TYPE_SMS in webPages[webPage].getNotificationTypes():
            #    smsCheck.setChecked(1)
            #self.connect(smsCheck,
            #        SIGNAL('stateChanged(int)'),
            #        self.checkBoxHandlerBuilder(webPage, options.NOTIFICATION_TYPE_SMS))
            #gridLayout.addWidget(smsCheck, row, 6)

            frequencySlider = QSlider(Qt.Horizontal)
            frequencySlider.setTracking(False)
            frequencySlider.setMaximum(options.MAX_FREQUENCY)
            frequencySlider.setMinimum(options.MIN_FREQUENCY)
            frequencySlider.setValue(webPages[webPage].getFrequency())
            self.connect(frequencySlider, SIGNAL('valueChanged(int)'), self.sliderChangeBuilder(webPage) )
            gridLayout.addWidget(frequencySlider, row, 7)

            wordCountSpinBox = QSpinBox()
            wordCountSpinBox.setMinimum(options.MIN_WC_THRESHOLD)
            wordCountSpinBox.setMaximum(options.MAX_WC_THRESHOLD)
            wordCountSpinBox.setValue(webPages[webPage].getWCThreshold())
            self.connect(wordCountSpinBox, SIGNAL('valueChanged(int)'), self.spinboxChangeBuilder(webPage))
            gridLayout.addWidget(wordCountSpinBox, row, 8)

            removeButton = QPushButton('Remove')
            self.connect(removeButton, SIGNAL('clicked()'), self.removeWebPageBuilder((webPage)))
            gridLayout.addWidget(removeButton, row, 10)
        
        # add a blank line for adding new entries
        row = row + 1
        self.newWebPageLink = QLineEdit("<Location>")
        gridLayout.addWidget(self.newWebPageLink, row, 0, 1, 4)
        # FIXME
        #clientCheck = QCheckBox()
        #gridLayout.addWidget(clientCheck, row, 2)
        #emailCheck = QCheckBox()
        #gridLayout.addWidget(emailCheck, row, 3)
        #smsCheck = QCheckBox()
        #gridLayout.addWidget(smsCheck, row, 4)

        addButton = QPushButton("Add")
        self.connect(addButton, SIGNAL("clicked()"), self.addNewWebPage)
        gridLayout.addWidget(addButton, row, 10)
        return row+1

    def deleteLayouts(self, layout=None):
        if layout == None:
            layout = self.layout()
        if layout == None:
            return

        # a layout's children are the sublayouts
        for childLayout in layout.children():
            self.deleteLayouts(childLayout)

        import sip
        sip.delete(layout)

    def deleteWidgets(self, parent=None):
        if self.layout() is None:
            return

        if parent == None:
            parent = self

        # widgets belong to the parents, not the layout
        for widget in parent.children():
            widget.deleteLater()

    def updateUi(self):
        self.deleteWidgets()
        self.deleteLayouts()

        spanOneRow = 1
        row = 0

        self.setWindowTitle(self.model.getViewTitle())
        layout = QGridLayout()

        emailLabel = QLabel('Email:')
        layout.addWidget(emailLabel, row, 0)
        self.emailLineEdit = QLineEdit(self.model.getEmailAddress())
        # FIXME this would be a great feature to have
        #self.connect(self.emailLineEdit, SIGNAL('editingFinished()'), self.changeEmailCallback)
        layout.addWidget(self.emailLineEdit, row, 1, spanOneRow, 7)

        row = row + 1
        
        row = self.addWebPageListToLayout(layout, row)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok |
                QDialogButtonBox.Cancel)
        buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        self.connect(buttonBox, SIGNAL('accepted()'), self.accept)
        self.connect(buttonBox, SIGNAL('rejected()'), self, SLOT('reject()'))
        layout.addWidget(buttonBox, row, 0, spanOneRow, 11)

        self.setLayout(layout) 

    def accept(self):
        print('DEBUG: ok clicked')
        # close the dialog, but save settings later
        QTimer.singleShot(0, self.saveSettings)
        # call QDialog's accept() to close the window
        QDialog.accept(self)

    def saveSettings(self):
        print('DEBUG: gui triggered saving settings')
        self.changeEmailCallback()
        self.model.saveSettings()

    def reject(self):
        print('DEBUG: cancel clicked')
        QTimer.singleShot(0, self.loadSettings)
        QDialog.reject(self)

    def loadSettings(self):
        print('DEBUG: gui triggered loading settings')
        self.model.loadSettings()

class ConnectionError:
    pass
