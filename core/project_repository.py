import os
import uuid

from entity.details import Details
import csv


class BaseDao:
    """
    An abstract class datasource responsible for reading and writing data into a CSV file.

    @author strongforce1
    """

    def __init__(self, file_name):
        self.schema = ['ID', 'Title', 'Size', 'Priority']
        self.file_name = self.output_directory(file_name)

        try:
            csv.reader(self._open_file('r'))
        except FileNotFoundError:
            self._dict_writer(self._open_file('a')).writeheader()
        finally:
            self.file_output = self._dict_reader()

    def write_to_file(self, deets):
        """
        Write delimited string of rows into a csv file.

        :param deets: the object to be written in the file
        """
        if deets.id is None:
            deets.id = self.generate_uuid()

        with self._open_file('a', line=True) as input_file:
            self._dict_writer(input_file).writerow(self._to_dict(deets))
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
                return self._to_obj(row)
        return None

    def _get_all(self) -> [Details]:
        self.invalidate()
        """
        Method for reading all the project details data in the CSV file and
        converts it into a Details object and return it as a list of Details object.

        :return: list of Details object
        """
        list_of_deets = []

        for dic in self.file_output:
            list_of_deets.append(self._to_obj(dic))

        return list_of_deets

    def _dict_writer(self, file) -> csv.DictWriter:
        """
        Operates like a regular writer but maps dictionaries onto output rows.

        :param file: the file directory of the csv file
        :return: new instance of csv.DictWriter
        """
        return csv.DictWriter(file, delimiter=',', fieldnames=self.schema)

    def invalidate(self):
        """ request another instance of csv.DictReader """
        self.file_output = self._dict_reader()

    def _to_obj(self, dic) -> Details:
        """
        Convert dictionary object to a new instance of Details object.

        :param dic: the object to be converted
        :return: new instance of Details object.
        """
        return Details(
            dic[self.schema[0]], dic[self.schema[1]],
            dic[self.schema[2]], dic[self.schema[3]]
        )

    def _to_dict(self, obj) -> dict:
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
        except KeyError or AttributeError as e:
            print(e)

        return deets

    def _dict_reader(self) -> csv.DictReader:
        """
        Initialize a new instance of DictReader

        :return: new instance of csv.DictReader
        """
        return csv.DictReader(open(self.file_name))

    def _open_file(self, mode, line=False):
        """
        A helper method use to open a specific file with a set of custom modes and returns a file as an object.

        :param mode: mode that provides how files can be opened: read 'R', write 'W', or appending 'A'.
        :param line: flag to whether to write a new line in the csv file or not.
        :return: a file object
        """
        return open(self.file_name, mode, newline='' if line else None)

    def remove_document(self, deets):
        all_copy = self._get_all()
        file = self._open_file('w')
        file.truncate()
        file.close()

        self._dict_writer(self._open_file('a')).writeheader()

        with self._open_file('a', line=True) as input_file:
            for d in all_copy:
                if d.id != deets.id:
                    self._dict_writer(input_file).writerow(self._to_dict(d))
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
        return str(uuid.uuid4())[:8]

    def __internal_write_to_a_file(self, deets, mode, line=True):
        pass


class CompletedProjectDetailsDao(BaseDao):

    def __init__(self):
        BaseDao.__init__(self, 'completed_project.csv')

    def view_completed(self):
        pass

    def write(self, d):
        self.write_to_file(d)


class ProjectDetailsDao(BaseDao):

    def __init__(self):
        self._sorted_items = None
        self.new_write = False
        self.is_schedule_created = False
        BaseDao.__init__(self, 'typist_details.csv')

    def write(self, deets):
        self.write_to_file(deets)
        self.new_write = True

    def get_scheduled(self):
        if self.is_schedule_created:
            return self.create_schedule()
        return []

    def create_schedule(self) -> list:
        # if self.new_write:
        self.invalidate()
        self.is_schedule_created = True

        all_items = self._get_all()
        self._sorted_items = self._sort(all_items)
        return self._sorted_items

    def _sort(self, all_items):
        """
        Sort list of project documents by priority and size using Bubble Sort.

        :param all_items: list of items to be sorted
        :return: sorted items backed by priority and size
        """

        n = len(all_items)

        for i in range(n - 1):
            for j in range(0, n - i - 1):
                if int(all_items[j].priority) > int(all_items[j + 1].priority):
                    self._swap(all_items, j)
                elif int(all_items[j].priority) == int(all_items[j + 1].priority):
                    if int(all_items[j].size) > int(all_items[j + 1].size):
                        self._swap(all_items, j)
        return all_items

    def internal_view_schedule(self, invalidate):
        list_reflection = []

        if invalidate:
            list_reflection = self.create_schedule()
            self.is_schedule_created = True

        if not self.is_schedule_created:
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
    def _swap(deets, index):
        deets[index], deets[index + 1] = deets[index + 1], deets[index]

    def get_all(self):
        return self._get_all()

    def search(self, uid):
        return self._search_project(uid)

    def remove(self, deets):
        self.remove_document(deets)
        pass
