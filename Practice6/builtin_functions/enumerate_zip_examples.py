names=["Alice", "Bob", "Charlie"]
for index, name in enumerate(names):
    print(index, name)

scores=[90, 85, 80]
for name, score in zip(names, scores):
    print(name, score)

nums=[5, 2, 8, 4]
print("sorted:", sorted(nums))
print("sum:", sum(nums))
print("max:", max(nums))
print("min:", min(nums))
print("length:", len(nums))
