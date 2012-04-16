#!/usr/bin/env python

from smap.archiver.client import *

import logging
import logging.config

if __name__ == "__main__":
   
    #ARDQUERY = "select data in ('4/19/2012 9:00', '4/16/2012 9:45') \
    #                limit -1 streamlimit 1000 \
    #                where Metadata/Extra/Phase = 'ABC' and \
    #                Properties/UnitofMeasure = 'kW'"

    QUERY = "where Metadata/Extra/Phase = 'ABC' and Properties/UnitofMeasure = 'kW'"

    logging.config.fileConfig('archiving.conf')
    archiver = logging.getLogger()

    fetcher = SmapClient()
    for smapobj in fetcher.query(ARDQUERY):
        archiver.critical(''.join([str(smapobj), '\n']))
    


