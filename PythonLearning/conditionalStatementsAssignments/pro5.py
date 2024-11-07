# 5. Ask the user for a grade percentage and display the corresponding letter grade (A, B, C, D, F).

num = input("Enter you numbers")
if num >= 90:
    print("A grade")
elif num >= 70:
    print("B grade")
elif num >= 50:
    print("C grade")
elif num >= 33:
    print("D grade")
else:
    print("F grade")