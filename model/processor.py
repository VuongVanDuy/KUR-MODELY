from .task import Task
from config import COEFF_ROUND

class Processor:
    def __init__(self, id) -> None:
        self.id = id
        self.current_task = None
        self.time_left = 0

    def __repr__(self):
        return f"Processor(id={self.id}, current_task={self.current_task}, time_left={round(self.time_left, 4)})"

    def assign_task(self, task: Task) -> None:
        self.current_task = task
        self.time_left = task.service_time

    def work(self, time_step: float) -> None:
        if self.current_task is not None:
            self.time_left = round(self.time_left - time_step, COEFF_ROUND)
            if self.time_left <= 0:
                self.current_task = None
                self.time_left = 0

    def is_free(self) -> bool:
        return self.current_task is None

    def get_task(self) -> Task:
        return self.current_task
    #
    # def get_time_left(self) -> float:
    #     return self.time_left
