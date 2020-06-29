'''
Write a program that accepts a sequence of whitespace separated words 
as input and prints the words after removing all duplicate words and 
sorting them alphanumerically. Suppose the following input is 
supplied to the program:
hello world and practice makes perfect and hello world again
Then, the output should be:
again and hello makes perfect practice world

Your program should take in only one line of input.

You may assume that your program will only be tested
with valid inputs.
'''

sentence = input()


# Define this function to return the expected output
# Do not print it from this function
def singlify(s):
    words = s.split()
    newWords = []
    
    for word in words:
        isUnique = True
        for newWord in newWords:
            if word.lower() == newWord.lower():
            	isUnique = False
        if (isUnique):
            newWords.append(word)  
    
    newWords.sort(key=str.lower)
    return newWords

print(singlify(sentence))
