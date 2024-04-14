# TCPVegasSimulation

Networking Algorithm Visualizer

Intro:

  Soon to be:   
    - (Mostly) Portable tool to visualize headless networking processes in real time. Adjustable args, concurrent client connections + shared graph.
    - Split test different algorithms on the same graph

    GUI launches subprocesses and pipes STDOUT to dedicated python threads. 
    Formatted C proccess output is the only dependency between the GUI and C processes.
    
    Currently my simulation is a client side CCA. I have many individual clients and single server and emulator C processes. We launch the single Emulator and Server procs on initialization
    and the GUI interface allows us to create K number of client threads at any time with different arguments. This way we can test the networks behaviors and how all the 
    other client CCA's repond to these changes in real time. Concurrent client threads are differentiated by their line colour on the shared graph.
   
    Sample Run:


<img width="796" alt="DemoRunSim" src="https://github.com/Michael-lammens/NetworkSimulation/assets/94767965/fea08f16-6510-4e9d-943e-71800f1cdf6f">





    
