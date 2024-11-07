#14. Check if a year input by the user is a century year.

year = int(input("Enter year"))
if year % 100 == 0:
    print("It is a Century year")
else:
    print("It not a Century year")