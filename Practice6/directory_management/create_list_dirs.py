import os
os.mkdir("data")

os.makedirs("data/students/2026")

print("Directory contents:")
print(os.listdir("."))

print("current directory:", os.getcwd())

os.chdir("data")
print("changed directory to:", os.getcwd())
