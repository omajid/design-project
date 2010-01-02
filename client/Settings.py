from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QDialog 
from PyQt4.QtGui import QLabel, QLineEdit, QPushButton
from PyQt4.QtGui import QGridLayout, QHBoxLayout

class SettingsController(object):
    def __init__(self):
        self._model = SettingsModel()
        self._view = SettingsView(self, self._model)

    def addWebsite(self, website):
        self._model.addWebsite(website)

    def removeWebsite(self, website):
        self._model.removeWebsite(website)

    def getModel(self):
        return self._model

    def show(self):
        self._view.show()


class SettingsModel(object):
    """
    Defines a model for the user's settings
    """

    def __init__(self):
        self.userSettingsDatabase = 'user.settings'
        self._loadSettings()

    def _loadSettings(self):
        self.username = 'Omair'
        self.password = 'test'
        self.observers = []
        self.websiteList = []
        import sqlite3
        connection = sqlite3.connect(self.userSettingsDatabase)
        try:
            cursor = connection.cursor()
            print('Reading database')
            rows = cursor.execute('''SELECT name, link FROM Websites''')
            for row in rows:
               self.websiteList.append((row[0], row[1]))
        except:
            print('Error reading database')
            pass

        # FIXME
        self._notifyObservers()

    def _saveSettings(self):
        import sqlite3

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
                name TEXT,
                link TEXT
                )''')
        except sqlite3.OperationalError:
            print('Table already exists')
        connection.commit()

        print('Storing entries')
        for name, link in self.websiteList:
            print('name: ' + str(name) + ' link: ' + str(link))
            t = (unicode(name), unicode(link))
            cursor.execute('INSERT INTO Websites (id, name, link) VALUES (NULL, ?, ?)', t)
        connection.commit()
        cursor.close()

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
        self._saveSettings()
        self._notifyObservers()

    def getPassword(self):
        return self.password

    def setPassword(self, password):
        self.password = password
        self._saveSettings()
        self._notifyObservers()

    def getWebsiteList(self):
        return self.websiteList

    def addWebsite(self, website):
        website = self._sanitizeWebsite(website)
        self.websiteList.append(website)
        self._saveSettings()
        self._notifyObservers()

    def _sanitizeWebsite(self, website):
        link = unicode(website[1])
        if (not link.startswith('http://') ) and (not link.startswith('https://')):
                link = 'http://' + link
        return (website[0], link)

    def containsWebsite(self, website):
        return website in self.websiteList

    def removeWebsite(self, website):
        self.websiteList.remove(website)
        self._saveSettings()
        self._notifyObservers()

class SettingsView(QDialog):
    def __init__(self, controller=None, model=None):
        super(QDialog, self).__init__(None)
        self.newWebsiteName = None
        self.newWebsiteLink = None
        self.controller = controller
        self.model = model
        self.model.addObserver(self)

    def notify(self):
        self.updateUi()

    def addNewWebsite(self):
        self.controller.addWebsite((self.newWebsiteName.text(), self.newWebsiteLink.text()))

    def removeWebsiteBuilder(self, website):
        def removeWebsite():
            storedWebsite = website
            self.controller.removeWebsite(website)
        return removeWebsite

    def addWebsiteListToLayout(self, gridLayout, staringRow):
        """Returns the next row that can be used in the grid layout"""
        websites = self.model.getWebsiteList()
        row = staringRow - 1;
        for (name, link) in websites:
            row = row + 1
            nameLineEdit = QLineEdit(name)
            gridLayout.addWidget(nameLineEdit, row, 0)
            linkLineEdit = QLineEdit(link)
            gridLayout.addWidget(linkLineEdit, row, 1)
            removeButton = QPushButton('Remove')
            self.connect(removeButton, SIGNAL('clicked()'), self.removeWebsiteBuilder((name,link)))
            gridLayout.addWidget(removeButton, row, 2)
        
        # add a blank line for adding new entries
        row = row + 1
        self.newWebsiteName = QLineEdit("<Name>")
        gridLayout.addWidget(self.newWebsiteName, row, 0)
        self.newWebsiteLink = QLineEdit("<Location>")
        gridLayout.addWidget(self.newWebsiteLink, row, 1)
        addButton = QPushButton("Add")
        self.connect(addButton, SIGNAL("clicked()"), self.addNewWebsite)
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
        row = self.addWebsiteListToLayout(layout, row)

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
        self.model._saveSettings()
        # call QDialog's accept() to close the window
        QDialog.accept(self)
