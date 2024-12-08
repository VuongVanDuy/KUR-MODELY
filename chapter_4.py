import time
from threading import Event
from model.task import Task, generate_tasks
from model.buffer import Buffer
from model.processor import Processor
from config import NUM_PROCESS, PROCESSORS, TIME_STEP, MAX_RUN_TIME
import os

class SystemSimulator:
    def __init__(self, tasks: Task, num_processors: int, time_step: float = 0.001, max_run_time: float = 10.0) -> None:

        self.num_process = NUM_PROCESS
        self.processors = [Processor(i) for i in range(num_processors)]
        self.tasks = tasks
        self.buffer = Buffer(max_size=10)
        self.time = 0
        self.time_step = time_step
        self.max_run_time = max_run_time
        self.running = Event()

    def add_task(self, task: Task) -> None:
        self.buffer.add(task)

    def work(self) -> None:
        self.time += self.time_step

        if self.tasks:
            for task in self.tasks:
                task.tact(self.time_step)

            ready_tasks = [task for task in self.tasks if task.arrival_time == 0]
            ready_tasks.sort(key=lambda x: x.priority, reverse=True)
            tasks_to_add = ready_tasks[:self.num_process]

            for task in tasks_to_add:
                if len(self.buffer) < self.buffer.max_size:
                    self.add_task(task)
                    self.tasks.remove(task)

        for processor in self.processors:
            processor.work(self.time_step)

        for processor in self.processors:
            if processor.is_free():
                task = self.buffer.get()
                if task is not None:
                    processor.assign_task(task)

    def run(self) -> None:
        self.running.set()

        while self.running.is_set():
            self.work()

            if self.time > self.max_run_time:
                print("\nМаксимальное время выполнения истекло. Остановите систему...")
                self.stop()
                break

            if not self.tasks and len(self.buffer) == 0 and all(proc.is_free() for proc in self.processors):
                print("\nБольше никаких задач для выполнения нет. Остановите систему. Симуляция закончилась...")
                self.stop()
                break

            time.sleep(self.time_step)

            # xóa màn hình console
            os.system('cls')

            if not self.state_tasks():
                print("All tasks active!")
            else:
                print("List of tasks:")
                print(self.state_tasks())
            print(self)

    def stop(self) -> None:
        self.running.clear()

    def state_tasks(self) -> str:
        str = ""
        for task in self.tasks:
            str += f"{task}\n"
        return str

    def __repr__(self) -> str:
        state = f"Simulation Time: {self.time:.3f}\n"
        for processor in self.processors:
            state += f"{processor}\n"
        state += f"Buffer Size: {len(self.buffer)}\n"
        for entry in self.buffer:
            state += f"{entry}\n"
        return state


if __name__ == '__main__':
    tasks = generate_tasks(5, [0.8, 0.2], [0.5, 1.2])

    simulator = SystemSimulator(tasks=tasks, num_processors=PROCESSORS,
                                time_step=TIME_STEP, max_run_time=MAX_RUN_TIME)

    try:
        simulator.run()
    except KeyboardInterrupt:
        print("\nStop simulator...")
        simulator.stop()

