import StringIO

from OpenSSL.SSL import TLSv1_METHOD

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.ssl import ClientContextFactory
from twisted.mail.smtp import ESMTPSenderFactory
from twisted.python import log

class EmailNotification:
    def __init__(self, toAddresses = [], text = ''):
        self.username = ''
        self.password = ''
        self.fromAddress = 'consider.project@gmail.com'
        self.toAddresses = toAddresses
        self.text = text
        self.messageFile = StringIO.StringIO(text)

    def setDestination(self, emailAddresses):
        self.toAddresses = emailAddresses

    def setText(self, text):
        self.text = text
        self.messageFile = StringIO.StringIO(text)

    def notify(self):
        smtpHost = 'smtp.gmail.com'
        smtpPort = 587
        contextFactory = ClientContextFactory()

        contextFactory.method = TLSv1_METHOD

        def successCallback(result):
            log.msg('Sending email to ' + str(self.toAddresses) + ' suceeded')

        def errorCallback(result):
            log.err('Sending email to ' + str(self.toAddresses) + ' FAILED')
            log.err(str(result))

        resultDeferred = Deferred()
        resultDeferred.addCallback(successCallback)
        resultDeferred.addErrback(errorCallback)

        senderFactory = ESMTPSenderFactory(
                self.username,
                self.password,
                self.fromAddress,
                ' '.join(self.toAddresses),
                self.messageFile,
                resultDeferred,
                retries=2,
                timeout=10,
                contextFactory = contextFactory)

        reactor.connectTCP(smtpHost, smtpPort, senderFactory)

