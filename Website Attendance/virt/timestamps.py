import pandas as pd


time_now = pd.Timestamp.now().strftime('%H:%M:%S')

time_late = pd.to_datetime('12:30:0').strftime('%H:%M:%S')

data = [('john', '11111','11111')]


def marked(name):
    status = "Present"
    if any(item[0] == name for item in data):
        return
    if time_now > time_late:
        return data.append((name, time_now, "Late"))

    return data.append((name, time_now, status))