#!/usr/bin/env python

import sys
from os.path import dirname as dn, realpath
import os
import unittest
import traceback

sys.path.insert(0, realpath(dn(dn(__file__))))
from lib._utils import *
from lib import disk

class DiskUtilsTest(unittest.TestCase):
    def disconnectDev(self, dev):
        try:
            dev.disconnect()
            self.assertFalse(dev.connected)
            self.assertTrue(dev.imagePath is None)
        except Exception, e:
            print "Cannot disconnect %s. Please do it manually." % \
                    (dev.devicePath,)
            traceback.print_exc()
