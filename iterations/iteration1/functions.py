# Helper functions so that routes.py does not become cluttered with indirect funcions
import random
import string
import csv

class CSV:
    def __init__(self, fileName):
        self._filename = fileName

    # Writes into the filename. Will make one new row. One line per element in list.
    def append(self, write):
        with open(self._filename, 'a') as csv_out:
            writer = csv.writer(csv_out)
            writer.writerow(write)   

    # Replaces the item in the given row 'pos' with new items. 
    def replaceRow(self, pos, write):
        readList = self.readRow()
        readList[pos] = write
        with open(self._filename,'w') as csv_out:
            writer = csv.writer(csv_out)
            for row in readList:
                writer.writerow(row)            

    # Reads into a list from filename. Each row in the list becomes one new element in returned list.
    def readRow(self):
        readList = []
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                readList.append(row)
        return readList

    # Reads items in a specific row where that row's first item is equal to the key provided. Returns firstly the line that is read the item on and secondly the row elements.
    def readKeyedRow(self, key):
        readList = []
        count = 0
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                if row[0] == key:
                    readList.append(count)
                    for line in row:
                        readList.append(line)
                count += 1
        return readList 

    # Reads items in a specific row in the filename. Each item becomes a new element in the returned list.
    def readOneRow(self, pos):
        readList = []
        count = 0
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                if count == pos:
                    for line in row:
                        readList.append(line)
                count += 1
        return readList   

    # Reads into a list from filename. Only the first item on each row is read, returned in list.
    def readColumn(self):
        readList = []
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for i in reader:
                readList.append(i[0])
        return readList

    def readPairs(self):
        readList = {}
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for line in reader:
                readList[line[0]] = line[1]
        return readList

    def readAllRows(self):
        readList = []
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for i in reader:
                readList.append(i)
        return readList

    # Simply counts the number of rows in the CSV file
    def numRow(self):
        count = 0
        with open(self._filename,'r') as csv_in:
            reader = csv.reader(csv_in)
            for row in reader:
                count += 1
        return count

#non csv stuff

def randomKey():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
