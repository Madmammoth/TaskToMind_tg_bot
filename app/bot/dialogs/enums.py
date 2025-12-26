from enum import StrEnum


class ListSelectionMode(StrEnum):
    CREATE_TASK = "create_task"
    EDIT_TASK = "edit_task"
    CREATE_LIST = "create_list"
    EDIT_LIST = "edit_list"
