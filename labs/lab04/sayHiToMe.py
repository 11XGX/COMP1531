import csv

def write(inputName, inputID, inputDesc):
	with open('info.csv','a') as csv_out:
		writer = csv.writer(csv_out)
		writer.writerow([name, zID, desc]);

def read():
	with open('info.csv','r') as csv_in:
		reader = csv.reader(csv_in)
		for row in reader:
			print(row)
		
name = input("Enter your name: ")
zID = int(input("Enter your zID: "))
desc = input("Enter your description: ")
write(name, zID, desc)
read()
