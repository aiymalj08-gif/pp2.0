# Class methods

class MathUtils:
    @classmethod #decorator--> tells that the next method is related to the class
    def multiply(cls, a, b):
        return a * b

    @classmethod
    def cube(cls, x):
        return x ** 3


print("Multiply:", MathUtils.multiply(4, 5))
print("Cube:", MathUtils.cube(3))
