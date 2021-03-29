import csv
import os
import uuid
from abc import abstractmethod, ABC
from model.details import Details


class BaseDao:
    """
    An abstract class datasource responsible for reading and writing data into the CSV file.

    @author strongforce1
    """

    def __init__(self, file_name):
        """
        Initialize abstract base class, new instance of dict reader and
        it automatically populates the csv file header with set of schema
        columns when it throws and exception.

        :param file_name: the filename of the csv file.
        """
        self.schema = ['ID', 'Title', 'Size', 'Priority']
        self.file_name = self.output_directory(file_name)

        try:
            csv.reader(self.__open_file('r'))
        except FileNotFoundError:
            self.__dict_writer(self.__open_file('a')).writeheader()
        finally:
            self.file_output = self.__dict_reader()

    def write_to_file(self, deets):
        """
        Write delimited string of rows into a csv file.

        :param deets: the object to be written in the file
        """
        if deets.id is None:
            deets.id = self.generate_uuid()

        with self.__open_file('a', line=True) as input_file:
            self.__dict_writer(input_file).writerow(self.__to_dict(deets))
        input_file.close()

    def _search_project(self, uid):
        """
        Search one specific document project using its uid.

        :param uid: id to be search
        :return: new instance of Details or None object
        """
        self.invalidate()
        for row in self.file_output:
            if uid == str(row[self.schema[0]]):
                return self.__to_obj(row)
        return None

    def internal_get_all(self) -> [Details]:
        """
        Method for reading all the project details data in the CSV file and
        converts it into a Details object and return it as a list of Details object.

        :return: list of Details object
        """

        self.invalidate()
        list_of_deets = []

        for dic in self.file_output:
            list_of_deets.append(self.__to_obj(dic))

        return list_of_deets

    def __dict_writer(self, file) -> csv.DictWriter:
        """
        Operates like a regular writer but maps dictionaries onto output rows.

        :param file: the file directory of the csv file
        :return: new instance of csv.DictWriter
        """
        return csv.DictWriter(file, delimiter=',', fieldnames=self.schema)

    def invalidate(self):
        """ request another instance of csv.DictReader """
        self.file_output = self.__dict_reader()

    def __to_obj(self, dic) -> Details:
        """
        Convert dictionary object to a new instance of Details object.

        :param dic: the object to be converted
        :return: new instance of Details object.
        """
        return Details(
            dic[self.schema[0]], dic[self.schema[1]],
            dic[self.schema[2]], dic[self.schema[3]]
        )

    def __to_dict(self, obj) -> dict:
        """
        Convert details object to new dictionary instance.

        :param obj: the object to be converted.
        :return: new instance of dictionary object.
        """
        deets = {}
        try:
            deets[self.schema[0]] = obj.id
            deets[self.schema[1]] = obj.title
            deets[self.schema[2]] = obj.size
            deets[self.schema[3]] = obj.priority
        except KeyError or AttributeError:
            pass
        return deets

    def __dict_reader(self) -> csv.DictReader:
        """
        Initialize a new instance of DictReader

        :return: new instance of csv.DictReader
        """
        return csv.DictReader(open(self.file_name))

    def __open_file(self, mode, line=False):
        """
        A helper method use to open a specific file with a set of custom modes and returns a file as an object.

        :param mode: mode that provides how files can be opened: read 'R', write 'W', or appending 'A'.
        :param line: flag to whether to write a new line in the csv file or not.
        :return: a file object
        """
        return open(self.file_name, mode, newline='' if line else None)

    def remove_document(self, deets):
        all_copy = self.internal_get_all()
        file = self.__open_file('w')
        file.truncate()
        file.close()

        self.__dict_writer(self.__open_file('a')).writeheader()
        with self.__open_file('a', line=True) as input_file:
            for d in all_copy:
                if d.id != deets.id:
                    self.__dict_writer(input_file).writerow(self.__to_dict(d))

        self.finish_remove(deets)
        input_file.close()

    @staticmethod
    def output_directory(filename):
        """
        Writes the output file into a specific output folder.

        :param filename: the filename of the csv file
        :return: output directory of a filename
        """
        directory = os.path.dirname(os.getcwd()) + "/output"

        if not os.path.exists(directory):
            os.mkdir(directory)

        return os.path.join(directory, filename)

    @staticmethod
    def generate_uuid():
        """
        Generates unique ID for our details object delegate.
        :return: unique ID
        """
        return str(uuid.uuid4())[:8]

    @abstractmethod
    def finish_remove(self, details):
        pass


class CompletedProjectDetailsDao(BaseDao):
    """
    A class datasource responsible for reading and writing the completed projects.

    @author strongforce1
    """

    def __init__(self):
        BaseDao.__init__(self, 'completed_project.csv')

    def view_completed(self):
        """
        :return: all items added into the csv in order by write.
        """
        return self.internal_get_all()

    def write(self, d):
        """
        call the super class write_to_file method
        to write the file in completed_project.csv.

        :param d: the object to be written in the CSV file.
        :return: None
        """
        if isinstance(d, Details):
            self.write_to_file(d)

    def finish_remove(self, details):
        """
        Implements // TODO: Nothing
        :param details:
        :return:
        """
        pass


class ProjectDetailsDao(BaseDao):
    """
    A class datasource responsible for reading, writing and updating the project details.

    @author strongforce1
    """

    def __init__(self):
        self._increment = 0
        self._remove_items = set()
        self._sorted_items = None
        self._new_write = False
        self._schedule_created = False
        BaseDao.__init__(self, 'typist_details.csv')

    def write(self, deets):
        """
        call the super class write_to_file method
        to write the file in typist_details.csv.

        :param deets: the object to be written in the CSV file.
        """
        self.write_to_file(deets)
        self._new_write = True

    def get_scheduled(self):
        """
        Get the sorted scheduled items from self._sorted_items,
        first it checks if the schedule is created then it checks its length.

        If it contains, it'll linearly reference the top most object using the increment member variable.

        If it throws an exception, this indicates that the sorted item is already empty.
        And it invalidates the dictReader to re-initialize. Otherwise, it creates another set of
        schedule details list.

        :return: list of scheduled Details object if is scheduled. Otherwise, None.
        """
        if self._schedule_created:
            items = self._sorted_items
            if len(items) > 0:
                deets = None
                try:
                    deets = items[self._increment]
                    self._increment += 1
                except IndexError:
                    self._sorted_items = []
                    self._increment = 0
                    self.invalidate()
                return deets
            else:
                return self.create_schedule()
        return None

    def create_schedule(self) -> list:
        """
        Creates a schedule by getting all the list in the typist_details.csv file then
        it sorts the items using enhanced bubble sort algorithm.

        :return: sorted list of details objects order by priority then size.
        """
        self.invalidate()
        self._schedule_created = True

        all_items = self.get_all()
        self._sorted_items = self.__sort(all_items)
        return self._sorted_items

    def __sort(self, all_items):
        """
        Sort list of project documents by priority and size using enhanced bubble sort algorithm.

        :param all_items: list of items to be sorted
        :return: sorted items backed by priority and size
        """

        n = len(all_items)

        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if int(all_items[j].priority) > int(all_items[j + 1].priority):
                    self.__swap(all_items, j)
                elif int(all_items[j].priority) == int(all_items[j + 1].priority):
                    if int(all_items[j].size) > int(all_items[j + 1].size):
                        self.__swap(all_items, j)
        return all_items

    def internal_view_schedule(self, invalidate):
        """
        Force to invalidate if needed, This will re-creates the csv.DictReader instance
        to read all items in the specific typist_details.csv file.

        It uses simple linear data structure to sort flawlessly:

        1. Creates a copy of sorted sorted items from create_schedule method or self._sorted_items.

            list_reflection = []

            if invalidate:
                list_reflection = self.create_schedule()
                self._schedule_created = True

        2. Get the unique priority number from the copied sorted items using simple iteration and adding it into the set().

            priority_set = set()
            for index in range(len(list_reflection)):
                priority_set.add(list_reflection[index].priority)

        3. Using nested loops to check whether the unique ID in the priority matches the ID in the copied list.
            if it matches then it'll basically append to the dictionary key priority as value as arrays.

            nested_arr_dict = {}

            for p in priority_set:
                for deets in list_reflection:
                    if p == deets.priority:
                        nested_arr_dict.setdefault(int(p), []).append(deets)

        4. Sort the dictionary items.

            linear_sort = sorted(nested_arr_dict.items())

        :param invalidate: initialize new instance of csv.DictReader
        :return: sorted dictionary items order by priority and size.
        """
        list_reflection = []

        if invalidate:
            list_reflection = self.create_schedule()
            self._schedule_created = True

        if not self._schedule_created:
            return {}, False

        priority_set = set()

        for index in range(len(list_reflection)):
            priority_set.add(list_reflection[index].priority)

        nested_arr_dict = {}

        for p in priority_set:
            for deets in list_reflection:
                if p == deets.priority:
                    nested_arr_dict.setdefault(int(p), []).append(deets)

        linear_sort = sorted(nested_arr_dict.items())

        return linear_sort, True

    @staticmethod
    def __swap(deets, index):
        """
        Swaps two items
        :param deets: the details object
        :param index: index position to swapped the items.
        :return:
        """
        deets[index], deets[index + 1] = deets[index + 1], deets[index]

    def get_all(self):
        """
        :return: all items added into the csv in order by write.
        """
        return self.internal_get_all()

    def search(self, uid):
        """
        Scans and checks if specific ID is in the csv file, Otherwise, None
        :param uid: the uid of the project document
        :return: Details object
        """
        for deets in self._remove_items:
            if deets.id == uid:
                return str(uid)
        return self._search_project(uid)

    def remove(self, deets):
        """
        Remove the details object into the csv file.
        :param deets: The object to be removed.
        :return: None
        """
        if isinstance(deets, Details):
            self._remove_items.add(deets)
            self.remove_document(deets)

    def finish_remove(self, details):
        """
        Override method
        :param details:
        :return:
        """
        pass
