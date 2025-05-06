import threading

# Custom logger class to capture yt-dlp output
class StreamingLogger:
    def __init__(self):
        self.lock = threading.Lock()
        self.lines = []

    def debug(self, msg): pass
    def warning(self, msg):
        with self.lock:
            self.lines.append(f"WARNING: {msg}")
    def error(self, msg):
        with self.lock:
            self.lines.append(f"ERROR: {msg}")
    def info(self, msg):
        with self.lock:
            self.lines.append(msg)

    def push_line(self, line):
        with self.lock:
            self.lines.append(line)

    def pop_lines(self):
        with self.lock:
            current = self.lines[:]
            self.lines.clear()
        return current