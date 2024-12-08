import time
from threading import Event
from model.task import generate_tasks
from model.buffer import Buffer
from model.processor import Processor
from config import NUM_PROCESS, PROCESSORS, TIME_STEP, MAX_RUN_TIME, MAX_SIZE_BUFFER, ARRIVAL, NEW_WORK
import os

class SystemSimulator:
    def __init__(self, tasks: list, processors: int, buffer: Buffer, time_step: float, max_run_time: float) -> None:

        self.num_process = NUM_PROCESS
        self.processors = processors
        self.tasks = tasks
        self.buffer = buffer
        self.time = 0
        self.time_step = time_step
        self.max_run_time = max_run_time
        self.running = Event()

    def handle_tasks(self) -> tuple:
        if not self.tasks:
            return None, None

        for task in self.tasks:
            task.tact(self.time_step)

        ready_tasks = [task for task in self.tasks if task.arrival_time == 0]
        ready_tasks.sort(key=lambda x: x.priority, reverse=True)
        tasks_to_add = ready_tasks[:self.num_process]

        return (ARRIVAL, tasks_to_add) if tasks_to_add else (None, None)

    def request_to_buffer(self, tasks_to_add: list) -> None:
        for task in tasks_to_add:
            if len(self.buffer) < self.buffer.max_size:
                self.buffer.add(task)
                self.tasks.remove(task)

    def handle_buffer(self) -> tuple:
        if self.buffer.isEmpty():
            return None, None

        messages = []
        for id_proc, processor in enumerate(self.processors):
            if processor.is_free():
                task = self.buffer.get()
                messages.append((id_proc, task))
                if self.buffer.isEmpty():
                    break

        return NEW_WORK, messages

    def request_to_processor(self, new_works: list[tuple]) -> None:
        for work in new_works:
            id_proc, task = work
            self.processors[id_proc].assign_task(task)

    def handle_processors(self) -> None:
        for processor in self.processors:
            processor.work(self.time_step)

    def work(self) -> None:
        self.time += self.time_step
        state, tasks_to_add = self.handle_tasks()
        if state == ARRIVAL:
            self.request_to_buffer(tasks_to_add)

        state, new_works = self.handle_buffer()
        if state == NEW_WORK:
            self.request_to_processor(new_works)

        self.handle_processors()

    def run(self) -> None:
        self.running.set()

        while self.running.is_set():
            self.work()

            if self.time >= self.max_run_time:
                print("\nМаксимальное время выполнения истекло. Остановите систему...")
                self.stop()
                break

            if not self.tasks and len(self.buffer) == 0 and all(proc.is_free() for proc in self.processors):
                print("\nБольше никаких задач для выполнения нет. Остановите систему. Симуляция закончилась...")
                self.stop()
                break

            time.sleep(TIME_STEP)

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
    processors = [Processor(i) for i in range(PROCESSORS)]
    buffer = Buffer(max_size=MAX_SIZE_BUFFER)

    simulator = SystemSimulator(tasks=tasks, processors=processors, buffer=buffer,
                                time_step=TIME_STEP, max_run_time=MAX_RUN_TIME)

    try:
        simulator.run()
    except KeyboardInterrupt:
        print("\nStop simulator...")
        simulator.stop()

