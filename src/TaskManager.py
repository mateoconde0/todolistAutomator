from todoist.api import TodoistAPI, json_default, SyncError, CollaboratorsManager, CollaboratorStatesManager
import json
import logging
from src.Task import Task
from src.Assignee import Assignee


class ProjectError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class SectionError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class TaskManager:
    def __init__(self):
        with open('.app.pass', 'r') as passFile:
            api_key = passFile.readline().strip()
        self.api = TodoistAPI(api_key)
        self.api.sync()
        # get the project into json format
        self.projects = self.__get_project_data()
        self.sections = self.__get_sections_data()
        self.collaborators = self.__get_collaborators()
        self.collaborator_states = self.__get_collaborator_states()

    def __get_project_data(self):
        tmp_projects = {}
        for project in self.api.projects.all():
            tmp_projects[project['name']] = self.api.projects.get_data(project['id'])
        return tmp_projects

    def __get_sections_data(self):
        temp_sections = {}
        for section in self.api.sections.all():
            temp_sections[section['name']] = section
        return temp_sections

    def __get_collaborators(self):
        tmp_collaborators = {}
        for collaborator in self.api.collaborators.state['collaborators']:
            collaborator_info = collaborator.__dict__.copy()
            collaborator_info = collaborator_info['data']
            if collaborator_info.get('image_id') is not None:
                collaborator_info.pop('image_id')
            collaborator_info['task_load'] = 0
            collaborator_info['tasks'] = []
            tmp_collaborators[collaborator['id']] = collaborator_info
        return tmp_collaborators

    def __get_collaborator_states(self):
        tmp_collaborator_states = []
        for collaborator_state in self.api.collaborator_states.state['collaborator_states']:
            tmp_collaborator_states.append(collaborator_state)
        return tmp_collaborator_states

    def get_projects(self):
        return self.projects

    def get_sections(self):
        return self.sections

    def get_project_id(self, project_name):
        try:
            temp_project = self.projects.get(project_name)
            if temp_project is None:
                raise ProjectError('Project ' + project_name + 'does not exist')
            return temp_project['project']['id']
        except ProjectError:
            print(ProjectError)

    def get_section_id(self, section_name):
        try:
            temp_section = self.sections.get(section_name)
            if temp_section is None:
                raise SectionError('Section ' + section_name + 'does not exist')
            return temp_section['id']

        except SectionError:
            print(SectionError)

    def get_section(self, section):
        return self.sections.get(section)

    def get_sections(self):
        return self.sections

    def get_project(self, project_name):
        return self.projects.get(project_name)

    def get_section_from_project(self, project, section):
        temp_project = self.get_project(project)
        temp_section = [x for x in temp_project['sections'] if x['name'] == section]
        temp_section_data = self.api.sections.get(temp_section[0]['id'])
        return temp_section_data

    def get_tasks_from_project(self, project, sectionId=None, sectionName=None):
        temp_project = self.get_project(project)
        if sectionId or sectionName:
            if sectionName:
                sectionId = self.get_section_id(sectionName)
            temp_project_tasks = [x for x in temp_project['items'] if x['section_id'] == sectionId]
            return temp_project_tasks
        else:
            return temp_project['items']

    def get_collaborators_from_project(self, project_name):
        project_id = self.get_project_id(project_name)
        collaborators = []
        for collaborator_state in self.collaborator_states:
            if collaborator_state['project_id'] == project_id and collaborator_state['state'] == 'active':
                collaborators.append(collaborator_state['user_id'])
        if len(collaborators) > 0:
            for i, collaborator in zip(range(len(collaborators)), collaborators):
                collaborator_info = self.collaborators[collaborator]
                collaborators[i] = Assignee(collaborator_info['full_name'], collaborator_info['id'],
                                            collaborator_info['email'], collaborator_info['task_load'],
                                            collaborator_info['tasks'], collaborator_info['timezone'])
        else:
            # TODO: add error handling
            pass
        return collaborators

    def get_collaborator_from_user_id(self, user_id):
        return self.collaborators[user_id]

    def add_task(self, task_content, task_assignee: str = None, task_due_date: str = None, task_project: str = None,
                 task_section: str = None):
        opts = {'responsible_uid': '', 'due': '', 'project_id': '', 'section_id': ''}

        if task_project:
            opts['project_id'] = self.get_project_id(task_project)
        else:
            opts.pop('project_id')

        if task_assignee:
            opts['responsible_uid'] = task_assignee
        else:
            opts.pop('responsible_uid')

        if task_due_date:
            opts['due'] = task_due_date
        else:
            opts.pop('due')

        if task_section:
            opts['section_id'] = self.get_section_id(task_section)
        else:
            opts.pop('section_id')

        self.api.add_item(task_content, opts)

    def add_task_from_list(self, task_list):
        for task in task_list:
            task_content, opts = task.get_task_details()
            self.api.items.add(task_content, **opts)

    # TODO: add task updating functions

    def print_tasks(self, project=None, section=None):
        if section:
            if not project:
                raise AttributeError("Missing project name")
            print(self.get_tasks_from_project(project, section))
        elif project:
            print(self.get_tasks_from_project(project))
        else:
            projects = self.api.state['items']
            print(projects)

    # def get_task_list(self, filename):
    #     with open(filename, 'r') as taskListFile:
    #         tasks = json.load(taskListFile)
    #     task_list = []
    #
    #     for task in tasks['taskList']:
    #         temp_task_content = task['content']
    #         temp_task_assignee = task['assignee']
    #         temp_task_due_date = task['due']
    #         temp_task_project = task['project']
    #         temp_task_section = task['section']
    #         task_list.append(Task(temp_task_content, temp_task_assignee, temp_task_due_date, temp_task_project,
    #                               temp_task_section))
    #     return task_list

    def write_tasks_to_file(self, filename, projectName=None, sectionID=None, sectionName=None):
        try:
            task_string = json.dumps({'taskList': self.get_tasks_from_project(projectName, sectionID, sectionName)})
            with open(filename, 'w') as taskFile:
                taskFile.write(task_string)
        except IOError:
            print("Problem writing to file")

    def write_collaborators_to_file(self, filename, projectName=None):
        collaborator_dict = {'assignees': []}
        if projectName:
            collaborators = self.get_collaborators_from_project(projectName)
            tmp_collaborators = [x.__dict__ for x in collaborators]
            for collaborator in tmp_collaborators:
                collaborator["tasks"] = [x.__dict__ for x in collaborator["tasks"]]
            collaborator_dict['assignees'].extend(tmp_collaborators)
        else:
            for collaborator in self.collaborators:
                collaborator_dict['assignees'].append(collaborator)
        with open(filename, 'w') as collaborator_file:
            json.dump(collaborator_dict, collaborator_file)

    def commit_tasks(self):
        try:
            status = self.api.commit()
            return True
        except SyncError:
            return False

    def to_json(self):
        self.api.serialize()
        return json_default(self.api)


if __name__ == '__main__':
    myAutomator = TaskManager()
    # print(CollaboratorsManager(myAutomator.api).get_by_id())
    # print(myAutomator.api.collaborator_states.state['collaborator_states'])
    # print(CollaboratorStatesManager(myAutomator.api).get_by_ids(2237030900))
    # print(myAutomator.get_projects())
    # print(myAutomator.get_sections())
    # print(myAutomator.get_section())
    #print(myAutomator.get_tasks_from_project('Family', sectionName='Cleaning'))
    # myAutomator.print_tasks()
    # myAutomator.write_tasks_to_file('test_projects.json', 'Family', sectionName='Cleaning')
    # print(myAutomator.get_collaborators_from_project('Family'))
    # print(myAutomator.collaborators[11869293].__dict__)
    myAutomator.write_collaborators_to_file('soup_assignees.json', 'Soup')
    myAutomator.write_tasks_to_file("cleaning_template.json", "Soup", sectionName="Cleaning")
