import random
import string

from core import project_repository as p
from entity.details import Details


class ProjectDetailsController:

    def __init__(self):
        self.details = None
        self.persist = False
        self.__project = p.ProjectDetailsDao()
        self._complete_project = None

    def write(self, deets):
        if self.persist:
            return
        self.__project.write(deets)

    def search(self, uid):
        return self.__project.search(uid)

    def all_projects(self):
        return self.__project.get_all()

    def auto_write(self, flag):
        self.persist = flag

        for i in range(0, 200):
            letters = string.ascii_lowercase
            self.__project.write(
                Details(
                    title=str((''.join(random.choice(letters) for i in range(10)))),
                    size=random.randint(0, 1000),
                    priority=random.randint(0, 100)
                )
            )
        return self

    def get_project(self):
        if self._complete_project is None:
            self._complete_project = p.CompletedProjectDetailsDao()

    def create_schedule(self) -> list:
        return self.__project.create_schedule()

    def view_schedule(self, invalidate):
        return self.__project.internal_view_schedule(invalidate)

    def get_schedule(self):
        return self.__project.get_scheduled()

    def update_data_sources(self, deets):
        if self._complete_project is None:
            self._complete_project = p.CompletedProjectDetailsDao()

        self._complete_project.write(deets)
        self.__project.remove(deets)
