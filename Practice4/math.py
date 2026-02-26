import math
#Task1
def degree_to_rad(degree):
    return degree * math.pi/180

deg = 15
rad = degree_to_rad(deg)
print("Radian:", round(rad, 6))

#Task2
def area_Trapezoid(height, base1, base2):
    return ((base1+base2)/2)*height
print("Area of Trapezoid:", area_Trapezoid(5, 5, 6))

#Task3 Area of regular polygon
def area_regular_polygon(n, s):
    return (n * s ** 2) / (4 * math.tan(math.pi / n))
print("Area of polygon:", round(area_regular_polygon(4, 25)))

#Task4 Area of parallelogram
def area_parallelogram(base, height):
    return base * height
print("Area of parallelogram:", area_parallelogram(5, 6))