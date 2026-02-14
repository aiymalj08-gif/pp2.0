# Multiple inheritance

class Father:
    def skills(self):
        print("Gardening and driving")

class Mother:
    def talents(self):
        print("Cooking and painting")

class Child(Father, Mother):
    def abilities(self):
        print("Child has skills from both parents")


c = Child()
c.skills() # even though the c does not have the methods like skills and talents of its own, it actually prints the methods of the parent classes
c.talents()
c.abilities()
