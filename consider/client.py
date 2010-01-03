
import sys, signal
from settings import SettingsController
from updatechecker import UpdateCheckerController
from PyQt4.QtCore import SIGNAL, SLOT
from PyQt4.QtGui import QMenu, QSystemTrayIcon, QApplication, QDialog, QWidget

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

    def start(self):
        parseArguments(self.args)
        if verbose:
            print 'Starting client...'

        self.application = QApplication(self.args, True)
        self.application.setQuitOnLastWindowClosed(False)

        # allow exiting the application with ctrl-c
        # signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.systemTrayIcon = QSystemTrayIcon()
        self.systemTrayIcon.setToolTip('Web Notification Client')
        menu = self._buildMenu()
        self.systemTrayIcon.setContextMenu(menu)
        self.systemTrayIcon.show()

        self.application.exec_()

        if verbose:
            print 'Stoppping client...'

