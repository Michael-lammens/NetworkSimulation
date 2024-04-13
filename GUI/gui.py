import os
import subprocess
import threading
import time
import tkinter as tk
import queue
import random
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
num_packets = "1000"
bytes = "20"
queue_s = queue.Queue()
p_open_objects = {}
all_rec_packets=[]


def get_line_if_exists(pipe):
    try:
        line = pipe.readline().strip()
        if line:
            # Put the data into the global queue
            #print("FOUND LINE:", line)  # No need to decode strings
            queue_s.put(line)
            return True
    except Exception as e:
        print("Error:", e)
        return False


# todo also get stderr. Pipe = stdout right now
def read_data_from_c(pipe):
    while True:
        if not get_line_if_exists(pipe):  # conditional for testing purposes
            pass


def get_log_type(data_log):
    log_type = data_log.split(" | ", 1)[0]
    if len(log_type) == 0:
        raise ExeptGUI.ParseLogNoTypeSpecified
    return log_type



def parse_log_to_entry(data_log):
    data_dict = {}
    # get data from the global queue
    data_val_list = str(data_log).split(',')
    for entry in data_val_list:
        key, value = entry.split(": ")
        try:
            # Convert numeric values from strings to floats or integers
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass  # Keep the value as a string if conversion fails
        data_dict[key.strip()] = value
    return data_dict



def update_gui():
    try:
        logged_line = queue_s.get_nowait()
        log_type = get_log_type(logged_line)
        print(log_type)
        new_entry = parse_log_to_entry(logged_line)
        all_rec_packets.append(new_entry)
        print(all_rec_packets)

        base_rtt_label.config(text="Base-RTT: " + str(new_entry['Base_RTT']))
        window_label.config(text="Window Size: " + str(new_entry['WS']))
        alpha_label.config(text="Alpha: " + str(new_entry['Alpha']))
        beta_label.config(text="Beta: " + str(new_entry['Beta']))
    except queue.Empty:
        # Queue is empty, do nothing
        pass
    root.after(1000, update_gui)


def start_data_display():
    # Add functionality for the button here
    pass


# Create a pipe to communicate with the C program
"""
   Function to create all necessary sub procs. Called on 
  ./server 32400
  ./client 10000 20 40009 32582
"""


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
# Graph container
GRAPH_CONTAINER_WIDTH = 900
GRAPH_CONTAINER_HEIGHT = 600
# Graph Content. Overlay canvas slightly smaller than canvas container
GRAPH_WIDTH = 870
GRAPH_HEIGHT = 575
DISTANCE = 50
NUMBER = (GRAPH_CONTAINER_WIDTH // DISTANCE) + 1

graph_point_history = []


def move():
    # remove first
    data.pop(0)
    # add last
    data.append(random.randint(20, GRAPH_HEIGHT - 50))
    # remove all lines
    for point in graph_point_history:
        canvas_content.delete(point)
    graph_point_history.clear()
    # draw new lines
    for x, (y1, y2) in enumerate(zip(data, data[1:])):
        x1 = x * DISTANCE
        x2 = (x + 1) * DISTANCE  # x1 + DISTANCE
        graph_point = canvas_content.create_line([x1, y1, x2, y2], width=2)
        graph_point_history.append(graph_point)
    # run again after 500ms (0.5s)
    root.after(2000, move)


# --- main --- (lower_case names)
data = [random.randint(0, GRAPH_CONTAINER_HEIGHT) for _ in range(NUMBER)]

root = tk.Tk()
root.title("Real-Time Data Display")
root.geometry('{}x{}'.format(SCREEN_WIDTH, SCREEN_HEIGHT))

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# -----------------
# -  DISPLAY DATA -
# -----------------

# Create a label to display the data
base_rtt_label = tk.Label(root, text="Base RTT: ")
base_rtt_label.pack(side=tk.LEFT)

window_label = tk.Label(root, text="Window Size: ")
window_label.pack(side=tk.LEFT)

alpha_label = tk.Label(root, text="Alpha: ")
alpha_label.pack(side=tk.LEFT)

beta_label = tk.Label(root, text="Beta: ")
beta_label.pack(side=tk.LEFT)


# create graph container canvas
canvas_container = tk.Canvas(main_frame, bg="#E8E8E8", width=GRAPH_CONTAINER_WIDTH, height=GRAPH_CONTAINER_HEIGHT)
canvas_container.pack(side=tk.RIGHT)

# Add x-axis line bottom
canvas_container.create_line(0, GRAPH_CONTAINER_HEIGHT - 15, GRAPH_CONTAINER_WIDTH, GRAPH_CONTAINER_HEIGHT - 15,
                             fill="black", width=1)
index_interval = GRAPH_CONTAINER_WIDTH // 7
for i in range(7):
    x = i * index_interval
    canvas_container.create_line(x, GRAPH_CONTAINER_HEIGHT - 20, x, GRAPH_CONTAINER_HEIGHT - 10, fill="black", width=2)
    canvas_container.create_text(x, GRAPH_CONTAINER_HEIGHT - 10, text=str(i * 5), anchor=tk.N)
# Add y-axis line
canvas_container.create_line(25, GRAPH_CONTAINER_HEIGHT, 25, 0, fill="black", width=1)
index_interval_y = GRAPH_CONTAINER_HEIGHT // 7
for i in range(7):
    y = GRAPH_CONTAINER_HEIGHT - i * index_interval_y  # Reverse the calculation
    canvas_container.create_line(20, y, 30, y, fill="black", width=2)
    canvas_container.create_text(3, y, text=str(i * 5), anchor=tk.W)  # Adjust x-coordinate for the text

# create graph canvas
canvas_content = tk.Canvas(main_frame, bg="#E8E8E8", width=GRAPH_WIDTH, height=GRAPH_HEIGHT)
canvas_x = canvas_container.winfo_x()
canvas_y = canvas_container.winfo_y()
canvas_content.config(highlightthickness=0)
# Horizontal Lines
for i in range(7):
    y = GRAPH_CONTAINER_HEIGHT - i * index_interval_y  # Reverse the calculation
    canvas_content.create_line(0, y - 4, GRAPH_CONTAINER_WIDTH, y - 4, fill="#989898", width=1)

canvas_content.place(x=550, y=123)
# Vertical Lines
index_interval = GRAPH_CONTAINER_WIDTH // 7
for i in range(7):
    x = i * index_interval
    canvas_content.create_line(x + 97, GRAPH_CONTAINER_HEIGHT, x + 97, 0, fill="#989898", width=1)
canvas_content.place(x=550, y=123)

# start animation
move()



# -------------------------------
# -         THREADING           -
# -------------------------------

# Start a thread to continuously read data from the C program
create_background_processes()
print("Created BGS")
read_thread = threading.Thread(target=poll_routine)
read_thread.daemon = True  # Daemonize thread so it automatically dies when the main program exits
read_thread.start()
print("Polling BGS")

# test new client object

new_client_instance = flow.client_flow(client_path, num_packets,bytes, "40290", port_emulator)
new_client_popen = new_client_instance.start_flow()
print(new_client_popen)
p_open_objects["client"] = new_client_popen

read_thread = threading.Thread(target=read_data_from_c, args=(new_client_popen.stdout,))
read_thread.daemon = True  # Daemonize thread so it automatically dies when the main program exits
read_thread.start()

update_gui()
# Start the GUI main loop
root.mainloop()
