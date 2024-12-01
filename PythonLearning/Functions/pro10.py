# 5. Write a function to calculate the GCD (Greatest Common Divisor) of two numbers.


def gcd(a, b):
    while b != 0:
        a, b = b, a % b 
        print(a, b) # Update a to b, and b to the remainder of a divided by b
    return a

# Example usage:
num1 = 56
num2 = 98
result = gcd(num1, num2)
print(f"The GCD of {num1} and {num2} is: {result}")
