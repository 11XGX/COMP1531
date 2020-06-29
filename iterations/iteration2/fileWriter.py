from abc import ABCMeta, abstractmethod
import string
import csv

# Abstract writer to a generic filetype. Defined functions are all required by every writer object.
class Writer(object):
    __metaclass__ = ABCMeta
    def __init__(self, fileName):
        self._filename = fileName

    # Returns the filename associated with the writer
    def getFile(self):
        return self._filename

    # Writes into the filename. Will make one new row.
    @abstractmethod
    def append(self, write):
        pass

    # A reader must be 'injected' to find the appropriate row before writing.
    @abstractmethod
    def replaceRow(self, Reader, key, write):
        pass

    # Similar to the above. Except handles cases where a compound key is required.
    @abstractmethod
    def replaceCompoundKeyedRow(self, Reader, keys, write):
        pass

    # A reader must be 'injected' to find the appropriate row before writing.
    @abstractmethod
    def deleteRow(self, Reader, key):
        pass

    # Deletes all single entries found anywhere in the file that match the given toDeleteEntry
    @abstractmethod
    def deleteEntries(self, Reader, toDeleteEntry):
        pass


class CSVWriter(Writer):
    # Writes into the filename. Will make one new row. One 'line' per element in list.
    def append(self, write):
        with open(self._filename, 'a') as csv_out:
            writer = csv.writer(csv_out)
            writer.writerow(write)   

    # Replaces the items in the keyed row with new items. 
    def replaceRow(self, Reader, key, write):
        readList = Reader.readAllRows()
        found = 0
        count = 0
        for row in readList:
            if row[0] == key and not found:
                found = 1
            if not found:
                count += 1
        if (found):
            readList[count] = write
            with open(self._filename,'w') as csv_out:
                writer = csv.writer(csv_out)
                for row in readList:
                    writer.writerow(row) 

    # Replaces the items in the compound keyed row with the new items.
    def replaceCompoundKeyedRow(self, Reader, keys, write):
        readList = Reader.readAllRows()
        found = 0
        count = 0
        for row in readList:
            keyCount = 0
            for key in keys:
                if row[keyCount] == key:
                    keyCount += 1
            if keyCount == len(keys):
                found = 1
            if not found:
                count += 1
        if (found):
            readList[count] = write
            with open(self._filename,'w') as csv_out:
                writer = csv.writer(csv_out)
                for row in readList:
                    writer.writerow(row)  

    # Deletes the keyed row from the csv file.
    def deleteRow(self, Reader, key):
        readList = Reader.readAllRows()
        with open(self._filename,'w') as csv_out:
            writer = csv.writer(csv_out)
            for row in readList:
                if (row[0] != key):
                    writer.writerow(row) 

    def deleteEntries(self, Reader, toDeleteEntry):
        readList = Reader.readAllRows()
        for i in range(0, len(readList)):
            for j in range(0, len(readList[i])):
                if readList[i][j] == toDeleteEntry:
                    del readList[i][j]
        with open(self._filename,'w') as csv_out:
            writer = csv.writer(csv_out)
            for row in readList:
                writer.writerow(row)       
        
