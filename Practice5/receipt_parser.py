import re
import json 
with open("raw.txt", "r", encoding="utf-8") as f:
    text=f.read()

#1 Extract prices
price_pattern=r"\d[\d ]*,\d{2}"
prices=re.findall(price_pattern, text)

Price_numbers=[float(p.replace(" ", "").replace(",", ".")) for p in prices]

#2 Product names
product_pattern=r"\d+\.\n(.+)"
product_names=re.findall(product_pattern, text)

#3 Sum 
total=sum(Price_numbers)

#4 Date and Time 
date_time=r"\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}"
found_date_time=re.findall(date_time, text)
datetime = found_date_time[0] if found_date_time else None

#5 Payment Method
payment_method=r"(Банковская карта|Наличные)"
payments=re.search(payment_method, text)
payment=payments[0] if payment_method else None 

data={
    "Prices":Price_numbers,
    "Prodname":product_names,
    "Total":total,
    "Date-Time":datetime, 
    "Payment":payment
}

print(json.dumps(data, indent=4, ensure_ascii=False))

with open("receipt.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

