#Task 1 --> gives the squares of every number up to the given number n
def squares_upto_n(n):
    for i in range(n+1):
        yield i*i

#Task 2 --> even number generator from 0 up to the given number n
def evens(n):
    for i in range(n+1):
        if i%2==0:
            yield i

#Task 3 --> generator that outputs the numbers that are divisible by 3 and 4
def divisibles_3_4(n):
    for i in range(n+1):
        if i%3==0 and i%4==0:
            yield i

#Task 4 --> yields the squares of the numbers from those inputted two values a, b
def squares_range(a,b):
    for i in range(a, b+1):
        yield i*i

#Task 5--> outputs the number inputted until 0
def countdown(n):
    while n>=0:
        yield n
        n-=1



#inputs for the generators 
if __name__=="__main__":
    print("Task 1:")
    for value in squares_upto_n(5):
        print(value)


    print("\nTask 2:")
    n=10
    print(",".join(str(num) for num in evens(n)))

    print("\nTask 3:")
    n=50
    for value in divisibles_3_4(n):
        print(value)

    print("\nTask 4:")
    for val in squares_range(3,7):
        print(val)

    print("\nTask 5:")
    n=5
    for val in countdown(n):
        print(val)