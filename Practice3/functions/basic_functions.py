# Basic function examples

def greet():
    print("Hello! Welcome to Python functions practice.")

def square(number):
    result = number * number
    print("Square of", number, "is", result)

def is_even(num):
    if num % 2 == 0:
        print(num, "is even")
    else:
        print(num, "is odd")


# testing
greet()
square(5)
is_even(7)
