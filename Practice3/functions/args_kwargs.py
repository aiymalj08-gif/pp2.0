# *args and **kwargs example

def add_numbers(*args): #used when u don't know the specific number of arguments that u are going to give
    total = 0
    for num in args:
        total += num
    print("Sum =", total)

def print_profile(**kwargs):# used for uncertain amount of key arguments like, a=4 and so on
    for key, value in kwargs.items():
        print(key, ":", value)


add_numbers(1, 2, 3, 4, 5)

print_profile(name="Aruzhan", age=18, country="Kazakhstan", hobby="reading")
