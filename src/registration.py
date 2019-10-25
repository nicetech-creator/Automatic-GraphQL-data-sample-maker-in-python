import json
import uuid
import random
import csv
from faker import Faker
faker = Faker()


class Registration(object):
    def __init__(self, user_id, events):
        self.data = {
            "registredEvents": events,
            "id": user_id,
            "uuid": str(uuid.uuid4())
        }

    @staticmethod
    def generate(profiles: list, events: list):
        profile_ids = list(map(lambda profile: profile.data['id'], profiles))
        event_ids = list(map(lambda event: event['EventID'], events))

        profiles_to_events = dict.fromkeys(profile_ids)

        history = []
        for i in profile_ids:
            user = random.choice(profile_ids)
            selected_events = list(dict.fromkeys(random.choices(event_ids, k=faker.random_int(1, 3))))

            if profiles_to_events[user] is None:
                profiles_to_events[user] = selected_events
            else:
                for ev in selected_events:
                    if ev in profiles_to_events[user]:
                        selected_events.remove(ev)

            history.append(Registration(user, selected_events).data)
        return history

    @staticmethod
    def pushToMQ(history: list):
        for reg in history:
            print(reg)
            # should be sendJson(reg) here

    @staticmethod
    def save(history: list):
        counter = 0
        with open('data/edge-events.csv', mode='w') as csv_output:
            csv_writer = csv.writer(csv_output, delimiter=';')
            csv_writer.writerow(['~id', '~from', '~to', '~label'])
            for data in history:
                for event in data['registredEvents']:
                    csv_writer.writerow([
                        'R' + str(counter),
                        data['id'],
                        event,
                        'register'
                    ])
                    counter += 1

        with open('data/history.json', mode='w') as json_output:
            json.dump(history, json_output, indent=4, sort_keys=True)
