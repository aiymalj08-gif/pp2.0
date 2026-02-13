# Using lambda with map()

numbers = [1, 2, 3, 4, 5]

squared_numbers = list(map(lambda x: x ** 2, numbers))

print("Original:", numbers)
print("Squared:", squared_numbers)
