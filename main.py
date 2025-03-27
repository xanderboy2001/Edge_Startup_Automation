"""
Module containing the main entry point of the program.

This module retrieves task information from ServiceNow and prints them in a human-readable format.
"""

from typing import List
from get_tasks import get_service_now_tasks, Task


def print_tasks(tasks_list: List[Task]) -> None:
    """
    Prints all the task information in a human-readable format.

    Args:
        tasks_list (List[Task]): list of tasks to print."""
    for task in tasks_list:
        print(
            f"Task Number: {task.number}\t"
            "Assigned To: {task.assigned_to}\t"
            "State: {task.state}\t"
            "Description: {task.description}\t"
            "Opened: {task.opened}\t"
            "Link: {task.link}\n"
        )


def main():
    """
    Entry point of the program.

    Returns:
        None
    """
    url = (
        "https://nysifprod.service-now.com/now/nav/ui/classic/params/target/task_list.do%3F"
        "sysparm_query%3Dactive%253Dtrue%255E"
        "assignment_group%253D2d636adcdb4957006a2c9837db96193e%255Estate!%253D6%255E"
        "numberNOT%2520LIKERITM%26sysparm_first_row%3D1%26sysparm_view%3D"
    )
    print_tasks(get_service_now_tasks(url))


if __name__ == "__main__":
    main()
