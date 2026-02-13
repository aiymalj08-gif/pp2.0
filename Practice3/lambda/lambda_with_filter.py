# Using lambda with filter()

numbers = [10, 15, 20, 25, 30, 35]

even_numbers = list(filter(lambda x: x % 2 == 0, numbers))

print("Even numbers:", even_numbers)
