# Functions that return values

def add(a, b):
    return a + b

def maximum(a, b, c):
    return max(a, b, c)

def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


sum_result = add(4, 6)
print("Sum:", sum_result)

print("Max number:", maximum(3, 10, 7))
print("Factorial of 5:", factorial(5))
