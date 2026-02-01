# while loop with break

number = 1

while number <= 10:
    if number == 6:
        print("Stopping the loop")
        break
    print(number)
    number += 1
