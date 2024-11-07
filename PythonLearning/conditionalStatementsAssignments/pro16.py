# 16. Take the length of three sides and classify the triangle (equilateral, isosceles, or scalene).


side1 = float(input("Enter the length of the first side: "))
side2 = float(input("Enter the length of the second side: "))
side3 = float(input("Enter the length of the third side: "))

if side1 + side2 > side3 and side1 + side3 > side2 and side2 + side3 > side1:
    if side1 == side2 == side3:
        print("The triangle is equilateral.")
    elif side1 == side2 or side2 == side3 or side1 == side3:
        print("The triangle is isosceles.")
    else:
        print("The triangle is scalene.")
else:
    print("The given sides do not form a valid triangle.")