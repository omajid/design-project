import xmlrpclib

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from consider.settings import Settings

class UpdateDisplayController:
    def __init__ (self, settingsModel = None):
        if settingsModel == None:
            settingsModel = Settings()
            settingsModel.loadSettings()
        self._model = UpdateDisplayModel(settingsModel)
        self._view = UpdateDisplayView(self._model)

    def show (self):
        self._view.show()

class UpdateDisplayModel:
    def __init__ (self, settingsModel = None):
        self.settingsModel = settingsModel

    def getUserWebpages (self):
        server = xmlrpclib.Server(self.settingsModel.serverAddress)
        webPages = server.getWebPages(self.settingsModel.username)
        return webPages

    def getDiff (self, webpage):
        server = xmlrpclib.Server(self.settingsModel.serverAddress)
        return server.getDiff(self.settingsModel.username, webpage)

class UpdateDisplayView(QDialog):
    def __init__ (self, model):
        super(UpdateDisplayView, self).__init__(None)
        self._model = model
        self.webpages = self._model.getUserWebpages()

        self.webpageComboBox = QComboBox()
        #for webpage in self.webpages :
        self.webpageComboBox.addItems(self.webpages)
        self.diffDisplay = QTextBrowser()

        layout = QVBoxLayout()
        layout.addWidget(self.webpageComboBox)
        layout.addWidget(self.diffDisplay)
        self.setLayout(layout)
        #TODO:Connect signals for combobox selection
        self.connect(self.webpageComboBox, SIGNAL("currentIndexChanged(int)"), self.updateUi)

    def updateUi (self):
        selectedWebpage = self.webpageComboBox.currentText()
        self.updateDiffDisplay (selectedWebpage)

    def updateDiffDisplay (self, webpage):
        diffText = self._model.getDiff(webpage)
        self.diffDisplay.setPlainText(diffText)

