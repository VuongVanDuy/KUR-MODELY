import time
import os
from threading import Event
from model.task import generate_tasks, Task
from model.buffer import Buffer
from model.processor import Processor
from config import (NUM_PROCESS, NUM_PROCESSORS, TIME_STEP, TIME_SIMULATION, MAX_SIZE_BUFFER,
                    SERVICE_TIME_TASK, NUM_TASKS, NUM_PRIORITIES, PROBALITIES, LAMBDAS,
                    ARRIVAL, NEW_WORK, RUNNING, SUCCESS, FAILURE)

class SystemSimulator:
    def __init__(self, tasks: list, processors: int, buffer: Buffer, time_step: float, time_simulation: float) -> None:

        self.num_process = NUM_PROCESS
        self.time_step = time_step
        self.time_simulation = time_simulation
        self.time = 0

        self.processors = processors
        self.tasks = tasks
        self.buffer = buffer
        self.state = None
        self.running = Event()

    def handle_tasks(self) -> (str, list):
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

    def handle_buffer(self) -> (str, list):
        if self.buffer.isEmpty():
            return None, None

        messages = []
        for id_proc, processor in enumerate(self.processors):
            if processor.is_free():
                task = self.buffer.get()
                messages.append((id_proc, task))
                if self.buffer.isEmpty():
                    break

        return (NEW_WORK, messages) if messages else (None, None)

    def request_to_processor(self, new_works: list[tuple]) -> None:
        for work in new_works:
            id_proc, task = work
            self.processors[id_proc].assign_task(task)

    def handle_processors(self) -> str:
        alls_free = all(proc.is_free() for proc in self.processors)

        if self.time >= self.time_simulation and not alls_free:
            return FAILURE
        if alls_free and self.buffer.isEmpty() and not self.tasks:
            return SUCCESS

        for processor in self.processors:
            processor.work(self.time_step)

        return RUNNING

    def work(self) -> None:
        self.time += self.time_step
        state, tasks_to_add = self.handle_tasks()
        if state == ARRIVAL:
            self.request_to_buffer(tasks_to_add)

        state, new_works = self.handle_buffer()
        if state == NEW_WORK:
            self.request_to_processor(new_works)

        state_sys = self.handle_processors()
        self.state = state_sys

    def run(self) -> None:
        self.state = RUNNING
        self.running.set()

        while self.running.is_set():
            self.work()

            if self.state == FAILURE:
                print(f"State: {self.state}")
                print("\nМаксимальное время выполнения истекло. Остановите систему...")
                self.stop()
                break

            if self.state == SUCCESS:
                print(f"State: {self.state}")
                print("\nБольше никаких задач для выполнения нет. Остановите систему. Симуляция закончилась...")
                self.stop()
                break

            time.sleep(TIME_STEP)

            # xóa màn hình console
            os.system('cls')

            if not self.state_tasks():
                print("All tasks active!")
            else:
                print("***Tasks***")
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
        state = f"\n***Buffer***\nSize: {len(self.buffer)}\n"
        for entry in self.buffer:
            state += f"{entry}\n"
        state += f"\n***Processors***\n"
        for processor in self.processors:
            state += f"{processor}\n"
        state += f"\n--------Simulation Time: {self.time:.3f}--------\n"
        return state


if __name__ == '__main__':
    tasks = generate_tasks(num_tasks=NUM_TASKS, num_priorities=NUM_PRIORITIES, service_time=SERVICE_TIME_TASK,
                           probabilities=PROBALITIES, lambdas=LAMBDAS)
    processors = [Processor(i) for i in range(NUM_PROCESSORS)]
    buffer = Buffer(max_size=MAX_SIZE_BUFFER)

    simulator = SystemSimulator(tasks=tasks, processors=processors, buffer=buffer,
                                time_step=TIME_STEP, time_simulation=TIME_SIMULATION)

    try:
        simulator.run()
    except KeyboardInterrupt:
        print("\nStop simulator...")
        simulator.stop()

