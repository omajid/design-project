#!/usr/bin/env python

from twisted.application.service import Application, IServiceCollection
from twisted.application.internet import TCPServer
from twisted.web.server import Site

from consider.rpcservice import MonitorService

RPC_SERVER_PORT=1055
monitorService = MonitorService()
print("Created monitor service")
application = Application("consider-server")
serviceCollection = IServiceCollection(application)
print("starting tcp server")
TCPServer(RPC_SERVER_PORT, Site(monitorService.getResource())
        ).setServiceParent(serviceCollection)
