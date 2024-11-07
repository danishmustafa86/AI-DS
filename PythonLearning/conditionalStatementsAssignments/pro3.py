# Write a program that checks if a given year is a leap year.

year  = input("Enter year")
if year % 4 == 0:
    print("Given year is lead year")
else:
    print("It is not leap year")