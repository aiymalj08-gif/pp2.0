from functools import reduce

nums=[1, 2, 3, 4, 5]

square=list(map(lambda x: x*x, nums))
print("Squares:", square)

evens=list(filter(lambda x: x%2==0, nums))
print("Evens:", evens)

total=reduce(lambda a, b: a+b, nums) # reduce - combining all elements into a single value. like Sum function
print("Sum:", total)