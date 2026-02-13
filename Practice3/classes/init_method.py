# __init__ constructor example

class Student:
    def __init__(self, name, age, major):
        self.name = name
        self.age = age
        self.major = major

    def introduce(self):
        print("I am", self.name)
        print("Age:", self.age)
        print("Major:", self.major)


s1 = Student("Aigerim", 17, "IT")
s1.introduce()
