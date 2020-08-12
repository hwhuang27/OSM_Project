
# opening_hours.py

import sys
import numpy as np
import pandas as pd
from pprint import pprint

day_of_week = [
    "Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"
]

opening_hours_template = {
    "Mo": None, 
    "Tu": None, 
    "We": None, 
    "Th": None, 
    "Fr": None, 
    "Sa": None, 
    "Su": None
}

# Given a day of week in abbreviation, return the index of the day
def day2num(day):
    return day_of_week.index(day)

# Return the number of hours in an interval of opening hours
def getHours(string):
    if len(string) <= 0 or string == 'off' or string == 'closed':
        return 0.0
    intervals = string.split(',')
    sign = 1
    for itvl in intervals:
        lst = itvl.split('-')
        if len(lst) == 2:
            start, end = lst
        elif len(lst) == 1:
            start = lst[0]
            if '+' in start:
                start = start.replace('+', '')
                start_H, start_M = [int(x) for x in start.split(':')]
                return (24 * 60 - 24 * start_H - start_M) / 60
        else:
            return 0.0
        try:
            start_H, start_M = [int(x) for x in start.split(':')]
            end_H, end_M = [int(x) for x in end.split(':')]
        except Exception as e:
            return 0.0
        start_min, end_min = start_H * 60 + start_M, end_H * 60 + end_M
        end_min += 24 * 60 if end_min < start_min else 0
        total_minutes = end_min - start_min
        # return [total_minutes // 60, total_minutes % 60]
        return total_minutes / 60

# Parse the opening hour
def opening_hour_parser(s):
    if '24/7' in s:
        opening_hour = opening_hours_template.copy()
        for key in opening_hour:
            opening_hour[key] = 24.0
        return opening_hour
    s = s.replace('; ', ';')
    s = s.replace(', ', ',')
    lst = [x.strip() for x in (s.split(';') if ';' in s else s.split(','))]
    opening_hour = opening_hours_template.copy()
    for itvl in lst:
        segs = itvl.split(' ')
        segs[0] = segs[0].replace(',', '-')
        days = segs[0].split('-')
        if days[0] == 'PH':
            continue
        elif len(days) > 1 and days[1] == 'PH':
            days[1] = days[0]
        if days[0] not in day_of_week or days[-1] not in day_of_week:
            h = getHours(segs[0])
            for key in opening_hour:
                opening_hour[key] = h
            return opening_hour
        start, end = day2num(days[0]), day2num(days[-1]) + 1
        end += len(day_of_week) if end < start else 0
        for idx in range(start, end + 1):
            if len(segs) > 1:
                segs[1] = segs[1].replace('+', '')
                opening_hour[day_of_week[idx % len(day_of_week)]] = getHours(segs[1])
            else:
                opening_hour[day_of_week[idx % len(day_of_week)]] = getHours("")
    for key in opening_hour:
        if opening_hour[key] == None:
            opening_hour[key] = 0.0
    return opening_hour

# python3 get_opening_hours.py ./osm/amenities-vancouver.json.gz
def main():
    input_file = sys.argv[1]
    data = pd.read_json(input_file, lines = True)
    # print(data)


    """ Extract opening hours of food amenities """
    food = data[data['amenity'].str.contains("restaurant|food|cafe|pub|bar|ice_cream|food_court|bbq|bistro") & ~data['amenity'].str.contains("disused")]
    food = food.dropna()
    food = food[food.apply(lambda x: 'opening_hours' in x['tags'], axis = 1)]

    # # Test
    # for i in range(len(food)):
    #     print(i, food['tags'].iloc[i]['opening_hours'])
    #     print(opening_hour_parser(food['tags'].iloc[i]['opening_hours']))

    food['opening_hours'] = food.apply(
        lambda x: opening_hour_parser(x['tags']['opening_hours']), 
        axis = 1
    )

    food['opening_hours_per_week'] = food.apply(
        lambda x: sum([x['opening_hours'][day] for day in day_of_week]), 
        axis = 1
    )
    food = food[[
        'lat', 
        'lon', 
        'amenity', 
        'tags', 
        'opening_hours', 
        'opening_hours_per_week'
    ]]
    food = food[food['opening_hours_per_week'] >= 10.0]
    food = food.reset_index(drop = True)
    print(food)

    # # Test
    # for i in range(len(food)):
    #     if food.iloc[i]['opening_hours_per_week'] == 0.0:
    #         print(i, food['tags'].iloc[i]['opening_hours'])
    #         print(food.iloc[i]['opening_hours'])

    food.to_json("opening_hours.json", orient = 'records', lines = True)



if __name__ == '__main__':
    main()
