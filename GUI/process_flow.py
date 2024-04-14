import subprocess

import Exceptions as ExeptGUI


# TODO Create function to launch thread?
class client_flow(object):
    def __init__(self, graph_plot, graph_figure, name="Client Flow"):
        self.graph = graph_figure
        self.plot = graph_plot
        self.name = name
        # Terminate vars
        self.finished = False
        # Start flow vars
        self.running = False
        self.pOpen_object = None
        self.start_time = 0.00
        # Initializer vars
        self.line = None
        self.initialized = False  # initializer
        self.exe_path = None
        self.bytes = None
        self.num_send = None
        self.my_port = None
        self.server_port = None

        self.data_history = []

    def initializer(self, exe_path, num_send, bytes_each, my_port, server_port, color):
        if self.initialized:  # don't let users redefine flows
            raise ExeptGUI.RedefineInstanceArgs
        # Set parameters
        self.exe_path = exe_path
        self.bytes = bytes_each
        self.num_send = num_send
        self.my_port = my_port
        self.server_port = server_port
        # Initialize plot
        line, = self.plot.plot([], [], label=self.name, color=color)  # Creates empty line of plot
        self.line = line
        self.plot.legend()
        self.initialized = True

    def start_flow(self, start_time):
        """Creates subprocess pipe on the set instances .exe path. Returns new POpen instance"""
        if not self.initialized:
            raise ExeptGUI.StartUninitializedFlow
        try:
            pipe_client = subprocess.Popen([self.exe_path, self.num_send, self.bytes, self.my_port, self.server_port],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            self.pOpen_object = pipe_client
            self.running = True
            self.start_time = start_time
            return pipe_client

        except Exception as e:
            print("Failed to start subprocess:", str(e))
            return None

    def terminate(self):
        if self.pOpen_object.poll() is None:  # Process still running
            self.pOpen_object.kill()
        self.running = False
        self.finished = True

    # Line / Graph manipulation methods
    def data_point(self, pack_rtt, pack_end_time,
                   pack_num):  # todo. instead of redrawing. Only draw in the order of pack num. If pack num not in order, add it to a list, or hash with key = expected index
        """X = RTT - Floating point     Y = Floating Point Epoch Time"""
        if not self.initialized:
            raise ExeptGUI.StartUninitializedFlow

        time_t = float(pack_end_time) - self.start_time

        new_entry = (pack_num, [pack_rtt, time_t])
        self.data_history.append(new_entry)
        self.data_history = sorted(self.data_history, key=lambda x: x[0])
        self.draw_line()

    def draw_line(self):
        x_data = [entry[1][1] for entry in self.data_history]  # time data
        y_data = [entry[1][0] for entry in self.data_history]  # RTT data
        # Update args + redraw. Pipe buffer inputs can be out of order. Here we order them
        self.line.set_data(x_data, y_data)
        self.line.axes.relim()
        self.line.axes.autoscale_view()
        self.line.figure.canvas.draw()
