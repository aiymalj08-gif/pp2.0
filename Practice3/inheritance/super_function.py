# Using super()

class Person:
    def __init__(self, name):
        self.name = name

class Teacher(Person):
    def __init__(self, name, subject): # when u create __init__function in the child class it does not take the properties of its parent class
        super().__init__(name) #allows the child class to inherit all the properties of the Parent class
        self.subject = subject

    def info(self):
        print(self.name, "teaches", self.subject)


t1 = Teacher("Mr. Nurlan", "Mathematics")
t1.info()
