from datetime import datetime, timedelta
#datetime is module and datetime, timedelta are classes
#timedelta allows us to perform calculations using timedelta objects


#Task 1--> subtracts 5 days from the current date
def subtract_5_days():
    current_date=datetime.now()
    new_date=current_date-timedelta(days=5)
    return new_date


#Task 2--> print yesterday, today, tomorrow
def yesterday_today_tomorrow():
    today=datetime.now()
    yester=today - timedelta(days=1)
    tomor=today + timedelta(days=1)
    return yester, today, tomor

#Task 3 --> drop microseconds from datetime
def drop_microsec():
    now=datetime.now()
    without_microseconds=now.replace(microsecond=0)
    return without_microseconds

#Task 4 --> two date difference in seconds
def second_differenceof_days(date1, date2):
    difference=date2-date1
    return difference.total_seconds()

#Execution 
if __name__ == "__main__":
    print("Task 1:", subtract_5_days())

    y, t, tm = yesterday_today_tomorrow()
    print("Task 2:")
    print("Yesterday:", y)
    print("Today:", t)
    print("Tomorrow:", tm)

    print("Task 3:", drop_microsec())

    d1 = datetime(2024, 1, 1, 12, 0, 0)
    d2 = datetime(2024, 1, 2, 12, 0, 0) #datetime(year, month, day, hour, minute, second)
    print("Task 4:", second_differenceof_days(d1, d2), "seconds")

