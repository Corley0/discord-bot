import asyncio, json, discord
config = {}

def parse_time(raw):
    if raw[-1] == "m":
        return int(raw[:-1])
    elif raw[-1] == "h":
        return int(raw[:-1]) * 60
    elif raw[-1] == "d":
        return int(raw[:-1]) * 60 * 24

def parse_time_str(raw):
    if raw[-1] == "m":
        if raw[:-1] == "1":
            return raw[:-1]+" Minute"
        else:
            return raw[:-1]+" Minutes"
    elif raw[-1] == "h":
        if raw[:-1] == "1":
            return raw[:-1]+" Hour"
        else:
            return raw[:-1]+" Hours"
    elif raw[-1] == "d":
        if raw[:-1] == "1":
            return raw[:-1]+" Day"
        else:
            return raw[:-1]+" Days"

def convert_to_unparsed(minutes):
    if minutes < 60:
        return f"{minutes}m"
    elif minutes < 60 * 24:
        hours = minutes // 60
        return f"{hours}h"
    else:
        days = minutes // (60 * 24)
        return f"{days}d"

def load_json():
    with open('config.json', 'r', encoding="utf-8") as file:
        global config
        config = json.load(file)
        file.close()