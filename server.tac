#!/usr/bin/env python

from twisted.application import service
from consider import server

master = server.MasterService()
application = service.Application("consider-server")
master.setServiceParent(application)
