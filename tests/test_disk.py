#!/usr/bin/env python

from test_common import *
from lib.disk import *
import unittest

class TestDisk(DiskUtilsTest):
    def setUp(self):
        qrImage = QemuRawDiskImage.create("qrdisk1", "1G")
        self.assertEqual(qrImage.virtualSize, 1024*1024*1024)
        self.assertEqual(qrImage.diskSize, 0)
        self.qrImage = qrImage

    def tearDown(self):
        QemuRawDiskImage.destroy("qrdisk1")
        
    def test_qemu_raw_disk_image(self):
        pass

    def test_available_loopback(self):
        """
        If this fails, then either
          1. user running the test has no permissions to sudo - used by the 
             function LoopbackDevice.availableDevice(), or
          2. there is no available loopback device.

        Case 1 is more likely. If not, one can check for case 2 with the 
        command
            
            losetup -a

        which lists all loopback devices being used. It is easy to check 
        with the list whether all the /dev/loopN devices are in use.
        """
        devPath = LoopbackDevice.availableDevicePath()
        self.assertEqual(devPath[0:9], "/dev/loop")
        dev = LoopbackDevice(devPath)
        self.assertFalse(dev.connected)
        self.assertTrue(dev.imagePath is None)

    def test_loopback_connections(self):
        devPath = LoopbackDevice.availableDevicePath()
        self.assertEqual(devPath[0:9], "/dev/loop")
        dev = LoopbackDevice(devPath)
        connected = False
        try:
            dev.connect(self.qrImage.imagePath)
            connected = True
            self.assertTrue(dev.connected)
            self.assertEqual(dev.imagePath, self.qrImage.imagePath)
        finally:
            if connected:
                self.disconnectDev(dev)
                
    def test_illegal_device_connections(self):
        dev = Device("/foo")
        self.assertRaises(Exception, dev.connect)
        self.assertRaises(Exception, dev.disconnect)

    def test_raw_image_device(self):
        connected = False
        try:
            dev = self.qrImage.device
            self.assertTrue(dev is not None)
            self.assertTrue(dev.connected)
            connected = True
            self.assertEqual(dev.imagePath, self.qrImage.imagePath)
        finally:
            if connected:
                self.disconnectDev(dev)

    def test_get_partition_table(self):
        connected = False
        try:
            dev = self.qrImage.device
            self.assertTrue(dev is not None)
            self.assertTrue(dev.connected)
            connected = True
            self.assertTrue(dev.partitionTable is None)
        finally:
            if connected:
                self.disconnectDev(dev)

    def test_parse_partition_table(self):
        dev = Device("/dev/sda")
        dev.partitionTable

if __name__ == "__main__":
    unittest.main()

