from PyQt4.QtCore import SIGNAL, SLOT, QString
from PyQt4.QtGui import QMenu, QSystemTrayIcon, QApplication, QDialog, \
        QWidget, QGridLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, \
        QIcon
import sys, signal

from consider.settings import SettingsController, Settings, ConnectionError
from consider.updatechecker import UpdateCheckerController

verbose = 0 

def parseArguments(args):
    global verbose
    if '-v' in args:
        verbose = 1

class ClientApplication():
    """Creates the client application

    The application appears as an icon in the system tray, and allows the user
    to control is graphically.

    """
    def __init__(self, args=None):
        self.args = args

    def _buildMenu(self):
        menu = QMenu()
        self.forceCheckAction = menu.addAction('Force Check Now')
        self.application.connect(self.forceCheckAction, SIGNAL('triggered()'), \
                self._checkUpdates)
        self.settingsAction = menu.addAction('Settings')
        self.settingsAction.connect(self.settingsAction, \
                SIGNAL('triggered()'), self._showSettings)
        self.exitAction = menu.addAction('Exit')
        self.application.connect(self.exitAction, SIGNAL('triggered()'), \
                self.application, SLOT('quit()'))
        # XXX: need to keep a reference to the dialog
        # without a reference/parent it will be destroyed
        # yes, i wasted 5 hours on this!
        self.settingsDialog = None
        return menu

    def _checkUpdates(self):
        updateChecker = UpdateCheckerController(self.systemTrayIcon)
        websites = updateChecker.checkForUpdates()
        for website in websites:
            self.updateNotification = updateChecker.showNotificationForWebsite(website)

    def _showSettings(self):
        if verbose:
            print 'Showing settings (well, not really)'
        if self.settingsDialog == None:
            self.settingsDialog = SettingsController()
        self.settingsDialog.show()

    def showLoginWindow(self):
        self.loginWindow = LoginWindow(self)
        self.loginWindow.show()

    def startMainProgram(self):
        menu = self._buildMenu()
        from consider.configuration import ClientConfiguration
        clientConfiguration = ClientConfiguration()
        iconLocation = QString(clientConfiguration.getSystrayIcon())
        icon = QIcon(iconLocation)
        self.systemTrayMenu = menu
        self.systemTrayIcon = QSystemTrayIcon(icon)
        self.systemTrayIcon.setContextMenu(self.systemTrayMenu)
        self.systemTrayIcon.setToolTip('Web Notification Client')
        self.systemTrayIcon.show()

    def start(self):
        parseArguments(self.args)
        if verbose:
            print 'Starting client...'

        self.application = QApplication(self.args, True)
        self.application.setQuitOnLastWindowClosed(False)
        self.showLoginWindow()

        # allow exiting the application with ctrl-c
        # signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.application.exec_()

        if verbose:
            print 'Stoppping client...'


class LoginWindow(QDialog):
    def __init__(self, client=None):
        QDialog.__init__(self)
        self.client = client

    def accept(self):
        # FIXME authenticate with server here

        settings = Settings()
        try:
            settings.setUsername(str(self.usernameLineEdit.text()))
        except ConnectionError, e:
            self.statusLine.setText('Unable to connect to server')
            return

        QDialog.accept(self)
        self.client.startMainProgram()

    def reject(self):
        QDialog.reject(self)
        self.client.application.quit()

    def show(self):
        self.updateUi()
        QDialog.show(self)

    def updateUi(self):
        self.setWindowTitle('Login')

        spanOneRow = 1
        spanTwoColumns = 2
        row = 0

        layout = QGridLayout()
        usernameLabel = QLabel('Username:')
        layout.addWidget(usernameLabel, row, 0)
        self.usernameLineEdit = QLineEdit('<Username>')
        layout.addWidget(self.usernameLineEdit, row, 1, spanOneRow, spanTwoColumns)
        row = row + 1

        passwordLabel = QLabel('Password:')
        layout.addWidget(passwordLabel, row, 0)
        self.passwordLineEdit = QLineEdit('<Password>')
        layout.addWidget(self.passwordLineEdit, row, 1, spanOneRow, spanTwoColumns)
        row = row + 1

        okButton = QPushButton('OK')
        self.connect(okButton, SIGNAL('clicked()'), self.accept)
        cancelButton = QPushButton('Cancel')
        self.connect(cancelButton, SIGNAL('clicked()'), self.reject)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(buttonLayout, row, 1)
        row = row + 1

        self.statusLine = QLabel('')
        layout.addWidget(self.statusLine, row, 0, spanOneRow, 3)

        self.setLayout(layout)

