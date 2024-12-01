# 2. Write a function to find the nth Fibonacci number using recursion.

def fibonacci_recursive(n):
    # Base case: the first two Fibonacci numbers
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2)

# Example usage:
n = 10
ans = fibonacci_recursive(n)
print(f"The {n}th Fibonacci number is: {ans}")