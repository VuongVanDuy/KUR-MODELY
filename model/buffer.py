from .task import Task

class Buffer:
    def __init__(self, max_size=10) -> None:
        self.entries = []
        self.max_size = max_size

    def add(self, entries: Task) -> None:
        if len(self.entries) < self.max_size:
            self.entries.append(entries)
        else:
            print("Buffer đầy, không thể thêm task!")
        self.entries.sort(key=lambda x: x.priority, reverse=True)

    def get(self) -> Task:
        return self.entries.pop(0) if self.entries else None

    def isEmpty(self) -> bool:
        return len(self.entries) == 0

    def reset(self) -> None:
        self.entries.clear()

    def __len__(self) -> int:
        return len(self.entries)

    def __getitem__(self, item: int) -> Task:
        return self.entries[item]

    def __repr__(self) -> str:
        str = ""
        for entry, id in enumerate(self.entries):
            str += f"{id}: {entry}\n"
        return str


if __name__ == '__main__':
    from task import generate_tasks
    task = generate_tasks(5, [0.8, 0.2], [0.5, 1.2])
    buffer = Buffer()
    for t in task:
        buffer.add(t)
    print(buffer)
    print(buffer.get())

