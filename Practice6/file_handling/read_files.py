with open("sample.txt", "r") as f:
    print("Using read:")
    print(f.read()) #reads the whole text 

with open("sample.txt", "r") as f:
    print("Using readline:")
    print(f.readline()) #reads only the first line 

with open("sample.txt", "r") as f:
    print("Using readlines:")
    lines=f.readlines()
    print(lines) # prints every line of text in one array