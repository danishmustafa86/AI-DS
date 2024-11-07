# 12. Write a program that takes a temperature in Celsius and checks if it’s freezing, moderate, or hot.

temp = float(input("Enter temperature of your weather"))
if temp <= 0:
    print("the temperature is freezing")
if temp > 0 and temp <= 25:
    print("the temperature is moderate")
else:
    print("the temperature is hot")

