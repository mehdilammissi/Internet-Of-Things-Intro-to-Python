class ReactionLog:
    def __init__(self, player):
        self.player = player
        self.times = []

    def add(self, ms):
        self.times.append(ms)

    def count(self):
        return len(self.times)

    def best(self):
        if not self.times:
            return None
        return min(self.times)

    def average(self):
        if not self.times:
            return None
        return sum(self.times) / len(self.times)

    def summary(self):
        if not self.times:
            return f"{self.player}: no valid rounds"
        return (f"{self.player}: {self.count()} rounds, "
                f"best {self.best():.0f} ms, average {self.average():.0f} ms")
