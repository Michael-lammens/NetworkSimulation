# TCPVegasSimulation

Networking Algorithm Visualizer

Intro:

  Soon to be:   
    - (Mostly) Portable tool to visualize headless networking processes in real time. Adjustable args, concurrent client connections + shared graph.
    - Split test different algorithms on the same graph

    Why i'm building it:
    In building a Vegas simulation I wanted to visualize my program in its real real time running state. For this I didnt want a single use, coupled GUI. I also didnt want to 
    impose higher memory usage or latency on my simulation. Essentially I wanted my own visual interface without additional overhead on the running processes and with minimal 
    mutual dependency.   
    My solution is dynamically embedding C processes into a Tkinter GUI.
    
    We can achieve our goals by launching subprocesses and piping STDOUT to dedicated python threads. 
    Formatted C proccess output is the only dependency between the GUI and C processes.
    
    Currently my simulation is a client side CCA. I have individual client, server and emulator C processes. We launch the single Emulator and Server procs on initialization
    and the GUI interface allows us to create K number of client threads at any time with different arguments. This way we can test the networks behaviors and how all the 
    other client CCA's repond to these changes in real time. Concurrent client threads will be differentiated by their line colour on the shared graph.
   
    How it works:

    GUI Dir:
      Eventually this will be handled in the interface but all command line args, file paths etc are hardcoded here.

    Algortihm Dir:
      Your C processes. Eventually we just select them in GUI







    
