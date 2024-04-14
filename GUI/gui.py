import os
import subprocess
import threading
import time
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
import process_flow as flow
import Exceptions as ExeptGUI

current_directory = os.path.dirname(__file__)
vegascode_directory = os.path.abspath(os.path.join(current_directory, '..', 'VegasCode'))

client_path = os.path.join(vegascode_directory, 'client')
emulator_path = os.path.join(vegascode_directory, 'emulate')
server_path = os.path.join(vegascode_directory, 'server')

# Emulator Args
em_bandwidth = "100"  # BPS
min_rtt = "1"
delay_d_max = ".1"
port_emulator = "32582"
port_server = "32400"
port_client = "40009"

queue_s = queue.Queue()
p_open_objects = {"clients": []}
all_rec_packets = []


def get_line_if_exists(pipe):
    try:
        for line in iter(pipe.readline, ''):
            queue_s.put(line.strip())
    finally:
        pipe.close()

def get_log_type(data_log):
    log_type = data_log.split(" | ", 1)[0]
    if len(log_type) == 0:
        raise ExeptGUI.ParseLogNoTypeSpecified
    return log_type


def parse_log_to_entry(data_log):
    data_dict = {}

    data_log = data_log.split(" | ", 1)[1] # removes the leading log type
    data_val_list = str(data_log).split(',')

    for entry in data_val_list:
        key, value = entry.split(": ")
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass  # Keep value as a string if conversion fails
        data_dict[key.strip()] = value
    return data_dict


def update_gui():
    try:
        next_line = queue_s.get_nowait()
        client_obj = next_line[0]
        logged_line = next_line[1]

        log_type = get_log_type(logged_line)
        print(log_type)

        new_entry = parse_log_to_entry(logged_line)
        all_rec_packets.append(new_entry)
        print(new_entry)
        pack_rtt = float(new_entry['RTT'])
        pack_end = float(new_entry['end_time'])
        pack_num = int(new_entry['Pack#'])

        print(pack_rtt, pack_end)
        # add pack to instance + GUI
        client_obj.data_point(pack_rtt, pack_end, pack_num)
        # todo add these back into their sections + relative to client name
        # base_rtt_label.config(text="Base-RTT: " + str(new_entry['Base_RTT']))
        # window_label.config(text="Window Size: " + str(new_entry['WS']))
        # alpha_label.config(text="Alpha: " + str(new_entry['Alpha']))
        # beta_label.config(text="Beta: " + str(new_entry['Beta']))
    except queue.Empty:
        # Queue is empty, do nothing
        pass
    root.after(500, update_gui)


# todo create instances with these pipes. Make flow and generals(?) extend base_subproc
def create_background_processes():
    with open(os.devnull, 'w') as devnull:
        pipe_em = subprocess.Popen(
            [emulator_path, em_bandwidth, min_rtt, delay_d_max, port_emulator, port_server],
            stdout=devnull, universal_newlines=True)
        pipe_serv = subprocess.Popen([server_path, port_server],
                                     stdout=devnull, universal_newlines=True)
    p_open_objects["emulate"] = pipe_em
    p_open_objects["server"] = pipe_serv


"""
Thread that checks procs are still running. If one terminates, exit the program
"""


def poll_routine():
    server_proc = p_open_objects["server"]
    emulator_proc = p_open_objects["emulate"]
    print("BGS: RUNNING...")
    while True:
        emulator_status = emulator_proc.poll()
        server_status = server_proc.poll()
        if emulator_status is not None and emulator_status != 0:
            print(f"Emulator process exited with spite: {emulator_status}")
            exit(1)
        elif server_status is not None and server_status != 0:
            print(f"Server process exited with spite: {server_status}")
            exit(1)
        time.sleep(2)


# -------------------------------
# -            GUI              -
# -------------------------------


# Screen dimensions
SCREEN_WIDTH = 1425
SCREEN_HEIGHT = 1100


def create_new_client_callback():
    # Client parameters from user input
    NC_proc_name = str(proc_name_entry.get())
    NC_size = str(proc_bytesize.get())
    NC_num_send = str(proc_num_send.get())
    NC_our_port = str(proc_our_port.get())
    NC_line_color = str(proc_color.get())

    len_client = len(p_open_objects['clients'])
    if len_client == 0:
        start_time = float(time.time())
    else:
        start_time = p_open_objects['clients'][0].start_time
    # Create new client instance
    new_client_instance = flow.client_flow(plot, figure, NC_proc_name)
    new_client_instance.initializer(client_path, NC_num_send, NC_size, NC_our_port, port_emulator, NC_line_color)
    new_client_instance.start_flow(start_time)

    p_open_objects["clients"].append(new_client_instance)

    # Handle buffer reading from subprocess stdout
    def read_data_from_c(
            client_obj):  # todo Make this generalized accross all threads with select(). Append data into our own buffer. (This replaces the pipes 64kb set buffer overflow with ours)
        pipe = client_obj.pOpen_object.stdout
        while True:
            time.sleep(0.1)  # Sleep to reduce CPU usage. todo we still have big memory usage somewhere
            try:
                for line in iter(pipe.readline, ''):
                    queue_s.put((client_obj, line.strip()))
            finally:
                pipe.close()

    read_thread = threading.Thread(target=read_data_from_c, args=(new_client_instance,))
    read_thread.daemon = True  # Kill with main
    read_thread.start()


def create_graph(canvas):
    figure_g = Figure(figsize=(5, 4), dpi=100)
    plot_g = figure_g.add_subplot(111)
    # Setting static axis limits
    plot_g.set_xlim([0, 180])
    plot_g.set_ylim([0, 50])
    plot_g.set_title('CCA Flow')
    plot_g.set_xlabel('Time (T)')
    plot_g.set_ylabel('RTT')

    matplotlib_canvas = FigureCanvasTkAgg(figure_g, master=canvas)
    matplotlib_widget = matplotlib_canvas.get_tk_widget()
    matplotlib_widget.pack(fill=tk.BOTH, expand=True)

    return plot_g, figure_g


# --------------------------------
# -  PAGE LAYOUT / GRID SECTIONS -
# --------------------------------


root = tk.Tk()
root.title("Real-Time Data Display")
root.geometry('{}x{}'.format(SCREEN_WIDTH, SCREEN_HEIGHT))

# Configure grid rows and columns in root
root.grid_rowconfigure(0, weight=3)  # Top row with larger height
root.grid_rowconfigure(1, weight=1)  # Bottom row with smaller height
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Create and place canvas widgets directly on root using grid
canvas1 = tk.Canvas(root, bg='light grey')
canvas1.grid(row=0, column=0, sticky='nsew')

top_right = tk.Canvas(root, bg='light grey')
top_right.grid(row=0, column=1, sticky='nsew')

canvas3 = tk.Canvas(root, bg='light grey')
canvas3.grid(row=1, column=0, sticky='nsew')

# Bottom Right Create New Client
bottom_right = tk.Canvas(root, bg='light grey')
bottom_right.grid(row=1, column=1, sticky='nsew')
bottom_right.create_text(100, 20, text="Create New Client", fill="black", font=('Helvetica', '16'))

# Creating entry widgets and labels
proc_name_entry = tk.Entry(bottom_right)
bottom_right.create_window(230, 70, window=proc_name_entry)
label_name = tk.Label(bottom_right, text="Process Name:")
bottom_right.create_window(70, 70, window=label_name)

proc_bytesize = tk.Entry(bottom_right)
bottom_right.create_window(230, 100, window=proc_bytesize)
label_bytesize = tk.Label(bottom_right, text="Byte Size:")
bottom_right.create_window(70, 100, window=label_bytesize)

proc_num_send = tk.Entry(bottom_right)
bottom_right.create_window(230, 130, window=proc_num_send)
label_num_send = tk.Label(bottom_right, text="Number to Send:")
bottom_right.create_window(70, 130, window=label_num_send)

proc_our_port = tk.Entry(bottom_right)
bottom_right.create_window(230, 160, window=proc_our_port)
label_our_port = tk.Label(bottom_right, text="Our Port:")
bottom_right.create_window(70, 160, window=label_our_port)

proc_color = tk.Entry(bottom_right)
bottom_right.create_window(230, 190, window=proc_color)
label_color = tk.Label(bottom_right, text="Color:")
bottom_right.create_window(70, 190, window=label_color)

button = tk.Button(bottom_right, text="Submit", command=create_new_client_callback)
bottom_right.create_window(100, 220, window=button)

# Example of drawing on a canvas
canvas1.create_text(50, 20, text="Top Left", fill="black", font=('Helvetica', '16'))
top_right.create_text(50, 20, text="Top Right", fill="black", font=('Helvetica', '16'))
canvas3.create_text(50, 20, text="Bottom Left", fill="black", font=('Helvetica', '16'))
is_first = False
# ----------------------------
# -  GRAPH TOP RIGHT SECTION -
# ----------------------------
plot, figure = create_graph(top_right)

# -----------------
# -  DISPLAY DATA -
# -----------------


# real time update animation. Merge into the recv calls
# move()


# -------------------------------
# -         THREADING           -
# -------------------------------

# Start a thread to continuously read data from the C program
create_background_processes()
print("Created BGS")
# read_thread = threading.Thread(target=poll_routine)
# read_thread.daemon = True  # Daemonize thread so it automatically dies when the main program exits
# read_thread.start()
print("Polling BGS")

update_gui()
# Start the GUI main loop
root.mainloop()
