# Basic class definition

class Dog:
    species = "Canis familiaris"

    def bark(self): # called Method if used with classes
        print("Woof! Woof!")


my_dog = Dog()
print("Species:", my_dog.species)
my_dog.bark()
