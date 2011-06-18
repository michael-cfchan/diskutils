#!/usr/bin/env python

"""

Operations are not concurrency-safe. User of the library are expected to 
perform their own synchronizations.
"""

import os
import re
from _utils import *

# {{{ Disk device
class Device(object):
    def __init__(self, devicePath):
        self.devicePath_ = devicePath

    def devicePath(self):
        return self.devicePath_

    def connect(self):
        raise Exception, "Operation not supported on %s: connect" % \
                self.__class__.__name__

    def disconnect(self):
        raise Exception, "Operation not supported on %s: disconnect" % \
                self.__class__.__name__

class LoopbackDevice(Device):
    def __init__(self, devicePath):
        super(LoopbackDevice, self).__init__(devicePath)
        # Path to image connected to the device
        self.imagePath_ = None

    @classmethod
    def availableDevicePath(cls):
        r, s, e = subprocessPiped(["sudo", "losetup", "-f"])
        m = re.match(r"/dev/loop[0-9]+",s)
        if not m:
            return None
        return m.group()

    def connected(self):
        r, s, e = subprocessPiped(["sudo", "losetup", self.devicePath_])
        if r == 0:
            rep = r"%s:\s+\[\w+\]:[0-9]+\s+\((.+)\)" % (self.devicePath_,)
            m = re.match(rep, s)
            self.imagePath_ = os.path.realpath(m.groups()[0])
            ret = True
        elif r == 1:
            self.imagePath_ = None
            ret = False
        else:
            raise Exception, "Cannot verify if %s is connected" % \
                    (self.devicePath_,)
        return ret

    def imagePath(self):
        if self.connected():
            return self.imagePath_
        return None
    
    def connect(self, imagePath): 
        if not os.path.isfile(imagePath):
            raise Exception, "Source disk image does not exist: %s" % \
                    (imagePath,)
        if self.connected():
            raise Exception, "Device already connected to %s" % \
                    (self.imagePath_,)

        r, s, e = subprocessPiped(["sudo", "losetup", self.devicePath(),
                                  imagePath])
        if r != 0:
            print "loopback connect stdout:", s
            print "loopback connect stderr:", e
            raise Exception, "Cannot connect to %s. Ret code: %d" % \
                    (imagePath, r)
        self.imagePath_ = imagePath


    def disconnect(self):
        if not self.connected():
            raise Exception, "Device is not connected."
        r, s, e = subprocessPiped(["sudo", "losetup", "-d",
                                   self.devicePath()])
        if r != 0:
            print "loopback disconnect stdout:", s
            print "loopback disconnect stdout:", e
            raise Exception, "Cannot disconnect from %s. Ret code: %d" % \
                    (self.imagePath_, r)
        self.imagePath_ = None
# }}}

# {{{ Disk image
class DiskImage(object):
    def __init__(self, imagePath):
        self.imagePath_ = os.path.realpath(imagePath)
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

    def imagePath(self):
        return self.imagePath_

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

# }}}
