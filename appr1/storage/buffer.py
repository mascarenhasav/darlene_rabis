
# storage/buffer.py
class Buffer:
    def __init__(self, max_items=50):
        self.q = []
        self.max = max_items

    def push(self, data):
        if len(self.q) < self.max:
            self.q.append(data)

    def pop_all(self):
        batch = self.q[:]
        self.q.clear()
        return batch
