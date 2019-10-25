from faker import Faker
from src.data import city_list, activity_list, category_list, city_abb
import random
import re
import json
import string
import csv
import uuid
faker = Faker()

USERID_OFFSET = 50000


class Profile(object):
    userId = 0

    def __init__(self, all_friends: list, coworkers: list, PROFILES_AMOUNT: int):
        self.mq = []
        profile = faker.profile()
        Profile.userId += 1

        id = f'P{USERID_OFFSET + Profile.userId}'
        street = profile.get('address').splitlines()[0]
        heap = profile.get('address').splitlines()[1].split(' ')
        zipcode = heap.pop()
        city = heap.pop()
        gender = profile.get('sex')

        self.data = {
            'name': profile.get('name'),
            'id': id,
            'city': random.choice(city_list),
            'address': re.sub(r'(.*)(.*),(.*)', lambda match: match.group(1), profile.get('address')),
            'height': float("{0:.2f}".format(random.uniform(5, 6.5))),
            'weight': faker.random_int(100, 190),
            'age': faker.random_int(18, 60),
            'pic': 'fb.com/Name/' + profile.get('username') + '.png',
            'video': 'fb.com/Name/' + profile.get('username') + '.mov',
            'socialNetwork': 'fb.com',
            'socialNetworkGrant': 'Y',
            'interestedEvents': random.choices(activity_list, k=4),
            'categories': random.choice(category_list),
            'password': ''.join(random.choice(string.ascii_lowercase) for i in range(8)),
            'interested_making_new_f': random.choice([True, False]),
            'interested_new_recommendations': random.choice([True, False]),
            'girl_power': False if gender == 'M' else random.choice([True, False])
        }
        name, surname, *rest = self.data['name'].split(' ')
        self.data['username'] = name[:3].lower() + surname[:3].lower()

        # generate friends
        amount = faker.random_int(0, 4)
        generated_friends = list(filter(
            lambda x: x != f'P{USERID_OFFSET + Profile.userId}',
            random.sample([f'P{USERID_OFFSET + x}' for x in range(1, PROFILES_AMOUNT)], amount)
        ))
        all_friends[Profile.userId - 1].extend(generated_friends)
        for friend in generated_friends:
            index = int(friend[2:]) - 1
            all_friends[index].extend([id])
        self.mq.append({
            "friends": list(set(all_friends[Profile.userId - 1])),
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })
        self.data['friends'] = all_friends[Profile.userId - 1]

        # generate coworkers
        amount = faker.random_int(0, 2)
        generated_coworkers = list(filter(
            lambda x: x != f'P{USERID_OFFSET + Profile.userId}',
            random.sample([f'P{USERID_OFFSET + x}' for x in range(1, PROFILES_AMOUNT)], amount)
        ))
        coworkers[Profile.userId - 1].extend(generated_coworkers)
        for friend in generated_coworkers:
            index = int(friend[2:]) - 1
            coworkers[index].extend([id])
        self.mq.append({
            "coworkers": list(set(coworkers[Profile.userId - 1])),
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })
        self.data['coworkers'] = coworkers[Profile.userId - 1]

        self.mq.append({
            "adress": {
                "street": street,
                "city": city,
                "zip": zipcode
            },
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })

        self.mq.append({
            "info": {
                'height': self.data['height'],
                'weight': self.data['weight'],
                'age': self.data['age']
            },
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })

        self.mq.append({
            "credentials": {
                'username': self.data['username'],
                'password': self.data['password']
            },
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })

        self.mq.append({
            "socialNetwork": {
                'name': self.data['socialNetwork'],
                'pic': self.data['pic'],
                'video': self.data['video'],
                'socialNetworkGrant': self.data['socialNetworkGrant']
            },
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })

        self.mq.append({
            "interested_events": self.data['interestedEvents'],
            "categories_interested": self.data['categories'],
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })

        self.mq.append({
            "recommendations": {
                "follow_friends": self.data['interested_making_new_f'],
                "event_suggestion": self.data['interested_new_recommendations'],
                "girl_power": self.data['girl_power']
            },
            "profile_id": id,
            "uuid": str(uuid.uuid4())
        })

    @staticmethod
    def generate(PROFILES_AMOUNT: int):
        all_friends = [[] for i in range(PROFILES_AMOUNT)]
        coworkers = [[] for i in range(PROFILES_AMOUNT)]
        profiles = []
        for i in range(PROFILES_AMOUNT):
            profiles.append(Profile(all_friends, coworkers, PROFILES_AMOUNT))
        for friends in all_friends:
            friends = list(dict.fromkeys(friends))
        for coworker in coworkers:
            coworker = list(dict.fromkeys(coworker))
        return profiles

    @staticmethod
    def pushToMQ(profiles: list):
        for profile in profiles:
            for message in profile.mq:
                print(message)
                # should be sendJson(message) here

    @staticmethod
    def save(profiles: list):
        with open('data/vertex-profiles.csv', mode='w') as csv_output:
            csv_writer = csv.writer(csv_output, delimiter=';')
            csv_writer.writerow([
                '~id', 'name:String', 'age:Int', 'city:String', 'int_new_fr:Bool', 'int_new_rec:Bool', 'girl_pwr:Bool', '~label'
            ])
            for profile in profiles:
                csv_writer.writerow([
                    profile.data['id'],
                    profile.data['username'],
                    profile.data['age'],
                    city_abb[profile.data['city']],
                    profile.data['interested_making_new_f'],
                    profile.data['interested_new_recommendations'],
                    profile.data['girl_power'],
                    'profile'
                ])

        with open('data/edge-profiles.csv', mode='w') as csv_output:
            csv_writer = csv.writer(csv_output, delimiter=';')
            csv_writer.writerow(['~id', '~from', '~to', '~label'])
            counter = 0
            for profile in profiles:
                for friend in profile.data['friends']:
                    csv_writer.writerow([
                        'F' + str(counter),
                        profile.data['id'],
                        friend,
                        'friend',
                    ])
                    counter += 1
                for coworker in profile.data['coworkers']:
                    csv_writer.writerow([
                        'C' + str(counter),
                        profile.data['id'],
                        coworker,
                        'coworker',
                    ])
                    counter += 1

        for profile in profiles:
            with open('data/profiles/' + profile.mq[0]['profile_id'] + '.json', mode='w') as json_output:
                json.dump(profile.mq, json_output, indent=4, sort_keys=True)
