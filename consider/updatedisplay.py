import xmlrpclib

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from consider.settings import Settings
from consider.updatechecker import UpdateCheckerController

class UpdateDisplayController:
    def __init__ (self, settingsModel = None, updateChecker = None):
        if settingsModel == None:
            settingsModel = Settings()
        self._model = UpdateDisplayModel(settingsModel, updateChecker)
        self._view = UpdateDisplayView(self._model)

    def show (self):
        self._view.show()
        self._view.updateUi()

class UpdateDisplayModel:
    def __init__ (self, settingsModel = None, updateChecker = None):
        self.settingsModel = settingsModel
        self.updateChecker = updateChecker

    def getUserWebpages (self):
        server = xmlrpclib.Server(self.settingsModel.serverAddress)
        webPages = server.getWebPages(self.settingsModel.username)
        return webPages

    def getDiff (self, webpage):
        diff = self.updateChecker.getWebPageDiff(str(webpage))
        return diff

class UpdateDisplayView(QDialog):
    def __init__ (self, model):
        super(UpdateDisplayView, self).__init__(None)
        self._model = model
        self.webpages = self._model.getUserWebpages()

        self.webpageComboBox = QComboBox()
        self.webpageComboBox.addItems(self.webpages)
        self.diffDisplay = QTextBrowser()
        self.refreshButton = QPushButton()
        self.refreshButton.setText('&Refresh')

        headerLayout = QHBoxLayout()
        headerLayout.addWidget(self.webpageComboBox, 1)
        headerLayout.addWidget(self.refreshButton)

        layout = QVBoxLayout()
        layout.addLayout(headerLayout)
        layout.addWidget(self.diffDisplay)
        self.setLayout(layout)
        self.connect(self.webpageComboBox, SIGNAL('currentIndexChanged(int)'), self.updateUi)
        self.connect(self.refreshButton, SIGNAL('clicked()'), self.updateUi)
        self.updateUi()

    def updateUi (self):
        selectedWebpage = self.webpageComboBox.currentText()
        print ('DEBUG: Updating UI with diff for ' + selectedWebpage )
        self.updateDiffDisplay (selectedWebpage)

    def updateDiffDisplay (self, webpage):
        diffText = self._model.getDiff(webpage)
        self.diffDisplay.setPlainText(diffText)

