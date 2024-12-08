import numpy as np
import matplotlib.pyplot as plt
from config import PROBALITIES, LAMBDAS, NUM_PRIORITIES, SERVICE_TIME_TASK, NUM_TASKS, COEFF_ROUND


class Task:
    def __init__(self, id, priority, arrival_time, service_time):
        self.id = id
        self.priority = priority
        self.arrival_time = arrival_time
        self.service_time = service_time

    def tact(self, time_step: float) -> None:
        if self.arrival_time - time_step > 0:
            self.arrival_time = round(self.arrival_time - time_step, COEFF_ROUND)
        else:
            self.arrival_time = 0

    def __repr__(self):
        return f"Task(id={self.id}, priority={self.priority}, arrival_time={self.arrival_time}, service_time={self.service_time})"


def generate_hyperexponential_times(probabilities, lambdas):
    if len(probabilities) != len(lambdas):
        raise ValueError("Количество вероятностей и параметров величины должно быть равным.")
    if not np.isclose(sum(probabilities), 1.0):
        raise ValueError("Сумма вероятностей должна равняться 1.")

    component_index = np.random.choice(len(probabilities), p=probabilities)

    return round(np.random.exponential(1 / lambdas[component_index]), COEFF_ROUND)

def generate_tasks(num_tasks, num_priorities, service_time, probabilities, lambdas):
    return [Task(id=i, priority=np.random.randint(1, num_priorities + 1),
                 arrival_time=generate_hyperexponential_times(probabilities, lambdas),
                 service_time=service_time) for i in range(num_tasks)]

if __name__ == '__main__':
    tasks = generate_tasks(NUM_TASKS, NUM_PRIORITIES, SERVICE_TIME_TASK, PROBALITIES, LAMBDAS)
    for task in tasks:
        print(task)

    task_time = [task.arrival_time for task in tasks]
    plt.figure(figsize=(10, 5))
    plt.plot(range(NUM_TASKS), sorted(task_time))
    plt.xlabel('Tasks')
    plt.ylabel('Arrival time')
    plt.title('Arrival time of tasks')
    plt.show()

