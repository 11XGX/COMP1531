from abc import ABCMeta, abstractmethod
import string
import csv

# Abstract reader for a generic filetype. Defined functions are all required by every reader object.
class Reader(object):
    __metaclass__ = ABCMeta
    def __init__(self, fileName):
        self._filename = fileName
    
    # Returns the filename associated with this reader object.
    def getFile(self):
        return self._filename 

    @abstractmethod
    def readAllRows(self):
        pass
    
    # Reads items in a specific row where that row's first item is equal to the key provided. Returns the list of items read on row. Returns -1 if key not found.
    @abstractmethod
    def readKeyedRow(self, key):
        pass

    # Similar to above method. Except also handles compound keys when argument keys are given as a list.
    @abstractmethod
    def readCompoundKeyedRow(self, keys):
        pass

    # Reads into a list from filename. Only the first item on each row is read, returned in list.
    @abstractmethod
    def readColumn(self):
        pass

    @abstractmethod
    def readTriples(self):
        pass

    @abstractmethod    
    def numRow(self):
        pass


class CSVReader(Reader):
    # Reads into a list from filename. Each row in the list becomes one new element in returned list.
    def readAllRows(self):
        readList = []
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                readList.append(row)
        return readList

    # Reads items in a specific row where that row's first item is equal to the key provided. Returns items in that row as a list. Returns -1 if key not found.
    def readKeyedRow(self, key):
        readList = []
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                if row[0] == key:
                    for line in row:
                        readList.append(line)
        return readList 

    # Similar to the above, except handles compound keys where argument keys are given as a list. 
    def readCompoundKeyedRow(self, keys):
        readList = []
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                count = 0
                for key in keys:
                    if row[count] == key:
                        count += 1
                if count == len(keys):
                    for line in row:
                        readList.append(line)
        return readList 
        

    # Reads into a list from filename. Only the items in the given column number are read, returned in list.
    def readColumn(self, columnNumber):
        readList = []
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for i in reader:
                readList.append(i[columnNumber])
        return readList

    def readTriples(self):
        readList = {}
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for line in reader:
                readList[line[0]] = (line[1],line[2]) # (password, salt)
        return readList

    # Simply counts the number of rows in the CSV file
    def numRow(self):
        count = 0
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                count += 1
        return count

