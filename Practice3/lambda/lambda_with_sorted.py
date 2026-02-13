# Sorting with lambda

students = [
    ("Ali", 85),
    ("Dana", 92),
    ("Miras", 78),
    ("Aruzhan", 95)
]

sorted_students = sorted(students, key=lambda student: student[1])

print("Sorted by grades:")
for s in sorted_students:
    print(s)
