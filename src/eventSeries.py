import json
import random
import os
from faker import Faker
from datetime import datetime, timedelta
faker = Faker()


class EventSeries(object):
    def __init__(self, userProfile, eventData):
        self.data = []
        minutes = eventData['DurationMinutes']
        start_time = eventData['EventTime']
        date = datetime.strptime(start_time, '%Y-%m-%d %H:%M')

        # heartRate = faker.random_int(85, 95)
        calories = 0
        steps = 0
        miles = 0

        for minute in range(minutes):
            self.data.append({
                "EventName": eventData['EventName'],
                "EventID": eventData['EventID'],
                "profile_id": userProfile['id'],
                "ProfileName": userProfile['username'],
                "EventCity": eventData['Location'],
                "HeartRate": faker.random_int(90, 180),
                "Calories": calories,
                "Steps": steps,
                "Miles": miles,
                "Timestamp": str(date)[:-3]
            })
            calories += faker.random_int(10, 20)
            steps += faker.random_int(10, 60)
            miles += faker.random_int(0, 1)
            date = date + timedelta(seconds=60)

    @staticmethod
    def generate(EVENT_SERIES_AMOUNT: int, profiles: list, events: list, registration: list):
        eventSeries = []
        for i in range(EVENT_SERIES_AMOUNT):
            choosedPersonForEvent = random.choice(registration)
            userId = choosedPersonForEvent['id']
            possibleEvents = choosedPersonForEvent['registredEvents']

            if len(possibleEvents) != 0:
                choosedEvent = random.choice(possibleEvents)

                userProfile = list(filter(lambda profile: profile.data['id'] == userId, profiles))[0].data
                eventData = list(filter(lambda event: event['EventID'] == choosedEvent, events))[0]

                eventSeries.append(EventSeries(userProfile, eventData).data)
        return eventSeries

    @staticmethod
    def pushToMQ(eventSeries: list):
        for eventData in eventSeries:
            for entry in eventData:
                exit(entry)
            # should be sendJson(entry) here

    @staticmethod
    def save(eventSeries: list):
        files = [file for file in os.listdir('data/eventSeries/')]
        for file in files:
            os.remove(os.path.join('data/eventSeries/', file))

        for eventData in eventSeries:
            with open('data/eventSeries/' +
                      eventData[0]['profile_id'] + eventData[0]['EventID'] + '.json', mode='w') as json_output:
                json.dump(eventData, json_output, indent=4, sort_keys=True)
