class CombatLogger:
    def __init__(self, verbose=True):
        self.entries = []
        self.verbose = verbose

    def log(self, msg):
        self.entries.append(msg)
        if self.verbose:
            print(msg)

    def log_combat_end(self, winner, rounds):
        self.log(f"Combat Over. Winner: {winner} in {rounds} rounds")

    def get_full_log(self):
        return "\n".join(self.entries)
