# Class variables example

class Car:
    wheels = 4  # class variable

    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def display(self):
        print(self.brand, self.model, "has", Car.wheels, "wheels")


c1 = Car("Toyota", "Camry")
c2 = Car("BMW", "X5")

c1.display()
c2.display()
