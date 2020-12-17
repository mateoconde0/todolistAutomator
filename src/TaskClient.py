from src.TaskScheduler import TaskScheduler
from src.TaskManager import TaskManager
from src.DateUtils import DateUtils
import json
import argparse
import sys
import logging
import re


class TaskClient:
    def __init__(self):
        self.task_scheduler = TaskScheduler()
        self.task_manager = TaskManager()

    def schedule_tasks(self, project, assignee_filename=None, sectionName=None, sectionID=None, task_file=None):
        # load assignees
        self.load_assignees(assignee_filename, project)
        # load tasks
        self.load_tasks(project, sectionName, task_file)
        # schedule tasks
        self.task_scheduler.schedule_tasks()

    def load_tasks(self, project, sectionName, task_file=None):
        # load tasks
        if task_file:
            self.task_scheduler.load_tasks_from_file(task_file)
        else:
            self.task_scheduler.load_tasks_from_project(project, sectionName)

    def load_assignees(self, project, assignee_filename=None):
        # load assignees
        if assignee_filename:
            self.task_scheduler.load_assignees_from_file(assignee_filename)
        else:
            self.task_scheduler.load_assignees_from_project(project)

    def write_scheduled_tasks(self, filename, mode='w'):
        """
        Writes scheduled tasks, with assignees.
        """
        scheduler_dict = {"assignees": [], "taskList": [], "head": self.task_scheduler.head,
                          "requirements": self.task_scheduler.requirements}
        assignees = self.task_scheduler.get_assignees()
        for assignee in assignees:
            assignee_dict = assignee.__dict__
            tmp_task_list = []
            for task in assignee_dict['tasks']:
                temp_task_dict = task.__dict__
                temp_task_dict['difficulty'] = str(temp_task_dict['difficulty'])
                scheduler_dict["taskList"].append(temp_task_dict)
                tmp_task_list.append(temp_task_dict)
            assignee_dict['tasks'] = tmp_task_list
            scheduler_dict['assignees'].append(assignee_dict)
        filename = 'scheduler_' + filename
        if not filename.endswith('.json'):
            logging.warning("File must be a json file. Writing to " + filename + ".json")
            filename += ".json"
        with open(filename, mode) as scheduler_file:
            json.dump(scheduler_dict, scheduler_file)

    def write_assignees(self, filename=None, mode='w'):
        """
        File to write the current list of assignees back to the system. Updates the current head of the scheduler.
        """
        assignees = self.task_scheduler.get_assignees()
        assignee_dict = {"assignees": [], "head": self.task_scheduler.head}
        for assignee in assignees:
            assignee_dict['assignees'].append(assignee.__dict__)
        if filename is None:
            filename = 'project_assignees_' + DateUtils.get_date() + '.json'
        with open(filename, mode) as assignee_file:
            json.dump(assignee_dict, assignee_file)

    def write_tasks(self, project: str, sectionName: str = None, sectionID=None, filename=None, mode='w'):
        """
        Write system level tasks to the system.
        :param project: project that you are writing tasks
        :param sectionName: sectionName within the project
        :param sectionID: sectionID within the project
        """
        tasks = self.task_scheduler.tasks
        task_dict = {"taskList": [], "project": str(project), "sectionName": str(sectionName),
                     "sectionID": str(sectionID)}
        for task in tasks:
            task_dict["taskList"].append(task.__dict__)
        if not filename:
            filename = 'tasks_' + str(project)
            if not sectionName:
                filename += "_" + str(sectionName)
            if not sectionID:
                filename += "_" + str(sectionID)
            filename += DateUtils.get_date() + ".json"
        with open(filename, mode) as task_file:
            json.dump(task_dict, task_file)

    def add_tasks_to_todoist(self):
        tasks = self.task_scheduler.get_tasks()
        self.task_manager.add_task_from_list(tasks)

    def commit_tasks(self):
        # TODO: add error handling
        # example response:
        # {'temp_id_mapping': {'f2134978-c897-11ea-a36e-3c15c2c55a26': 4043944309}, 'sync_status': {'f2134b58-c897-11ea-a36e-3c15c2c55a26': 'ok'}, 'sync_token': '2yBvSL0ZCZ-Nt0aTNveijDNPQLOJAmPxRxKdOuZ43coe-4qc4qtla-sFmd87hlCnb7gRjM8lWAFeGNBFUeGjqVY47fc0ZsEwDYv8zi0xevSZqjc', 'full_sync': False, 'items': [{'id': 4043944309, 'content': 'TEST2', 'checked': 0, 'project_id': 2237030900, 'user_id': 11869293, 'in_history': 0, 'priority': 1, 'collapsed': 0, 'date_added': '2020-07-18T01:42:31Z', 'date_completed': None, 'assigned_by_uid': 11869293, 'responsible_uid': 11869293, 'added_by_uid': 11869293, 'is_deleted': 0, 'sync_id': 4043944309, 'parent_id': None, 'child_order': 9, 'section_id': 13882916, 'labels': [], 'day_order': -1, 'due': None}], 'projects': [], 'project_notes': [], 'notes': [], 'filters': [], 'labels': [], 'live_notifications': [], 'live_notifications_last_read_id': 2309418030, 'reminders': [], 'day_orders_timestamp': '1591291374.39', 'day_orders': {}, 'collaborators': [], 'collaborator_states': [], 'due_exceptions': [], 'sections': []}
        self.task_manager.commit_tasks()

def command_regex(command: str, pattern=re.compile(r"setup|assign|visual|help")) -> bool:
    command = command.lower()
    if pattern.match(command) is not None:
        return command
    else:
        raise argparse.ArgumentTypeError


def main():
    args, assigneeFile, commit, dontWrite, logFile, logLevel, parser, project, sectionName, taskFile, writeAssignees, writeTasks = getArguments()

    logger = logging.basicConfig(filename=logFile, level=logLevel)
    client = TaskClient()
    if args.command == 'setup':
        # Set up is used for creating files to run the scheduler off of.
        # create a scheduler file
        client.load_assignees(project, assigneeFile)
        client.load_tasks(project, sectionName, taskFile)
        client.write_scheduled_tasks(project + "_" + sectionName + "_" + DateUtils.get_date() + "_scheduler.json")
        # TODO: Verify that this does its intended job. 
    elif args.command == 'assign':
        client.schedule_tasks(project, sectionName=sectionName, task_file=taskFile, assignee_filename=assigneeFile)
        client.add_tasks_to_todoist()
        if commit:
            client.commit_tasks()
        if not dontWrite:
            client.write_scheduled_tasks(project + "_" + sectionName + "_" + DateUtils.get_date() + "_scheduler.json")
        if writeTasks:
            client.write_tasks(project, sectionName)
        if writeAssignees:
            client.write_assignees()
    elif args.command == 'visual':
        logger.info("Visual is not currently implemented")
        exit(0)
        print("Welcome to TaskAutomator")
        cont = True
        while cont is True:
            print("Menu:\n"
                  "\t1. add tasks\n"
                  "\t2. remove tasks\n"
                  "\t3. view tasks\n"
                  "\t4. print tasks\n"
                  "\t5. write tasks")
            response = input()
            if response is None:
                return -1
            else:
                response = int(response)
                if 0 < response < 5:
                    return -1
            if response == 1:
                pass
            elif response == 2:
                pass
            elif response == 3:
                pass
            elif response == 4:
                pass
            elif response == 5:
                pass
    elif args.command == "help":
        parser.print_help()
    else:
        logger.error("Invalid command argument! Options are ")


def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('COMMAND', type=command_regex,
                        help="Command to run the task client. Options are SETUP, ASSIGN, VISUAL, HELP")
    parser.add_argument('-p', '--project', type=str, dest='project')
    parser.add_argument('-s', '--sectionName', type=str, dest='sectionName')
    parser.add_argument('-d', '--dontcommit', action="store_true",
                        help="Used to not commit tasks and only print.")
    parser.add_argument('-tf', '--taskFile', type=str, dest='taskFile')
    parser.add_argument('-af', '--assigneeFile', type=str, dest='assigneeFile')
    parser.add_argument('-ll', '--logLevel', type=str, dest='logLevel', nargs='?', const=logging.ERROR,
                        default=logging.ERROR)
    parser.add_argument('-lf', '--logFile', type=str, dest='logFile', nargs='?', const='TaskClient.log',
                        default='TaskClient.log')
    parser.add_argument('-dw', '--dontWrite', dest='dontWrite', action="store_true",
                        help="Don't write a TaskScheduler File.")
    parser.add_argument('-wt', '--writeTasks', dest='writeTasks', action="store_true",
                        help="Write tasks that are being assigned to a file")
    parser.add_argument('-wa', '--writeAssignees', dest='writeAssignees', action="store_true",
                        help="Write tasks that are being assigned to a file")
    args = parser.parse_args(sys.argv[1:])  # get the command line arguments
    logLevel = args.logLevel
    logFile = args.logFile
    commit = args.commit
    project = args.project
    sectionName = args.sectionName
    taskFile = args.taskFile
    assigneeFile = args.assigneeFile
    dontWrite = args.dontWrite
    writeTasks = args.writeTasks
    writeAssignees = args.writeAssignees
    return args, assigneeFile, commit, dontWrite, logFile, logLevel, parser, project, sectionName, taskFile, writeAssignees, writeTasks


def print_assignees():
    client = TaskClient()
    client.task_scheduler.load_assignees_from_file('test_assignees.json')
    client.write_assignees('test_assignees.json')


if __name__ == '__main__':
    main()
