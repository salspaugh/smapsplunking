#!/usr/bin/env python

from smap.archiver.client import *

import daemon
import json
import lockfile
import logging
import logging.config
import signal

class SmapSplunkingLogger:

    QUERYURL = "http://ar1.openbms.org:8079"
    DATA = "Metadata/Extra/Phase = 'ABC' and \
                Properties/UnitofMeasure = 'kW'"
    
    def __init__(self):
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger()
        self.republisher = RepublishClient(SmapSplunkingLogger.QUERYURL, 
                             self.log, restrict=SmapSplunkingLogger.DATA)

    def convert(smapobj):
        converted = []
        for (metadata, readings) in smapobj.iteritems():
            uuid = readings['uuid']
            readinglist = readings['Readings']
            for item in readinglist:
                item.extend([metadata, uuid])
                converted.append(item)
        return converted

    def log(self, smapobj):        
        #self.logger.critical(''.join([str(smapobj), '\n']))
        #data = convert(smapobj)
        #for d in data:
        #    self.logger.critical(''.join([str(d), '\n']))
        self.logger.critical(''.join([str(smapobj), '\n']))

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
