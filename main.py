#!/usr/bin/python
from src.profiles import Profile
from src.events import Event
from src.registration import Registration
from src.eventSeries import EventSeries

PROFILES_AMOUNT = 500
EVENT_SERIES_AMOUNT = 50


if __name__ == '__main__':
    profiles = Profile.generate(PROFILES_AMOUNT)
    # Profile.pushToMQ(profiles)
    Profile.save(profiles)

    events = Event.generate()
    # Event.pushToMQ(events)
    Event.save(events)

    registration = Registration.generate(profiles, events)
    # Registration.pushToMQ(registration)
    Registration.save(registration)

    eventSeries = EventSeries.generate(EVENT_SERIES_AMOUNT, profiles, events, registration)
    # EventSeries.pushToMQ(eventSeries)
    EventSeries.save(eventSeries)
