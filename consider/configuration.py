
import designpatterns

class ClientConfiguration(designpatterns.Borg):

    CLIENT_CONFIG_NAME = 'client.conf'

    def __init__(self):
        if not 'server' in self.__dict__:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read(ClientConfiguration.CLIENT_CONFIG_NAME)
            self.server = config.get('main', 'server')
            self.username = config.get('main', 'username')

    def getServer(self):
        return self.server

    def getUsername(self):
        return self.username


class ServerConfiguration(designpatterns.Borg):

    SERVER_CONFIG_NAME = 'server.conf'

    def __init__(self):
        if not 'port' in self.__dict__:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read(ServerConfiguration.SERVER_CONFIG_NAME)
            self.port = config.getint('main', 'port')

    def getPort(self):
        return self.port

