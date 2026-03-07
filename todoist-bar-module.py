from todoist_api_python.api import TodoistAPI
from datetime import datetime
from subprocess import run, CompletedProcess
from dotenv import dotenv_values

from todoist_api_python.models import Task
from requests.exceptions import HTTPError
from typing import Callable

# Todoist Python API: https://pypi.org/project/todoist_api_python/
# Todoist Python API Docs: https://doist.github.io/todoist-api-python/

secrets = dotenv_values(".env")

# Deprecated; use of local keyring discouraged for practical reasons
def get_todoist_api_token_keyring() -> str:
    completed_process: CompletedProcess[bytes] = run(
            ["secret-tool", "lookup", "todoist", "api_token"],
            capture_output=True)

    result: str = completed_process.stdout.decode()
    if result == "":
        print("?secret")
        exit()

    return result


def get_todoist_api_token() -> str:
    return secrets["TODOIST_API_TOKEN"]


def get_todoist_tasks() -> list[Task]:
    try:
        todoist_api: TodoistAPI = TodoistAPI(get_todoist_api_token())
        iter_tasks = todoist_api.get_tasks()

        tasks = []
        for task_page in iter_tasks:
            tasks.extend(task_page)

        return tasks

    except HTTPError:
        print("?api")
        exit()


def get_task_info(tasks: list[Task],
                  *predicates: Callable[[Task], bool]) -> list[int]:
    result: list[int] = [0 for _ in range(len(predicates))]

    for task in tasks:
        for i, predicate in enumerate(predicates):
            result[i] = result[i] + 1 if predicate(task) else result[i]

    return result


def format_task_info(task_info: list[int]) -> str:
    result: str = ""

    for info in task_info:
        result += str(info)

    return result.strip()


# date_string: %Y-%m-%d
# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
def is_due_today(task: Task) -> bool:
    if task.due is None:
        return False

    return task.due.date == datetime.now().strftime("%Y-%m-%d")


def is_past_due(task: Task) -> bool:
    # TODO: Compare time if task contains it

    if task.due is None:
        return False

    # task.due.date is either date or datetime, depending on the task.
    # a new date object is being crafted to guarantee a date object
    task_date = task.due.date
    date = datetime(task_date.year, task_date.month, task_date.day).date()

    # .date() to compare date only and ignore time
    return date < datetime.now().date()



def no_due(task: Task) -> bool:
    return task.due is None


def main() -> None:
    tasks: list[Task] = get_todoist_tasks()
    task_info: list[int] = get_task_info(tasks,
                                         is_due_today, is_past_due, no_due)
    print(format_task_info(task_info))


if __name__ == "__main__":
    main()
