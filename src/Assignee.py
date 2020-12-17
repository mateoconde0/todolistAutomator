from src.Task import TaskDifficultyEnum
import logging

class Assignee:
    def __init__(self, name, uid, email, task_load=0, tasks=None, timezone='America/New_York'):
        if tasks is None:
            tasks = []
        self.full_name = name
        self.id = uid
        self.task_load = task_load
        self.tasks = tasks
        self.timezone = timezone
        self.email = email

    def add_task(self, task):
        if task.get_task_difficulty() in TaskDifficultyEnum:
            self.tasks.append(task)
            self.__compute_task_load()
        else:
            raise ValueError("Invalid Difficulty Level. Difficulty levels are easy, medium, hard")

    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.pop(task)
        else:
            print("Task is not included in assigned tasks for " + self.full_name)

    def __compute_task_load(self):
        """
        Compute the task load of the assignee. Sets the task_load instance variable.
        Note there are several different types of difficulties defined by the TaskDifficulty Enum:
        - easy: 0.5
        - medium: 0.75
        - hard: 1

        Task load is calculated using a weighted average.
        """
        task_load = 0
        for task in self.tasks:
            try:
                print(str.upper(str(task.get_task_difficulty)))
                task_load += TaskDifficultyEnum.EASY.value
            except KeyError:
                print("Invalid task. Please check TaskDifficultyEnum")
                raise KeyError
        return task_load / len(self.tasks)

    def get_assignee_id(self):
        return self.id

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __repr__(self):
        return self.full_name + " : " + str(self.id)

    def __str__(self):
        return str(self.id)
