import random
import string

from core import project_repository as p
from model.details import Details as deets


class ProjectDetailsController:

    """
        This controller act as middle man between console view and the data access object.
        This class is responsible for retrieving CSV files into data sources

        @author strongforce1
        """

    def __init__(self):
        self.details = None
        self._complete_project = None

        self.__project = p.ProjectDetailsDao()
        self.__completed = p.CompletedProjectDetailsDao()

    def write(self, details):
        self.__project.write(details)
        print("\nSuccessfully writing a project.")

    def search(self, uid):
        """
        Search specific project in the data source.
        :param uid: id to search in the datasource.
        :return: the matche uid project
        """
        return self.__project.search(uid)

    def all_projects(self):
        """"
        Get all projects in the datasource in order by writes.
        """
        return self.__project.get_all()

    def auto_write(self, flag):
        if flag:
            for i in range(0, 5):
                letters = string.ascii_lowercase
                self.__project.write(
                    deets(
                        title=str((''.join(random.choice(letters) for i in range(10)))),
                        size=random.randint(0, 1000),
                        priority=random.randint(0, 100)
                    )
                )
        return self

    def create_schedule(self) -> list:
        """
        Get the created sorted schedule in the data source.
        :return: sorted projects based on its ID
        """
        return self.__project.create_schedule()

    def view_schedule(self, invalidate):
        """
        View the schedule sorted items.
        :param invalidate: flag whether to re init the dictReader
        :return: sorted schedule items.
        """
        return self.__project.internal_view_schedule(invalidate)

    def get_schedule(self):
        """
        Get the top most project in the queue.
        :return: the top most project.
        """
        top_most = self.__project.get_scheduled()
        self.__update_data_sources(top_most)
        return top_most

    def __update_data_sources(self, details):
        """
        Force both data sources to update the data.
        :param details: the object to update and removed.
        :return: None
        """
        if details is not None:
            self.__completed.write(details)
            self.__project.remove(details)

    def view_completed(self):
        """
        Get all completed projects in the data source.
        :return:
        """
        return self.__completed.view_completed()
