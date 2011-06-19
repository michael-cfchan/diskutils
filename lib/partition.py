#!/usr/bin/env python


class PartitionTable(object):
    def __init__(self, sectorSize, tableType):
        self.sectorSize = sectorSize
        self.type = tableType
        self.partitions_ = {}

    def partition(self, partitionNumber):
        if partitionNumber not in self.partitions_:
            return None
        return self.partitions_[partitionNumber]

    def newPartition(self, partitionNumber, startSector, endSector,
                     partitionType, flags):
        if partitionNumber in self.partitions_:
            raise Exception, "Partition %d already exists." % (partitionNumber,)
        partition = Partition(self, partitionNumber, startSector, endSector, 
                             partitionType, flags)
        self.partitions_[partitionNumber] = partition

    def delPartition(self, partitionNumber):
        pass

class Partition(object):
    def __init__(self, table, partitionNumber, startSector, endSector,
                 partitionType, flags):
        self.table = table
        self.number = partitionNumber
        self.startSector = startSector
        self.endSector = endSector
        self.type = partitionType
        self.flags = flags

    @property
    def sectorSize(self):
        return self.table.sectorSize

    @property
    def sizeInSectors(self):
        return self.endSector_ - self.startSector_ + 1;

    @property
    def sizeInBytes(self):
        return self.sizeInSectors() * self.sectorSize()
