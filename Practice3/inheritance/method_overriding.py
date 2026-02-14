# Method overriding

class Bird:
    def sound(self):
        print("Bird makes a sound")

class Parrot(Bird):
    def sound(self): #child class replaces parent class method with its own version
        print("Parrot can talk") #polymorphism-when the method names are identical but the output differs


b = Bird()
p = Parrot()

b.sound()
p.sound()
