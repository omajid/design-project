from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QDialog 
from PyQt4.QtGui import QLabel, QLineEdit, QPushButton
from PyQt4.QtGui import QGridLayout, QHBoxLayout

import xmlrpclib
from consider import designpatterns


""" A MVC system for the settings dialog shown to the user

"""

class SettingsController(object):
    """ The controller in the MCV model for settings

    """
    def __init__(self):
        self._model = Settings()
        self._view = SettingsView(self, self._model)

    def addWebPage(self, webPage):
        self._model.addWebPage(webPage)

    def removeWebPage(self, webPage):
        self._model.removeWebPage(webPage)

    def getModel(self):
        return self._model

    def show(self):
        self._view.show()


class Settings(designpatterns.Borg):
    """ Defines a model for the user's settings

    """
    # Borg design pattern

    def __init__(self):
        # load state when the state of the first borg is initialized
        if 'username' not in self.__dict__:
            self.username = 'test'
            self.password = 'test'
            self.serverAddress = 'http://localhost:1055'
            self.observers = []
            self.webPageList = []

    def loadSettings(self):
        server = xmlrpclib.Server(self.serverAddress)
        pages = server.getWebPages(self.username)
        print('Settings from server:')
        print(str(pages))
        self.webPageList = []
        for page in pages:
            print(str(page))
            self.webPageList.append(page)
        
        self._notifyObservers()

    def saveSettings(self):
        server = xmlrpclib.Server(self.serverAddress)
        server.addUser(self.username)
        for webPage in self.webPageList:
            server.addWebPage(self.username, unicode(webPage))

    def getViewTitle(self):
        return 'Settings'

    def addObserver(self, observer):
        self.observers.append(observer)
        self._notifyObservers()

    def _notifyObservers(self):
        for observer in self.observers:
            observer.notify()

    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username
        self.saveSettings()
        self._notifyObservers()

    def getPassword(self):
        return self.password

    def setPassword(self, password):
        self.password = password
        self.saveSettings()
        self._notifyObservers()

    def getWebPageList(self):
        return self.webPageList

    def addWebPage(self, webPage):
        #webPage.sanitize() 
        self.webPageList.append(webPage)
        self.saveSettings()
        self._notifyObservers()

    def containsWebPage(self, webPage):
        return webPage in self.webPageList

    def removeWebPage(self, webPage):
        self.webPageList.remove(webPage)
        self.saveSettings()
        self._notifyObservers()

class SettingsView(QDialog):
    def __init__(self, controller=None, model=None):
        super(QDialog, self).__init__(None)
        self.newWebPageName = None
        self.newWebPageLink = None
        self.controller = controller
        self.model = model
        self.model.addObserver(self)

    def notify(self):
        self.updateUi()

    def addNewWebPage(self):
        webPage = self.newWebPageLink.text()
        self.controller.addWebPage(webPage)

    def removeWebPageBuilder(self, webPage):
        def removeWebPage():
            storedWebPage = webPage
            self.controller.removeWebPage(webPage)
        return removeWebPage

    def addWebPageListToLayout(self, gridLayout, staringRow):
        """Returns the next row that can be used in the grid layout"""
        webPages = self.model.getWebPageList()
        print(str(webPages))
        row = staringRow - 1;
        for webPage in webPages:
            print(str(webPage))
            row = row + 1
            nameLineEdit = QLineEdit('None')
            gridLayout.addWidget(nameLineEdit, row, 0)
            linkLineEdit = QLineEdit(webPage)
            gridLayout.addWidget(linkLineEdit, row, 1)
            removeButton = QPushButton('Remove')
            self.connect(removeButton, SIGNAL('clicked()'), self.removeWebPageBuilder((webPage)))
            gridLayout.addWidget(removeButton, row, 2)
        
        # add a blank line for adding new entries
        row = row + 1
        self.newWebPageName = QLineEdit("<Name>")
        gridLayout.addWidget(self.newWebPageName, row, 0)
        self.newWebPageLink = QLineEdit("<Location>")
        gridLayout.addWidget(self.newWebPageLink, row, 1)
        addButton = QPushButton("Add")
        self.connect(addButton, SIGNAL("clicked()"), self.addNewWebPage)
        gridLayout.addWidget(addButton, row, 2)
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
        spanTwoColumns = 2
        row = 0

        self.setWindowTitle(self.model.getViewTitle())
        layout = QGridLayout()
        usernameLabel = QLabel('Username:')
        layout.addWidget(usernameLabel, row, 0)
        usernameLineEdit = QLineEdit(self.model.getUsername())
        layout.addWidget(usernameLineEdit, row, 1, spanOneRow, spanTwoColumns)

        row = row + 1
        passwordLabel = QLabel('Password:')
        layout.addWidget(passwordLabel, row, 0)
        passwordLineEdit = QLineEdit(self.model.getPassword())
        layout.addWidget(passwordLineEdit, row, 1, spanOneRow, spanTwoColumns)
        
        row = row + 1
        row = self.addWebPageListToLayout(layout, row)

        okButton = QPushButton('OK')
        self.connect(okButton, SIGNAL('clicked()'), self.accept)
        cancelButton = QPushButton('Cancel')
        self.connect(cancelButton, SIGNAL('clicked()'), self, SLOT('reject()'))
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(buttonLayout, row, 1)

        self.setLayout(layout) 

    def accept(self):
        self.model.saveSettings()
        # call QDialog's accept() to close the window
        QDialog.accept(self)

    def reject(self):
        self.model.loadSettings()
        QDialog.reject(self)
