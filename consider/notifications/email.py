import StringIO

from twisted.internet.defer import Deferred
from twisted.internet.ssl import ClientContextFactory
from twisted.python import log

class EmailNotification:
    def __init__(self, toAddress = '', text = ''):
        self.username = ''
        self.password = ''
        self.fromAddress = 'Consider <consdier.project@gmail.com>'
        self.toAddress = emailAddress
        self.messageFile = StringIO.StringIO(text)

    def setDestination(self, emailAddress):
        self.emailAddress = emailAddress

    def setText(self, text):
        self.text = text
        self.messageFile = StringIO.StringIO(text)

    def notify(self):
        contextFactory = ContextFactory()

        contextFactory.method = SSLv3_METHOD

        def successCallback():
            log.msg('Sending email to ' + self.emailAddress ' + suceeded')

        def errorCallback():
            log.err('Sending email to ' + self.emailAddress ' + FAILED')

        resultDeferred = Deferred()
        resultDeferred.addCallback(successCallback)
        resultDeferred.addErrback(errorCallback)

        senderFactory = ESMTPSenderFactory(
                self.username,
                self.password,
                self.fromAddress,
                self.toAddress,
                self.messageFile,
                resultDeferred,
                contextFactory = contextFactory)

        reactor.connectTCP(smtpHost, smptPort, senderFactory)

