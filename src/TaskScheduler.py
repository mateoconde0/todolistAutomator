from src.TaskManager import TaskManager
from src.Assignee import Assignee
from src.Task import Task
from src.DateUtils import DateUtils
import json
import logging


class TaskScheduler:
    def __init__(self):
        self.assignees = []
        self.tasks = []
        self.taskAutomator = TaskManager()
        self.head = 0
        self.requirements = {}
        self.date_bin = {}

    def schedule_tasks(self):
        # need to filter tasks that are due this week
        # then filter tasks that are due next week
        # 1. number of tasks that need to be assigned
        # 2. number of people that are going to be assigned to
        # 3. Tasks will have different due dates -> bin them by week due
        # Going to start with a round robin scheduler assigning tasks with in each bin
        # if there are less tasks then people in a bin then the person will be assigned to
        # the next task in the next bin
        # It would be good in some future revision to have a way to assess difficulty/time
        # - this could be done with the use of labels
        # TODO: Consider adding a way to assign based of of time proximity and task difficulty.
        # TODO: Add error handling.
        self.__bin_tasks()
        numAssignees = len(self.assignees)
        for week in self.date_bin:
            # numTasks = len(week)
            idx = self.head
            idy = 0
            for task in self.date_bin[week]:
                if -idy == self.head:
                    idx = self.head
                idy = (numAssignees - 1) - idx
                task.assign_task(self.assignees[idy].get_assignee_id())
                self.assignees[idy].add_task(task)
                idx += 1
            self.head = idx

    def load_assignees_from_file(self, fileName):
        with open(fileName, 'r') as assigneeFile:
            assignees = json.load(assigneeFile)
        for assignee in assignees['assignees']:
            # load the assignees into the scheduler
            self.assignees.append(Assignee(assignee['full_name'], assignee['id'], assignee['email']))

    def load_assignees_from_project(self, projectName):
        self.assignees.extend(self.taskAutomator.get_collaborators_from_project(projectName))

    def load_tasks_from_project(self, project=None, section=None):
        tasks = self.taskAutomator.get_tasks_from_project(project, sectionName=section)
        for task in tasks:
            try:
                self.tasks.append(Task(task['content'], task['responsible_uid'], task['due'], task['project_id'],
                                       task['section_id']))
            except KeyError as ke:
                raise Task.TaskError(ke.msg)

    def load_tasks_from_file(self, fileName):
        with open(fileName, 'r') as taskFile:
            tasks = json.load(taskFile)
        for task in tasks['taskList']:
            try:
                self.tasks.append(Task(task['content'], task_assignee=task['responsible_uid'], task_due_date=task['due'], task_project=task['project_id'],
                                       task_section=task['section_id']))
            except KeyError as ke:
                raise Task.TaskError(ke.msg)

    def get_tasks(self):
        return self.tasks

    def get_assignees(self):
        return self.assignees

    def __bin_tasks(self):
        if len(self.tasks) == 0:
            print("Warning: There are no tasks provided")
        for task in self.tasks:
            task_date = task.get_date_string()
            if task_date:
                # has a date
                temp_date = DateUtils.string_to_date(task_date)
                temp_week = DateUtils.get_week(temp_date)
                if not self.date_bin.get(temp_week):
                    self.date_bin[temp_week] = [task]
                    continue
                self.date_bin[temp_week].append(task)

    # TODO: Consider implementing a binning function that bins off of difficulty.
