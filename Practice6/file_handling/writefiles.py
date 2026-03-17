#creating a file called sample.txt
with open("sample.txt", "w") as f:
    f.write("Alice 15\n")
    f.write("Aiym 17\n")
    f.write("Bob 20\n")

print("File's created and data written")

#appending a new information to the existing file 
with open("sample.txt", "a") as f:
    f.write("Charlie 9\n")

print("new line appended")