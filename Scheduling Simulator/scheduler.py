import sys
import copy
import random
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# High DPI Awareness settings for clearer UI rendering on Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# SCI-FI THEME CONSTANTS & COLORS

BG_SPACE = "#0B0E14"       # Dark space background
PANEL_BG = "#161B22"       # Dark grey panel background
NEON_CYAN = "#00F3FF"      # Accent color for titles/lines
NEON_GREEN = "#39FF14"     # Status and load color
NEON_ORANGE = "#FFAC1C"    # RAM and rocket fire color
CRITICAL_RED = "#FF3131"   # Error or high priority color
TEXT_COLOR = "#E0E6ED"     # Primary text color
GANTT_LIGHT_BG = "#1C2533" # Background for the Gantt chart area

# List of vibrant colors assigned to different processes
PROCESS_COLORS = ["#FF3131", "#39FF14", "#00F3FF", "#FFAC1C", "#F0DB4F", "#FF00FF", "#7D26CD", "#00FF7F", "#FF4500"]

class Process:
    """Class representing a single CPU process entity."""
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid                                   # Process ID (e.g., P1)
        self.arrival_time = int(arrival_time)           # Time the process arrives in the ready queue
        self.burst_time = int(burst_time)               # Total CPU time required
        self.priority = int(priority)                   # Priority level (lower value = higher priority)
        self.remaining_time = self.burst_time           # Time left to complete (used in preemptive algos)
        self.finish_time = 0                            # Time when process execution ends
        self.ram_size = random.randint(50, 256)         # Simulated RAM consumption in MB
        self.color = random.choice(PROCESS_COLORS)      # Randomly assigned color for visualization

class Simulator:
    """Class containing the core scheduling logic."""
    def __init__(self, processes):
        self.original_processes = processes             # Store original list to allow resets
        self.cs_count = 0                               # Counter for Context Switches
        self.busy_time = 0                              # Total time CPU was actively working

    def reset_simulation(self):
        """Resets variables and returns a fresh copy of processes for a new run."""
        self.cs_count = 0
        self.busy_time = 0
        return copy.deepcopy(self.original_processes)

    def run_algorithm(self, algo_name, tq=3):
        """Routing function to call the selected scheduling algorithm."""
        if algo_name == "FCFS": return self.run_fcfs()
        elif algo_name == "SJF": return self.run_sjf_preemptive()
        elif algo_name == "PRIORITY": return self.run_priority_preemptive()
        elif algo_name == "ROUND ROBIN": return self.run_rr(tq)

    def run_fcfs(self):
        """First Come First Served - Non-preemptive."""
        processes = self.reset_simulation()
        processes.sort(key=lambda x: x.arrival_time)    # Sort by arrival time
        current_time, gantt_log, completed = 0, [], []
        last_pid = None

        for p in processes:
            # Handle idle time if CPU has no process to run
            if current_time < p.arrival_time:
                gantt_log.append((current_time, p.arrival_time, "IDLE", "#2F363D"))
                current_time = p.arrival_time
            
            # Increment context switch if switching between different processes
            if last_pid is not None and last_pid != p.pid: self.cs_count += 1
            
            start_t = current_time
            self.busy_time += p.burst_time
            current_time += p.burst_time
            p.finish_time = current_time
            gantt_log.append((start_t, current_time, p.pid, p.color))
            completed.append(p)
            last_pid = p.pid
        
        util = (self.busy_time / current_time * 100) if current_time > 0 else 0
        return completed, gantt_log, self.cs_count, util

    def run_sjf_preemptive(self):
        """Shortest Remaining Time First (SRTF) - Preemptive."""
        processes = self.reset_simulation()
        current_time, completed, gantt_log = 0, [], []
        last_pid = None
        
        while len(completed) < len(processes):
            # Find processes that have arrived and are not finished
            available = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
            
            if not available:
                next_arr = min(p.arrival_time for p in processes if p.remaining_time > 0)
                gantt_log.append((current_time, next_arr, "IDLE", "#2F363D"))
                current_time = next_arr
                continue
            
            # Pick the process with the shortest remaining time
            next_p = min(available, key=lambda x: (x.remaining_time, x.arrival_time))
            
            if last_pid is not None and last_pid != next_p.pid: self.cs_count += 1
            
            start_t = current_time
            next_p.remaining_time -= 1                  # Execute for 1 unit of time
            self.busy_time += 1
            current_time += 1
            
            # Merge Gantt log entries if the same process continues execution
            if gantt_log and gantt_log[-1][2] == next_p.pid:
                gantt_log[-1] = (gantt_log[-1][0], current_time, next_p.pid, next_p.color)
            else:
                gantt_log.append((start_t, current_time, next_p.pid, next_p.color))
            
            if next_p.remaining_time == 0:
                next_p.finish_time = current_time
                completed.append(next_p)
            last_pid = next_p.pid
            
        util = (self.busy_time / current_time * 100) if current_time > 0 else 0
        return completed, gantt_log, self.cs_count, util

    def run_priority_preemptive(self):
        """Preemptive Priority Scheduling."""
        processes = self.reset_simulation()
        current_time, completed, gantt_log = 0, [], []
        last_pid = None
        
        while len(completed) < len(processes):
            available = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]
            
            if not available:
                next_arr = min(p.arrival_time for p in processes if p.remaining_time > 0)
                gantt_log.append((current_time, next_arr, "IDLE", "#2F363D"))
                current_time = next_arr
                continue
            
            # Pick process with the highest priority (lowest numeric value)
            next_p = min(available, key=lambda x: (x.priority, x.arrival_time))
            
            if last_pid is not None and last_pid != next_p.pid: self.cs_count += 1
            
            start_t = current_time
            next_p.remaining_time -= 1
            self.busy_time += 1
            current_time += 1
            
            if gantt_log and gantt_log[-1][2] == next_p.pid:
                gantt_log[-1] = (gantt_log[-1][0], current_time, next_p.pid, next_p.color)
            else:
                gantt_log.append((start_t, current_time, next_p.pid, next_p.color))
                
            if next_p.remaining_time == 0:
                next_p.finish_time = current_time
                completed.append(next_p)
            last_pid = next_p.pid
            
        util = (self.busy_time / current_time * 100) if current_time > 0 else 0
        return completed, gantt_log, self.cs_count, util

    def run_rr(self, tq):
        """Round Robin Scheduling with a Time Quantum (TQ)."""
        processes = self.reset_simulation()
        processes.sort(key=lambda x: x.arrival_time)
        current_time, completed, gantt_log = 0, [], []
        queue = deque()                                 # Ready Queue
        p_idx, last_pid = 0, None
        
        while len(completed) < len(processes):
            # Add all processes that have arrived to the queue
            while p_idx < len(processes) and processes[p_idx].arrival_time <= current_time:
                queue.append(processes[p_idx])
                p_idx += 1
            
            if not queue:
                start_idle = current_time
                current_time = processes[p_idx].arrival_time
                gantt_log.append((start_idle, current_time, "IDLE", "#2F363D"))
                continue
                
            p = queue.popleft()                         # Get process from front of queue
            if last_pid is not None and last_pid != p.pid: self.cs_count += 1
            
            start_t = current_time
            exec_time = min(tq, p.remaining_time)       # Run for TQ or remaining time
            p.remaining_time -= exec_time
            self.busy_time += exec_time
            current_time += exec_time
            gantt_log.append((start_t, current_time, p.pid, p.color))
            
            # Check for new arrivals during execution
            while p_idx < len(processes) and processes[p_idx].arrival_time <= current_time:
                queue.append(processes[p_idx])
                p_idx += 1
            
            # If not finished, send back to the end of the queue
            if p.remaining_time > 0: queue.append(p)
            else:
                p.finish_time = current_time
                completed.append(p)
            last_pid = p.pid
            
        util = (self.busy_time / current_time * 100) if current_time > 0 else 0
        return completed, gantt_log, self.cs_count, util

class SpaceBaseApp:
    """Main GUI Application class."""
    def __init__(self, root):
        self.root = root
        self.root.title("PROCESS SCHEDULING SIMULATOR")
        self.root.geometry("1450x950")
        self.root.configure(bg=BG_SPACE)
        self.last_results = None
        self.cpu_data = [20] * 32                       # Fake load data for the monitor graph
        
        # UI Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", background=PANEL_BG, foreground=TEXT_COLOR, fieldbackground=PANEL_BG, rowheight=30)
        self.style.configure("Treeview.Heading", background="#0D1117", foreground=NEON_CYAN, font=("Courier", 10, "bold"))

        self._setup_ui()
        self.update_monitor()                           # Start the animated CPU monitor
        self.root.after(500, self.initial_rocket_launch) # Visual intro message

    def _setup_ui(self):
        """Initializes all GUI components."""
        # Top Header
        header = tk.Frame(self.root, bg=BG_SPACE, highlightbackground=NEON_CYAN, highlightthickness=1)
        header.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(header, text="⚡ PROCESS SCHEDULING SIMULATOR ⚡", font=("Courier", 20, "bold"), bg=BG_SPACE, fg=NEON_CYAN).pack(pady=5)

        main_frame = tk.Frame(self.root, bg=BG_SPACE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15)

        # Left Sidebar (Controls)
        sidebar_container = tk.Frame(main_frame, bg=PANEL_BG, width=360, highlightbackground=NEON_CYAN, highlightthickness=1)
        sidebar_container.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.canvas_side = tk.Canvas(sidebar_container, bg=PANEL_BG, width=340, highlightthickness=0)
        scrollbar_side = tk.Scrollbar(sidebar_container, orient="vertical", command=self.canvas_side.yview)
        self.scrollable_sidebar = tk.Frame(self.canvas_side, bg=PANEL_BG)

        self.scrollable_sidebar.bind("<Configure>", lambda e: self.canvas_side.configure(scrollregion=self.canvas_side.bbox("all")))
        self.canvas_side.create_window((0, 0), window=self.scrollable_sidebar, anchor="nw")
        self.canvas_side.configure(yscrollcommand=scrollbar_side.set)
        scrollbar_side.pack(side="right", fill="y")
        self.canvas_side.pack(side="left", fill="both", expand=True)

        # CPU Load Monitor Graphics
        self.monitor_frame = tk.Frame(self.scrollable_sidebar, bg="#0D1117", highlightbackground=NEON_GREEN, highlightthickness=1)
        self.monitor_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(self.monitor_frame, text="⚡ CORE_LOAD ⚡", bg="#0D1117", fg=NEON_GREEN, font=("Courier", 8, "bold")).pack()
        self.monitor_canvas = tk.Canvas(self.monitor_frame, bg="#0D1117", width=300, height=60, highlightthickness=0)
        self.monitor_canvas.pack(pady=5)

        # Process Input Area
        tk.Label(self.scrollable_sidebar, text="[ PROCESS_LIST ]", bg=PANEL_BG, fg=NEON_CYAN, font=("Courier", 10, "bold")).pack(pady=5)
        self.text_input = tk.Text(self.scrollable_sidebar, height=12, width=38, bg="#0D1117", fg=NEON_GREEN, font=("Consolas", 9), relief=tk.FLAT)
        self.text_input.pack(padx=10)
        self.text_input.insert(tk.END, "P1, 0, 8, 3\nP2, 1, 4, 1\nP3, 2, 9, 4\nP4, 3, 5, 2")

        # Time Quantum Input
        tq_fm = tk.Frame(self.scrollable_sidebar, bg=PANEL_BG)
        tq_fm.pack(pady=10)
        tk.Label(tq_fm, text="TIME QUANTUM:", bg=PANEL_BG, fg=TEXT_COLOR, font=("Courier", 9)).grid(row=0, column=0)
        self.tq_entry = tk.Entry(tq_fm, width=5, bg="#0D1117", fg=NEON_CYAN, insertbackground=NEON_CYAN, justify="center")
        self.tq_entry.insert(0, "3")
        self.tq_entry.grid(row=0, column=1, padx=5)

        # File and Random Buttons
        btn_fm = tk.Frame(self.scrollable_sidebar, bg=PANEL_BG)
        btn_fm.pack()
        self.create_sci_btn(btn_fm, "📂 LOAD", self.load_file, NEON_CYAN).grid(row=0, column=0, padx=2)
        self.create_sci_btn(btn_fm, "🎲 RANDOM", self.generate_random, NEON_CYAN).grid(row=0, column=1, padx=2)

        # Algorithm Selection Buttons
        tk.Label(self.scrollable_sidebar, text="[ EXECUTION_COMMANDS ]", bg=PANEL_BG, fg=NEON_CYAN, font=("Courier", 10, "bold")).pack(pady=10)
        for a in ["FCFS", "SJF", "PRIORITY", "ROUND ROBIN"]:
            self.create_sci_btn(self.scrollable_sidebar, f"▶ START {a}", lambda x=a: self.run_sim(x), NEON_CYAN).pack(pady=2, fill=tk.X, padx=20)

        # Right Panel (Visualization & Tables)
        right_panel = tk.Frame(main_frame, bg=BG_SPACE)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Gantt Chart Area
        tk.Label(right_panel, text=">> GANTT CHART VISUALIZATION", bg=BG_SPACE, fg=NEON_CYAN, font=("Courier", 10, "bold")).pack(anchor="w", padx=10)
        gantt_container = tk.Frame(right_panel, bg=GANTT_LIGHT_BG, highlightbackground=NEON_CYAN, highlightthickness=1)
        gantt_container.pack(fill=tk.X, pady=5, padx=10)
        self.canvas = tk.Canvas(gantt_container, bg=GANTT_LIGHT_BG, height=140, highlightthickness=0)
        h_scroll = tk.Scrollbar(gantt_container, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=h_scroll.set)
        self.canvas.pack(side=tk.TOP, fill=tk.X)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # RAM Visualization Area
        tk.Label(right_panel, text=">> RAM ALLOCATION FLOW", bg=BG_SPACE, fg=NEON_ORANGE, font=("Courier", 10, "bold")).pack(anchor="w", padx=10)
        ram_box = tk.Frame(right_panel, bg="#0D1117", highlightbackground=NEON_ORANGE, highlightthickness=1)
        ram_box.pack(fill=tk.X, pady=5, padx=10)
        self.ram_canvas = tk.Canvas(ram_box, bg="#0D1117", height=70, highlightthickness=0)
        ram_scroll = tk.Scrollbar(ram_box, orient="horizontal", command=self.ram_canvas.xview)
        self.ram_canvas.configure(xscrollcommand=ram_scroll.set)
        self.ram_canvas.pack(side=tk.TOP, fill=tk.X)
        ram_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Data Table (Treeview)
        cols = ("Process ID", "Arrival", "Burst", "Finish", "Turnaround", "Waiting", "RAM")
        self.tree = ttk.Treeview(right_panel, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Bottom Stats Bar
        self.footer = tk.Frame(right_panel, bg="#0A0F14", highlightbackground=NEON_GREEN, highlightthickness=2)
        self.footer.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        self.lbl_stats_all = tk.Label(self.footer, text="Avg TAT: 0.00 | Avg WT: 0.00 | CPU Util: 0.0%", bg="#0A0F14", fg=NEON_CYAN, font=("Consolas", 14, "bold"), pady=20)
        self.lbl_stats_all.pack(fill=tk.X)

    def create_sci_btn(self, parent, text, cmd, color, px=15):
        """Helper to create buttons with a Sci-Fi look."""
        btn = tk.Button(parent, text=text, command=cmd, bg="#1A1F26", fg=color, activebackground=color, activeforeground="black", font=("Courier", 9, "bold"), relief=tk.FLAT, highlightthickness=1, highlightbackground=color, padx=px, pady=5)
        return btn

    def update_monitor(self):
        """Animates a fake CPU load graph on the sidebar."""
        self.monitor_canvas.delete("all")
        self.cpu_data.pop(0)
        is_active = self.last_results is not None
        val = random.randint(70, 95) if is_active else random.randint(5, 15)
        self.cpu_data.append(val)
        for i in range(len(self.cpu_data)-1):
            self.monitor_canvas.create_line(i*10, 60-(self.cpu_data[i]*0.5), (i+1)*10, 60-(self.cpu_data[i+1]*0.5), fill=NEON_GREEN, width=1)
        self.root.after(200, self.update_monitor)

    def initial_rocket_launch(self):
        """Displays 'SYSTEM READY' on the canvas at startup."""
        self.root.update_idletasks()
        w = self.canvas.winfo_width()
        cx = w/2 if w > 1 else 600
        self.canvas.create_text(cx, 70, text="S Y S T E M     R E A D Y", fill=NEON_CYAN, font=("Courier", 18, "bold"), tags="initial_msg")

    def parse_input(self):
        """Reads and validates process data from the text area."""
        try:
            lines = self.text_input.get("1.0", tk.END).strip().split('\n')
            return [Process(*[x.strip() for x in line.split(',')]) for line in lines if line.strip()]
        except:
            messagebox.showerror("INPUT ERROR", "Format: PID, Arrival, Burst, Priority"); return []

    def load_file(self):
        """Loads process data from a text file."""
        path = filedialog.askopenfilename()
        if path:
            with open(path, "r") as f:
                self.text_input.delete("1.0", tk.END); self.text_input.insert(tk.END, f.read())

    def generate_random(self):
        """Generates random process data for quick testing."""
        self.text_input.delete("1.0", tk.END)
        for i in range(random.randint(5, 8)):
            self.text_input.insert(tk.END, f"P{i}, {random.randint(0, 10)}, {random.randint(2, 10)}, {random.randint(1, 5)}\n")

    def run_sim(self, algo):
        """Starts the simulation for the selected algorithm."""
        raw_tq = self.tq_entry.get().strip()
        if not raw_tq.isdigit() or int(raw_tq) <= 0:
            messagebox.showerror("INVALID TQ", "Time Quantum must be a positive integer!")
            return
        tq = int(raw_tq)

        procs = self.parse_input()
        if not procs: return 

        sim = Simulator(procs)
        completed, gantt, cs, util = sim.run_algorithm(algo, tq)
        self.last_results = (completed, gantt, cs, util, algo)
        self.draw_ram_map(completed)                      # Visualize RAM usage
        self.animate_gantt(gantt, completed, cs, util, algo) # Start Gantt animation

    def draw_ram_map(self, completed):
        """Draws a visual representation of RAM allocation."""
        self.ram_canvas.delete("all")
        curr_x = 10
        for p in completed:
            part_w = p.ram_size * 5
            self.ram_canvas.create_rectangle(curr_x, 10, curr_x+part_w, 60, fill=p.color, outline="white")
            self.ram_canvas.create_text(curr_x+part_w/2, 35, text=f"{p.pid}", fill="black", font=("Arial", 8, "bold"))
            curr_x += part_w
        self.ram_canvas.config(scrollregion=(0, 0, curr_x + 50, 70))

    def animate_gantt(self, gantt, completed, cs, util, algo):
        """Handles the step-by-step rocket animation on the Gantt Chart."""
        self.canvas.delete("all") 
        scale, x_off, y_off = 45, 30, 40
        total_duration = gantt[-1][1] if gantt else 0
        self.canvas.config(scrollregion=(0, 0, x_off + total_duration * scale + 150, 140))

        def draw_step(idx):
            if idx < len(gantt):
                s, e, pid, p_color = gantt[idx]
                
                def anim(curr_e):
                    # Progressively grow the bar to simulate execution
                    if curr_e < e - 0.05:
                        self.canvas.delete("rocket_obj")
                        self.canvas.create_rectangle(x_off+s*scale, y_off, x_off+curr_e*scale, y_off+50, fill=p_color, outline="white", tags="rocket_obj")
                        if pid != "IDLE":
                            rx = x_off+curr_e*scale
                            # Drawing the rocket fire triangle
                            self.canvas.create_polygon(rx, y_off+10, rx+15, y_off+25, rx, y_off+40, fill=NEON_ORANGE, tags="rocket_obj")
                        self.root.after(15, lambda: anim(curr_e + 0.2))
                    else:
                        # Finalize the bar and show PID
                        self.canvas.delete("rocket_obj")
                        self.canvas.create_rectangle(x_off+s*scale, y_off, x_off+e*scale, y_off+50, fill=p_color, outline="white")
                        self.canvas.create_text(x_off+(s+e)*scale/2, y_off+25, text=pid, fill="black" if pid != "IDLE" else "white", font=("Courier", 10, "bold"))
                        self.canvas.create_text(x_off+e*scale, y_off+65, text=str(e), fill=TEXT_COLOR, font=("Arial", 8))
                        draw_step(idx+1)
                anim(s)
            else:
                # Execution finished, update stats
                self.print_to_terminal(completed, cs, util, algo, gantt)
                self.update_gui_stats(completed, util)
        
        self.canvas.create_text(x_off, y_off+65, text="0", fill=TEXT_COLOR, font=("Arial", 8))
        draw_step(0)

    def print_to_terminal(self, completed, cs, util, algo, gantt):
        """Prints a detailed execution summary to the console/terminal."""
        print("\n" + "="*50)
        print(f"--- Scheduling Algorithm: {algo} ---")
        gantt_str = f"Gantt Chart: [{gantt[0][0]}]"
        for s, e, pid, col in gantt:
            gantt_str += f"--{pid}--[{e}]"
        print(gantt_str)
        print("\nProcess      | Finish Time | Turnaround Time | Waiting Time")
        print("-" * 55)
        t_wt, t_tat = 0, 0
        for p in sorted(completed, key=lambda x: x.pid):
            tat = p.finish_time - p.arrival_time
            wt = tat - p.burst_time
            t_tat += tat
            t_wt += wt
            print(f"{p.pid:<10} | {p.finish_time:<11} | {tat:<15} | {wt:<12}")
        n = len(completed)
        print("-" * 55)
        print(f"Average Turnaround Time: {t_tat/n:.2f}")
        print(f"Average Waiting Time: {t_wt/n:.2f}")
        print(f"CPU Utilization: {util:.1f}%")
        print(f"Context Switches: {cs}")
        print("="*50 + "\n")

    def update_gui_stats(self, completed, util):
        """Calculates final metrics and fills the Treeview table."""
        for row in self.tree.get_children(): self.tree.delete(row)
        t_wt, t_tat = 0, 0
        for p in sorted(completed, key=lambda x: x.pid):
            tat = p.finish_time - p.arrival_time
            wt = tat - p.burst_time
            t_tat += tat
            t_wt += wt
            self.tree.insert("", "end", values=(p.pid, p.arrival_time, p.burst_time, p.finish_time, tat, wt, f"{p.ram_size}MB"))
        avg_tat = t_tat/len(completed)
        avg_wt = t_wt/len(completed)
        # Update the UI footer with results
        self.lbl_stats_all.config(text=f"Avg TAT: {avg_tat:.2f} | Avg WT: {avg_wt:.2f} | CPU Util: {util:.1f}%", fg=NEON_CYAN)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceBaseApp(root)
    root.mainloop() # Start the main event loop