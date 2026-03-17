import shutil
import os 

shutil.copy("sample.txt", "backup.txt")
print("Backup created")


if os.path.exists("backup.txt"):
    os.remove("backup.txt")
    print("backup file has been deleted")
else:
    print("File hasn't been found")