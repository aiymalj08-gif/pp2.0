import re #re - Regular expressions (module)

# 1. 'a' followed by zero or more 'b'
pattern = r"ab*"
text = "ab abb abbb a ac"
print("1:", re.findall(pattern, text)) # findall = outputs list containing all matches


# 2. 'a' followed by two to three 'b'
pattern = r"ab{2,3}"
text = "ab abb abbb abbbb"
print("2:", re.findall(pattern, text))


# 3. sequences of lowercase letters joined with underscore
pattern = r"[a-z]+_[a-z]+"
text = "snake_case example_text test"
print("3:", re.findall(pattern, text))


# 4. one uppercase letter followed by lowercase letters
pattern = r"[A-Z][a-z]+"
text = "Hello World Python REGEX"
print("4:", re.findall(pattern, text))


# 5. 'a' followed by anything ending in 'b'
pattern = r"a.*b"
text = "a123b axxb ab a_test_b"
print("5:", re.findall(pattern, text))


# 6. replace space, comma, dot with colon
text = "Hello, world. Python is cool"
result = re.sub(r"[ ,\.]", ":", text) #sub = Replaces one or many matches with a string
print("6:", result)


# 7. snake_case → camelCase
def snake_to_camel(text):
    words = text.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])

print("7:", snake_to_camel("snake_case_string"))


# 8. split string at uppercase letters
text = "SplitThisStringAtUppercase"
result = re.split(r"(?=[A-Z])", text) # ?= --> splits BEFORE the uppercase letters \ positive lookahead --> does not include the match
print("8:", result)


# 9. insert spaces before capital letters
text = "InsertSpacesBeforeCapitals"
result = re.sub(r"([A-Z])", r" \1", text).strip() # \ ("escape character")--> treats the following element as a literal character 
print("9:", result)


# 10. camelCase → snake_case
def camel_to_snake(text):
    return re.sub(r"([A-Z])", r"_\1", text).lower() # ()-Capture and group

print("10:", camel_to_snake("camelCaseStringExample"))