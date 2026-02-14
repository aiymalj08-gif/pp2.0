# Basic inheritance

class Animal:
    def eat(self):
        print("This animal eats food")

class Cat(Animal): # cat class ingerits the features of the parent class Animal
    def meow(self):
        print("Cat says meow")


c = Cat()
c.eat()
c.meow()
