
PROJECT: PROCESS SCHEDULING SIMULATOR
COURSE:OPERATING SYSTEMS

Name:Sefa Tanrısever
Student ID:220444084


1. PROJECT DESCRIPTION
----------------------
This program is a comprehensive Process Scheduling Simulator designed to 
visualize and analyze four fundamental CPU scheduling algorithms:
- First-Come, First-Served (FCFS) [Non-preemptive]
- Shortest Job First (SJF/SRTF) [Preemptive/Non-preemptive variants]
- Priority Scheduling [Preemptive/Non-preemptive variants]
- Round Robin (RR) [Preemptive] with a configurable Time Quantum.

The simulator provides both a GUI (Graphical User Interface) and a 
detailed terminal output to display Gantt Charts, process tables, 
and performance metrics (Avg TAT, Avg WT, CPU Utilization).

2.Files Included:
---------------
1. scheduler.py  - Main source code (Python).
2. processes.txt - Sample input file.
3. starvation.txt - Input file demonstrating starvation.
4. scheduler.exe - Executable version (Windows).
5. Report.pdf    - Analysis and discussion.

3. PREREQUISITES
----------------
- Python 3.x
- Tkinter library (usually included with standard Python installations)

4. HOW TO RUN
-------------
You can start the simulator by executing the main python file via terminal:

    python scheduler.py

Upon launching, the GUI allows you to:
- Input process data manually (Format: PID, Arrival, Burst, Priority).
- Load data from an external file (e.g., processes.txt).
- Set the Time Quantum for the Round Robin algorithm.
- Start simulations for different algorithms using the side-panel buttons.

5. SYSTEM DESIGN & DATA STRUCTURES
----------------------------------
- Process Class: Acts as a Process Control Block (PCB) storing PID, 
  Arrival Time, Burst Time, and Priority. It also tracks dynamic 
  variables like Remaining Time and Finish Time.
- Simulator Class: Contains the core scheduling logic.
- Time Management: A 'current_time' variable acts as the simulation clock, 
  incrementing based on execution or idle periods.
- Queue Management: Uses 'collections.deque' for efficient Round Robin 
  ready-queue operations and list filtering for priority/SJF selection.

6. INPUT FILE FORMAT
--------------------
The simulator accepts .txt files where each line follows this comma-separated format:
Process_ID, Arrival_Time, Burst_Time, Priority

Example (processes.txt):
P1, 0, 8, 3
P2, 1, 4, 1
P3, 2, 9, 4
P4, 3, 5, 2

7. SIMULATION OUTPUTS
---------------------
For every execution, the program generates:
- A visual Gantt Chart with rocket-fire animations.
- A table containing: Finish Time, Turnaround Time, and Waiting Time.
- Global statistics: Average Turnaround Time, Average Waiting Time, 
  and CPU Utilization percentage.
- Terminal Log: A text-based summary is also printed to the standard output.

