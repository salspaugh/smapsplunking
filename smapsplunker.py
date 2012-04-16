#!/usr/bin/env python

from smap.archiver.client import *

import daemon
import grp
import lockfile
import logging
import logging.config
import signal
import sys

class SmapSplunkingLogger:

    QUERYURL = "http://ar1.openbms.org:8079"
    CORYDATA = "Metadata/Extra/Phase = 'ABC' and \
                Properties/UnitofMeasure = 'kW' and \
                Metadata/Location/Building = 'Cory Hall'"
    
    def __init__(self):
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger()
        self.republisher = RepublishClient(SmapSplunkingLogger.QUERYURL, 
                             self.log, restrict=SmapSplunkingLogger.CORYDATA)

    def log(self, datapoint):        
        self.logger.critical(''.join([str(datapoint), '\n']))

    def run(self):
        self.republisher.connect()
        reactor.run()

    def close(self):
        self.republisher.close() #TODO: Check if this returns True on exit?

if __name__ == "__main__":
    
    sslog = SmapSplunkingLogger()

    fdpreserve = [] # don't close the logging files on daemon startup
    for handler in sslog.logger.handlers:
        if hasattr(handler, 'stream') and hasattr(handler.stream, 'fileno'):
            fdpreserve.append(handler.stream.fileno())

    context = daemon.DaemonContext(
        working_directory='/var/smapsplunker',
        umask=0o002,
        pidfile=lockfile.FileLock('/var/run/smapsplunker.pid'),
        files_preserve = fdpreserve
        )

    context.signal_map = {
        signal.SIGTERM: sslog.close,
        signal.SIGHUP: 'terminate',
        }

    with context:
        sslog.run() 
