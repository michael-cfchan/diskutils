#!/usr/bin/env python

from test_common import *
from lib.disk import QemuRawDiskImage
import unittest

class TestDisk(DiskUtilsTest):
    def setUp(self):
        qrImage = QemuRawDiskImage.create("qrdisk1", "1G")
        self.assertEqual(qrImage.virtualSize(), 1024*1024*1024)
        self.assertEqual(qrImage.diskSize(), 0)
        self.qrImage = qrImage

    def tearDown(self):
        QemuRawDiskImage.destroy("qrdisk1")
        
    def test_qemu_raw_disk_image(self):
        pass

if __name__ == "__main__":
    unittest.main()
