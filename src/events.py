from src.data import city_list, event_details, city_codes
from faker import Faker
import random
import json
import csv
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
faker = Faker()


class Event(object):
    def __init__(self, day, citycode, event, time):
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        date_after_three_month = date.today() + relativedelta(months=3)
        first_day_after = date_after_three_month.replace(day=1)
        second_day_after = date_after_three_month.replace(day=2)
        third_day_after = date_after_three_month.replace(day=3)

        possible_dates = [
            yesterday, today, tomorrow, first_day_after, second_day_after, third_day_after
        ]

        self.data = {
            'EventName': event['name'],
            'Category': random.choice(event['categories']),
            'Description': faker.text(),
            'AgeLimit': faker.random_int(18, 60),
            'Reward': random.choice([100, 200, 300]),
            'EventTime': str(possible_dates[day]),
            'Location': city_codes['00' + str(citycode)],
            'EventOrganization': 'abc corp',
            'DurationMinutes': event['duration_minutes']
        }
        if '1k' in self.data['EventName'] or '50m' in self.data['EventName']:
            self.data['Reward'] = 100
        if '5k' in self.data['EventName'] or '100m' in self.data['EventName']:
            self.data['Reward'] = 200
        if '10k' in self.data['EventName'] or '200m' in self.data['EventName']:
            self.data['Reward'] = 300

        self.data['EventTime'] += ' ' + time
        self.data['GirlPower'] = time in event['girlpower_time']

        self.data['EventID'] = 'E00' + str(citycode) + \
            event['id'] + time[:2] + ('01' if self.data['GirlPower'] else '00')

    @staticmethod
    def generate():
        events = []
        for day in range(6):
            for citycode in range(1, 8):
                for event in event_details:
                    for reg_time in event['regular_time']:
                        events.append(Event(day, citycode, event, reg_time).data)
                    for grl_time in event['girlpower_time']:
                        events.append(Event(day, citycode, event, grl_time).data)
        return events

    @staticmethod
    def pushToMQ(events: list):
        for event in events:
            print(event)
            # should be sendJson(event) here

    @staticmethod
    def save(events: list):
        with open('data/vertex-events.csv', mode='w') as csv_output:
            csv_writer = csv.writer(csv_output, delimiter=';')
            csv_writer.writerow(['~id', 'name:String', 'city:String', 'girl_power:Bool', '~label'])
            # csv_writer.writerow(['~id', 'name:String', 'city:String', '~date:String'])
            for event in events:
                csv_writer.writerow([
                    event['EventID'],
                    event['EventName'],
                    event['Location'],
                    event['GirlPower'],
                    'event'
                    # event['EventTime'],
                ])

        with open('data/events.json', mode='w') as json_output:
            json.dump(events, json_output, indent=4, sort_keys=True)
