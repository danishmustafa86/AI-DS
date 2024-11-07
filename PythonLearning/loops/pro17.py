# 17. Write a program that continues to ask for a number until the correct number is guessed.


num = 5
inputedNum = int(input("enter a number to guess "))
while num != inputedNum:
    inputedNum = int(input("enter a number to guess "))

print("Thanks for intering correct number")