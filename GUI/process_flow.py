import subprocess

# todo, create list for all packets send and received... Create function to launch thread?
class client_flow(object):
    def __init__(self, exe_path, num_send, bytes, my_port, server_port):
        self.exe_path = exe_path
        self.bytes = bytes
        self.num_send = num_send
        self.my_port = my_port
        self.server_port = server_port

        self.pOpen_object = None
        self.finished = False
        self.running = False

    def start_flow(self):
        """Creates subprocess pipe on the set instances .exe path. Returns new POpen instance"""
        try:
            pipe_client = subprocess.Popen([self.exe_path, self.num_send, self.bytes, self.my_port, self.server_port],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            self.pOpen_object = pipe_client
            self.running = True
            return pipe_client
        except Exception as e:
            print("Failed to start the subprocess:", str(e))
            return None

    def terminate(self):
        if self.pOpen_object.poll() is None:  # Process is still running
            self.pOpen_object.kill()
        self.running = False
        self.finished = True
