#!/usr/bin/env python

"""

Operations are not concurrency-safe. User of the library are expected to 
perform their own synchronizations.
"""

import os
from _utils import *

class Disk(object):
    pass

class DiskImage(object):
    def __init__(self, imagePath):
        self.imagePath_ = imagePath
        self.disk_ = None
        self._getSizes()

    def _getSizes(self):
        """
        Linux-only. Will break in Windows and UNIX systems that do not provide
        the st_blocks
        """
        if os.path.isfile(self.imagePath_):
            stat = os.stat(self.imagePath_)

            # See these links for why a multiplier of 512 is used on Linux:
            #
            # http://bugs.python.org/issue10016  - msg117944
            # http://www.gossamer-threads.com/lists/python/bugs/925654
            #
            # This patch has better documentation of the object returned by
            # os.stat():
            # 
            # http://bugs.python.org/file22382/stat_result.patch
            self.diskSize_ = stat.st_blocks * 512
            self.virtualSize_ = stat.st_size 
        else:
            self.diskSize_ = 0
            self.virtualSize = 0

    def device(self):
        """
        Override in derived type to return a Disk object representing the disk
        device for the image. For example, this could 
        """
        return None

    def virtualSize(self):
        return self.virtualSize_

    def virtualSizeIs(self, numBytes):
        """
        Override in derived type to set the size of the disk image
        """
        raise Exception, "Virtual size cannot be changed."

    def diskSize(self):
        return self.diskSize_ 

    def cleanup(self):
        """
        Override in derived type to perform cleanup tasks
        """
        pass

class QemuDiskImage(DiskImage):
    TYPE_RAW = 0
    # TODO: To be supported:
    # TYPE_QCOW2 = 1

    _createTypeMap = {
        TYPE_RAW : "raw",
        #TYPE_QCOW2 : "qcow2",
    }

    def __init__(self, imagePath, imageType):
        super(QemuDiskImage, self).__init__(imagePath)
        self.imageType_ = imageType

    @classmethod
    def create(cls, imagePath, imageType, virtualSize):
        if imageType not in QemuDiskImage._createTypeMap:
            raise Exception, "Unsupported QEMU image type."
        typeArg = QemuDiskImage._createTypeMap[imageType]
        qargs = ["qemu-img", "create", "-f", typeArg, 
                 imagePath, virtualSize]
        r, s, e = subprocessPiped(qargs)
        if r != 0:
            print "qemu-img stdout:", s
            print "qemu-img stderr:", e
            raise Exception, "qemu-img failed. Return code: %d" % (r,)
        return cls(imagePath)

    @classmethod
    def destroy(cls, imagePath):
        if os.path.isfile(imagePath):
            os.remove(imagePath)

    @property
    def imageType(self):
        return self.imageType_

    def device(self):
        if self.disk_:
            return self.disk_

        # Note: Not concurrency safe
        if self.imageType == QemuDiskImage.TYPE_RAW:
            print "raw disk device"

class QemuRawDiskImage(QemuDiskImage):
    def __init__(self, imagePath):
        super(QemuRawDiskImage, self).__init__(imagePath, QemuDiskImage.TYPE_RAW)

    @classmethod
    def create(cls, imagePath, virtualSize):
        return super(QemuRawDiskImage, cls).create(imagePath,
                                                   QemuDiskImage.TYPE_RAW,
                                                   virtualSize)

