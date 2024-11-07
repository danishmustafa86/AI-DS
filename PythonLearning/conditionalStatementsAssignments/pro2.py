# 2. Take a user’s age as input and display whether they are a minor, adult, or senior citizen.


age = input("Enter your age")
if age < 20:
    print("User is minor citizen")
elif age >= 20 and age <= 45:
    print("User is Adult")
else:
    print("User is seniour citizen")