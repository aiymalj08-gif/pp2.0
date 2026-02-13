# Different types of function arguments

def introduce(name, age):
    print("My name is", name, "and I am", age, "years old.")

# default argument
def power(base, exponent=2): 
    print(base, "to the power of", exponent, "=", base ** exponent)

# keyword arguments
def student_info(name, major, gpa):
    print("Student:", name)
    print("Major:", major)
    print("GPA:", gpa)


introduce("Aigerim", 17)
power(5)
power(2, 5)
student_info(gpa=3.8, name="Ali", major="Computer Science")
