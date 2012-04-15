#!/usr/bin/env python

from smap.archiver.client import *
from time import time

import daemon
import grp
import lockfile
import signal
import sys

class Logger:

    QUERYURL =  "http://ar1.openbms.org:8079"
    CORYDATA = "Metadata/Extra/Phase = 'ABC' and \
                Properties/UnitofMeasure = 'kW' and \
                Metadata/Location/Building = 'Cory Hall'"
    
    def __init__(self):
        self.starttime = str(time())
        self.republisher = RepublishClient(Logger.QUERYURL, self.log, restrict=Logger.CORYDATA)
        self.logfile = None
        self.errfile = None

    def log(self, datapoint):        
        self.logfile.write(''.join([str(datapoint), '\n']))
        self.logfile.flush()

    def run(self):
        try:
            self.errfile = open(''.join([self.starttime, ".err"]), 'a')
        except:
            # fuck if I know how else to get errors out of this daemon
            pass
        try:
            self.logfile = open(''.join([self.starttime, ".log"]), 'a')
        except IOError:
            self.errfile.write("Mysterious IOError.")
            self.errfile.flush()
        self.republisher.connect()
        reactor.run()

    def close(self):
        self.errfile.close()
        self.logfile.close()
        if not self.republisher.close():
            sys.stderr.write("Couldn't close smap republisher client.\n")

if __name__ == "__main__":
    
    logger = Logger()

    context = daemon.DaemonContext(
        working_directory='/var/smapsplunker',
        umask=0o002,
        pidfile=lockfile.FileLock('/var/run/smapsplunker.pid')
        )

    context.signal_map = {
        signal.SIGTERM: logger.close,
        signal.SIGHUP: 'terminate',
        }

    with context:
        logger.run() 
        #QUERYURL =  "http://ar1.openbms.org:8079"
        #CORYDATA = "Metadata/Extra/Phase = 'ABC' and \
        #            Properties/UnitofMeasure = 'kW' and \
        #            Metadata/Location/Building = 'Cory Hall'"
        #
        #logfile = None
        #try:
        #    logfile = open(''.join([str(time()), ".log"]), 'w')
        #except IOError:
        #    sys.stderr.write("Unable to open smapsplunker log.\n")
        #    exit()

        #def log(datapoint):
        #    logfile.write(''.join([str(datapoint), '\n']))
        #    logfile.flush()

        #republisher = RepublishClient(QUERYURL, log, restrict=CORYDATA)
        #republisher.connect()

        #reactor.run()
