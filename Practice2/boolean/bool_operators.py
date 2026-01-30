'''bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({}) #these all return False '''


x = 200
print(isinstance(x, int)) # asks whether x is integer --> if Yes then it outputs true

b = "3.14"
print(isinstance(b, (int, float))) # asks whether b is integer or float--> if No then it outputs false