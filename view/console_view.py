from model.details import Details as deets
from view.project_controller import ProjectDetailsController as PDController


class ConsoleView:
    """
    A class Responsible for drawing the console
    commands and navigating to different sub-modules.
    """

    def __init__(self, c):
        self._is_created = False
        self._arrow = "==> "
        self.force_recursive = True
        self._c = c
        self._init_m_vars()
        self._menu(False)

    def _menu(self, auto_line=True):
        if auto_line:
            print("\n")

        self._input_project()
        self._view_projects()
        self._view_schedule()
        print("4. Get a Project")
        print("5. Exit")

        try:
            self._navigate(int(input(self._arrow)))
        except ValueError:
            self._menu(True)

    def _init_m_vars(self):
        self._project_id_str = "Project ID  : "
        self._title_str = "Title       : "
        self._size_str = "Size        : "
        self._priority_str = "Priority    : "

    def _navigate(self, choice):
        skip = False
        flag = None

        print("\n" * 2)

        if choice == 1:
            try:
                title = input(self._title_str)
                size = int(input(self._size_str))
                priority = int(input(self._priority_str))

                if size < -1 and priority < -1:
                    raise ValueError
                self.write_project(title, size, priority)
            except ValueError:
                print("Size or Priority number must be a valid integer")

        # View Projects
        elif choice == 2:
            self._view_projects()
            sub = input(self._arrow).lower()

            if sub == "a":
                p_id = input("Enter " + self._project_id_str)
                data = self._c.search(p_id)
                self._display_one_project(data)
            elif sub == "b":
                print("Completed Projects")
                for items in self._c.view_completed():
                    self._show_completed(items)
            elif sub == "c":
                items = self._c.all_projects()
                if len(items) == 0:
                    print("Document is empty...")
                for d in items:
                    self._display_one_project(d)

        elif choice == 3:
            self._view_schedule()
            sub = input(self._arrow).lower()

            if sub == "a":
                self._display_created_schedule()
            elif sub == "b":
                self._show_updated_schedule(self._is_created)
                flag = 3

        elif choice == 4:
            skip = self.get_project()
            flag = 4

        elif choice == 5:
            print("Thank you!")
            exit()
        self._menu() if not skip else self._navigate(flag)

    @staticmethod
    def _input_project():
        print("1. Input Project Details")

    @staticmethod
    def _view_projects():
        print("2. View Projects")
        print("\ta. One Project")
        print("\tb. Completed Projects")
        print("\tc. All Projects")

    @staticmethod
    def _view_schedule():
        print("3. Schedule Projects")
        print("\ta. Create Schedule")
        print("\tb. View Schedule")

    def write_project(self, title, size, priority):
        self._c.write(deets(title=title, size=size, priority=priority))

    def _display_one_project(self, data):
        if data is not None and not isinstance(data, str):
            print("-----------------------------------")
            print("| " + self._project_id_str, data.id)
            print("| " + self._title_str, data.title)
            print("| " + self._size_str, data.size)
            print("| " + self._priority_str, data.priority)
            print("-----------------------------------")
        else:
            if isinstance(data, str):
                print("This document with project ID: " + data + " has been recently deleted.")
            else:
                print("No Document found in the project.")

    def _display_created_schedule(self):
        schedule = self._c.create_schedule()
        if len(schedule) == 0:
            print("-----------------------------------")
            print("|\tProject Document is Empty!\t  |")
            print("-----------------------------------")
            return
        else:
            self._is_created = True

        for index in range(len(schedule)):
            if index == 0:
                print("-----------------------------------")
                print("|\tDocuments to be copy-typed\t  |")
                print("-----------------------------------")
            print("|  \t Document ID #" + str(index + 1) + ": " + str(schedule[index].id) + " \t  |")
            if index == len(schedule) - 1:
                self._show_if_created()

    def _show_updated_schedule(self, invalidate):
        list_items, is_updated = self._c.view_schedule(invalidate)

        if (not list_items or len(list_items) == 0) and not is_updated:
            show = self._show_if_not_created()
            if show:
                self._show_updated_schedule(show)
        elif is_updated and list_items:
            s = len(list_items)
            i = 0

            for priority, obj in list_items:
                print("------------------------------------------")
                print(" Priority " + str(priority))
                for o in obj:
                    print("------------------------------------------")
                    print(" " + self._project_id_str + str(o.id) + "\t\t\t\t ")
                    print(" " + self._title_str + str(o.title) + "\t\t\t\t ")
                    print(" " + self._size_str + str(o.size) + "\t\t\t\t ")

                if s - 1 == i:
                    print("------------------------------------------")
                i += 1
                print("\n")
        elif is_updated and not list_items:
            print("Project document is empty!")

    def _show_as_priority_list(self):
        pass

    @staticmethod
    def _show_if_not_created():
        print("------------------------------------------")
        print("|\t  Schedule hasn't been created yet\t |")
        print("------------------------------------------")

        create = input("Do you want to create schedule? Y/N: ").lower()
        if create == 'y':
            return True
        return False

    def _show_if_created(self):
        if self._is_created:
            print("-----------------------------------")
            print("|\t     Schedule Created!\t      |")
            print("-----------------------------------")

    def get_project(self):
        # TODO: Fix
        top_most = self._c.get_schedule()

        if not self._is_created and not top_most:
            print("You must create a schedule first before you can queue and get a project.")
            return False

        top = top_most

        try:
            print("Your top most document with project ID: " + str(top.id) + " has been removed from the queue.")
        except AttributeError:
            print("Empty...")

        return False

    def _show_completed(self, i):
        print("----------------------------")
        print(self._project_id_str + str(i.id))
        print(self._title_str + str(i.title))
        print(self._size_str + str(i.size))
        print(self._priority_str + str(i.priority))


if __name__ == '__main__':
    # Creates 25 random project inputs into the file if set to True.
    ConsoleView(PDController().auto_write(False))
