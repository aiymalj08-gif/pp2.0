import re
import json 

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Extract item total prices (line after "x ..." quantity line)
price_pattern = r"\d[\d ]*,\d{2}\n(\d[\d ]*,\d{2})"
prices = re.findall(price_pattern, text)
Price_numbers = [float(p.replace(" ", "").replace(",", ".")) for p in prices]

# 2. Extract product names (lines starting with number + dot)
product_pattern = r"\d+\.\n(.+)"
product_names = re.findall(product_pattern, text)

# 3. Sum total
total = sum(Price_numbers)

# 4. Extract date and time
date_time_pattern = r"\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}"
found_date_time = re.findall(date_time_pattern, text)
datetime = found_date_time[0] if found_date_time else None

# 5. Extract payment method
payment_pattern = r"(Банковская карта|Наличные)"
payments = re.search(payment_pattern, text)
payment = payments[0] if payments else None 

# 6. Combine all data into a dictionary
data = {
    "Prices": Price_numbers,
    "Prodname": product_names,
    "Total": total,
    "Date-Time": datetime, 
    "Payment": payment
}

# 7. Print JSON
print(json.dumps(data, indent=4, ensure_ascii=False))

# 8. Save to file
with open("receipt.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

