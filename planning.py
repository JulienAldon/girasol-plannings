from __future__ import annotations

# Time range
## Une time range est une zone de temps (start, end) sur laquelle des taches peuvent être assignés

# Tasks
## Une tache a des besoin de user / groups (needs)

# Group
## Un groupe est une association de 2 ou plus user

# User
## Un user est un bénévole aved des préférences, des timerange de présences
import datetime
import csv
import time
import math
from typing import Type

class Task:
    name: str
    user_needs: int
    mobilisation_time: int
    
    def __init__(self, _name: str, _user_needs: int, _mobilisation_time: int):
        self.name = _name
        if _user_needs != '':
            self.user_needs = int(_user_needs)
        if _mobilisation_time != '':
            self.mobilisation_time = int(_mobilisation_time)
    
    def __repr__(self):
        return f'{self.name}'

class Timerange:
    name: str
    start: datetime.datetime
    end: datetime.datetime

    def is_in_range(self, timerange):
        return timerange.start >= self.start and timerange.end <= self.end 

    def __init__(self, _name: str, _start: str, _end: str):
        self.name = _name
        self.start = datetime.datetime.strptime(_start, "%Hh%M")
        self.end = datetime.datetime.strptime(_end, "%Hh%M")

class User:
    name: str
    availability: list[Timerange]
    preferences: list[Task]
    shifts: list[Shift] = []

    def assign_shifts(self, shifts: Shift):
        self.shifts.append(shifts)

    def is_available(self, timerange: Timerange):
        has_availability = []
        is_in_planning = []
        # print(list(map(lambda x: x.name, self.plannings)))
        for a in self.availability:
            has_availability.append(a.is_in_range(timerange))
        for shift in self.shifts:
            # print(self in shift.users)
            is_in_planning.append(self in shift.users)
        return (all(has_availability) or len(has_availability) <= 0) and (not all(is_in_planning) or len(is_in_planning) <= 0)

    def __init__(self, _name, _availability, _preferences):
        self.name = _name
        self.availability = _availability
        self.preferences = _preferences
    
    def __repr__(self):
        return f'{self.name}'

class Shift(Timerange):
    users: list[User]

    def __init__(self, _name: str, _start: str, _end: str, _users: list[User]):
        super().__init__(_name, _start, _end)
        self.users = _users

    def __repr__(self):
        return f'{self.start} {self.end} {self.users}'

class Planning(Timerange):
    task: Task
    shifts: list[Shift] = []

    def find_available_users(self, users: list[User], nb_users: int = 2) -> list[User]:
        result = []
        for user in users:
            # print(user, user.is_available(self))
            if user.is_available(self) and len(result) < nb_users:
                result.append(user)
        return result

    def create_shifts(self, all_users: list[User]):
        timedelta = self.end - self.start
        nb_shift = timedelta / datetime.timedelta(minutes=self.task.mobilisation_time)
        for i in range(0, math.ceil(nb_shift)):
            start = self.start + datetime.timedelta(minutes=(i) * self.task.mobilisation_time)
            end = self.start + datetime.timedelta(minutes=(i+1) * self.task.mobilisation_time)
            users = self.find_available_users(all_users, self.task.user_needs)
            shift = Shift(self.task.name, start.strftime("%Hh%M"), end.strftime("%Hh%M"), users)
            self.shifts.append(shift)
            for user in users:
                user.assign_shifts(shift)
            print(shift, users)

    def __init__(self, _name, _start, _end, _task, all_tasks):
        super().__init__(_name, _start, _end)
        self.task = find_resources_by_name(_task, all_tasks)[0]

def load_csv(filename: str):
    with open(filename) as csvfile:
        result = []
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            result.append(row)
        return result[1:]

def find_resources_by_name(resources: list, all_resources: list) -> list[Task]:
    task = list(filter(lambda x: x.name in resources, all_resources))
    return task

def load_users(users: list, tasks: list[Task], timeranges: list[Timerange]) -> list[User]:
    loadedusers = []
    for row in users:
        preferences = find_resources_by_name(row[2].split(', '), tasks)
        availability = find_resources_by_name(row[1].split(', '), timeranges)
        loadedusers.append(User(row[0], availability, preferences))
    return loadedusers

def load_timerange(timeranges: list):
    result = []
    for row in timeranges:
        result.append(Timerange(row[0], row[1], row[2]))
    return result

def load_tasks(tasks: list):
    result = []
    for row in tasks:
        result.append(Task(row[0], row[1], row[2]))
    return result

def load_plannings(shifts: list, all_tasks: list[Task]):
    result = []
    for row in shifts:
        result.append(Planning(row[0], row[1], row[2], row[3], all_tasks))
    return result



    # Create groups (2 users) taking into account friends from previously created users.
    # For each shifts : 
        # For each Tasks
            # Create planning

config_timeranges = load_timerange(load_csv('timerange.csv'))
config_tasks = load_tasks(load_csv('tasks.csv'))

users = load_users(load_csv('users.csv'), config_tasks, config_timeranges)

def main():
    plannings_to_create = load_plannings(load_csv('plannings.csv'), config_tasks)
    for plan in plannings_to_create:
        plan.create_shifts(users)

main()