import signal


class DockerStop:
    """Class for catch stop signal from Docker."""
    stop_now = False

    def __init__(self):
        signal.signal(signal.SIGTERM, self.stop_gracefully)

    def stop_gracefully(self, signum, frame):
        self.stop_now = True
