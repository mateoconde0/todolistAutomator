from enum import Enum
import logging

class Task:
    def __init__(self, task_content: str, task_assignee: str = None, task_due_date: str = None,
                 task_project: str = None, task_section: str = None, **kwargs):
        self.content = task_content
        self.responsible_uid = task_assignee
        self.due = self.create_date(**task_due_date)
        self.project_id = task_project
        self.section_id = task_section
        self.difficulty = TaskDifficultyEnum.EASY
        # TODO: Consider moving towards a item_model to store task data, and use class to store metadata.

    def __str__(self):
        return self.content

    # def __repr__(self):
    #     if self.task_due_date:
    #         return self.task_content + " " + str(self.task_due_date)
    #     else:
    #         return self.task_content
    def __repr__(self):
        return str(self.__dict__)

    def get_task_details(self):
        """
        Represents the task as a dictionary. Useful for adding tasks.
        :return: The task dictionary
        """
        opts = {"project_id": "", "section_id": "", "responsible_uid": ""}

        if self.project_id:
            opts['project_id'] = self.project_id
        else:
            opts.pop('project_id')

        if self.responsible_uid:
            opts['responsible_uid'] = self.responsible_uid
        else:
            opts.pop('responsible_uid')

        # if self.task_due_date:
        #     opts['due'] = self.task_due_date
        # else:
        #     opts.pop('due')

        if self.section_id:
            opts['section_id'] = self.section_id
        else:
            opts.pop('section_id')

        return self.content, opts

    @staticmethod
    def create_date(date: str = None, string: str = "", **kwargs) -> dict:
        # Example date format "due": {"date": "2020-07-17", "timezone": null, "string": "every other fri",
        # "lang": "en", "is_recurring": true}
        date_format = {"date": "", "timezone": None, "string": "", "lang": "en", "is_recurring": False}
        for key, value in kwargs.items():
            if date_format.get(key) is not None:
                if isinstance(value, type(date_format[key])):
                    date_format[key] = value
                elif date_format[key] == "timezone" and isinstance(value,str):
                    date_format[key] = value
                else:
                    raise TypeError("Problem adding " + key + " to the date format because " + type(value) +
                                    " cannot be converted to " + type(date_format[key]))
        if date:
            date_str = date
            date_format["date"] = date_str
        if string:
            date_format["string"] = string

        return date_format

    def get_date_string(self):
        if self.due:
            return self.due['date']
        else:
            return None

    def get_task_difficulty(self):
        return self.difficulty

    def assign_task(self, assignee):
        self.responsible_uid = assignee


class TaskError(KeyError):
    def __init__(self, msg):
        super().__init__(msg)


class TaskDifficultyEnum(Enum):
    EASY = 0.5
    MEDIUM = 0.75
    HARD = 1

    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)
