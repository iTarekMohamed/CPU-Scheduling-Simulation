import tkinter as tk
from tkinter import ttk, messagebox
import random

from scheduler_core import Process, run_fcfs, run_sjf, run_round_robin, run_priority

# ─── Color Palette ───────────────────────────────────────────────────────────
BG        = "#0d0f1a"
PANEL     = "#13162a"
BORDER    = "#1e2340"
ACCENT    = "#00e5ff"
ACCENT2   = "#7b2fff"
GREEN     = "#00ff9d"
YELLOW    = "#ffd166"
RED       = "#ff4d6d"
TEXT      = "#e0e8ff"
SUBTEXT   = "#6b7db3"
WHITE     = "#ffffff"


class CPUSchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Visualizer")
        self.geometry("1100x780")
        self.configure(bg=BG)
        self.resizable(True, True)

        self.processes = []
        self.pid_counter = 0
        self._build_ui()

    # ── UI Construction ────────────────────────────────────────────────────

    def _build_ui(self):
        # Top header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(hdr, text="⬡ CPU SCHEDULING VISUALIZER",
                 font=("Courier", 16, "bold"), fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(hdr, text="Operating Systems Project",
                 font=("Courier", 10), fg=SUBTEXT, bg=BG).pack(side="right", pady=6)

        sep = tk.Frame(self, bg=ACCENT, height=1)
        sep.pack(fill="x", padx=20, pady=(8, 0))

        # Main layout
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=12)

        self._build_left(main)
        self._build_right(main)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg=PANEL, bd=0, highlightthickness=1,
                        highlightbackground=BORDER)
        left.pack(side="left", fill="y", padx=(0, 10), ipadx=8, ipady=8)

        tk.Label(left, text="PROCESSES", font=("Courier", 11, "bold"),
                 fg=ACCENT2, bg=PANEL).pack(pady=(10, 4))

        # Add process form
        form = tk.Frame(left, bg=PANEL)
        form.pack(padx=10, pady=4, fill="x")

        fields = [("Arrival", 4), ("Burst", 4), ("Priority", 3)]
        self.entries = {}
        for label, w in fields:
            row = tk.Frame(form, bg=PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{label}:", font=("Courier", 9),
                     fg=SUBTEXT, bg=PANEL, width=8, anchor="w").pack(side="left")
            e = tk.Entry(row, width=w, font=("Courier", 10), bg=BORDER,
                         fg=TEXT, insertbackground=ACCENT,
                         relief="flat", bd=4)
            e.pack(side="left")
            e.insert(0, "0" if label == "Arrival" else "5" if label == "Burst" else "1")
            self.entries[label] = e

        btn_frame = tk.Frame(left, bg=PANEL)
        btn_frame.pack(pady=6)
        self._btn(btn_frame, "+ Add Process", self._add_process, ACCENT2).pack(side="left", padx=3)
        self._btn(btn_frame, "Random", self._random_processes, SUBTEXT).pack(side="left", padx=3)

        # Process list
        tk.Label(left, text="PROCESS TABLE", font=("Courier", 9, "bold"),
                 fg=SUBTEXT, bg=PANEL).pack(pady=(8, 2))

        cols = ("PID", "Arr", "Burst", "Pri")
        self.tree = ttk.Treeview(left, columns=cols, show="headings",
                                 height=8, selectmode="browse")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=BORDER, foreground=TEXT,
                        fieldbackground=BORDER, rowheight=22,
                        font=("Courier", 9))
        style.configure("Treeview.Heading", background=PANEL, foreground=ACCENT,
                        font=("Courier", 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT2)])

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=52, anchor="center")
        self.tree.pack(padx=8, pady=2)

        self._btn(left, "✕ Remove Selected", self._remove_process, RED).pack(pady=4)
        self._btn(left, "Clear All", self._clear_processes, SUBTEXT).pack(pady=2)

        # Algorithm selector
        tk.Label(left, text="ALGORITHM", font=("Courier", 9, "bold"),
                 fg=SUBTEXT, bg=PANEL).pack(pady=(12, 2))

        self.algo_var = tk.StringVar(value="FCFS")
        algos = [("FCFS", "FCFS"), ("SJF", "SJF"),
                 ("Round Robin", "RR"), ("Priority", "Priority")]
        for text, val in algos:
            tk.Radiobutton(left, text=text, variable=self.algo_var, value=val,
                           font=("Courier", 9), fg=TEXT, bg=PANEL,
                           selectcolor=ACCENT2, activebackground=PANEL,
                           activeforeground=ACCENT).pack(anchor="w", padx=20)

        # Quantum
        q_row = tk.Frame(left, bg=PANEL)
        q_row.pack(fill="x", padx=16, pady=4)
        tk.Label(q_row, text="Quantum:", font=("Courier", 9),
                 fg=SUBTEXT, bg=PANEL).pack(side="left")
        self.quantum_var = tk.IntVar(value=2)
        tk.Spinbox(q_row, from_=1, to=20, textvariable=self.quantum_var,
                   width=4, font=("Courier", 10), bg=BORDER, fg=TEXT,
                   buttonbackground=BORDER, relief="flat").pack(side="left", padx=6)

        self._btn(left, "▶  RUN SIMULATION", self._run_simulation, ACCENT,
                  bold=True).pack(pady=12, ipadx=6, ipady=4)

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Gantt chart canvas
        tk.Label(right, text="GANTT CHART", font=("Courier", 10, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w")

        self.gantt_canvas = tk.Canvas(right, bg=PANEL, height=120,
                                      highlightthickness=1,
                                      highlightbackground=BORDER)
        self.gantt_canvas.pack(fill="x", pady=(4, 10))

        # Stats
        stats_lbl = tk.Label(right, text="PERFORMANCE METRICS",
                             font=("Courier", 10, "bold"), fg=ACCENT, bg=BG)
        stats_lbl.pack(anchor="w")

        self.stats_frame = tk.Frame(right, bg=PANEL, highlightthickness=1,
                                    highlightbackground=BORDER)
        self.stats_frame.pack(fill="x", pady=(4, 10), ipadx=6, ipady=6)
        tk.Label(self.stats_frame, text="Run a simulation to see metrics.",
                 font=("Courier", 9), fg=SUBTEXT, bg=PANEL).pack()

        # Detail table
        tk.Label(right, text="PROCESS DETAILS",
                 font=("Courier", 10, "bold"), fg=ACCENT, bg=BG).pack(anchor="w")

        cols2 = ("PID", "Arrival", "Burst", "Start", "Finish", "Waiting", "Turnaround")
        self.detail_tree = ttk.Treeview(right, columns=cols2, show="headings",
                                        height=7)
        for c in cols2:
            self.detail_tree.heading(c, text=c)
            self.detail_tree.column(c, width=95, anchor="center")
        self.detail_tree.pack(fill="x", pady=4)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _btn(self, parent, text, cmd, color, bold=False):
        font = ("Courier", 9, "bold") if bold else ("Courier", 9)
        b = tk.Button(parent, text=text, command=cmd, font=font,
                      fg=color, bg=PANEL, activebackground=BORDER,
                      activeforeground=color, relief="flat",
                      cursor="hand2", bd=0,
                      highlightthickness=1, highlightbackground=color)
        return b

    def _add_process(self):
        try:
            arr   = int(self.entries["Arrival"].get())
            burst = int(self.entries["Burst"].get())
            pri   = int(self.entries["Priority"].get())
            assert burst > 0
        except:
            messagebox.showerror("Input Error", "Arrival ≥ 0, Burst > 0, Priority ≥ 1")
            return
        p = Process(self.pid_counter, arr, burst, pri)
        self.processes.append(p)
        self.tree.insert("", "end",
                         values=(f"P{self.pid_counter}", arr, burst, pri),
                         tags=(str(self.pid_counter),))
        self.pid_counter += 1

    def _remove_process(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        self.tree.delete(sel[0])
        self.processes.pop(idx)

    def _clear_processes(self):
        self.processes.clear()
        self.pid_counter = 0
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _random_processes(self):
        self._clear_processes()
        n = random.randint(4, 7)
        for i in range(n):
            arr   = random.randint(0, 8)
            burst = random.randint(1, 10)
            pri   = random.randint(1, 5)
            p = Process(self.pid_counter, arr, burst, pri)
            self.processes.append(p)
            self.tree.insert("", "end",
                             values=(f"P{self.pid_counter}", arr, burst, pri))
            self.pid_counter += 1

    # ── Simulation ─────────────────────────────────────────────────────────

    def _run_simulation(self):
        if not self.processes:
            messagebox.showwarning("No Processes", "Add at least one process.")
            return

        algo = self.algo_var.get()
        if algo == "FCFS":
            timeline, done = run_fcfs(self.processes)
        elif algo == "SJF":
            timeline, done = run_sjf(self.processes)
        elif algo == "RR":
            q = self.quantum_var.get()
            timeline, done = run_round_robin(self.processes, q)
        else:
            timeline, done = run_priority(self.processes)

        self._draw_gantt(timeline)
        self._show_stats(done, algo)
        self._show_details(done)

    def _draw_gantt(self, timeline):
        c = self.gantt_canvas
        c.delete("all")
        if not timeline:
            return

        c.update_idletasks()
        W = c.winfo_width() or 700
        H = 120
        pad_x, bar_y, bar_h = 40, 30, 50

        total_time = timeline[-1][2]
        if total_time == 0:
            return
        scale = (W - pad_x * 2) / total_time

        # Background grid
        for i in range(0, total_time + 1):
            x = pad_x + i * scale
            c.create_line(x, bar_y, x, bar_y + bar_h,
                          fill=BORDER, width=1)

        pid_colors = {}
        for p in self.processes:
            pid_colors[p.pid] = p.color

        for seg in timeline:
            pid, start, end = seg
            x1 = pad_x + start * scale
            x2 = pad_x + end * scale
            if pid == "idle":
                color, label = BORDER, "IDLE"
            else:
                color = pid_colors.get(pid, ACCENT)
                label = f"P{pid}"

            # Bar
            c.create_rectangle(x1, bar_y, x2, bar_y + bar_h,
                                fill=color, outline=BG, width=2)
            # Label inside bar
            mid_x = (x1 + x2) / 2
            if x2 - x1 > 14:
                c.create_text(mid_x, bar_y + bar_h / 2, text=label,
                              font=("Courier", 9, "bold"), fill=BG)

        # Time labels
        step = max(1, total_time // 10)
        for i in range(0, total_time + 1, step):
            x = pad_x + i * scale
            c.create_text(x, bar_y + bar_h + 12,
                          text=str(i), font=("Courier", 8), fill=SUBTEXT)

        # Legend
        seen = {}
        lx = pad_x
        for seg in timeline:
            pid = seg[0]
            if pid != "idle" and pid not in seen:
                seen[pid] = True
                color = pid_colors.get(pid, ACCENT)
                c.create_rectangle(lx, 8, lx + 12, 20,
                                   fill=color, outline="")
                c.create_text(lx + 20, 14, text=f"P{pid}",
                              font=("Courier", 8), fill=TEXT, anchor="w")
                lx += 46

    def _show_stats(self, done, algo):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        if not done:
            return

        avg_wt = sum(p.waiting_time for p in done) / len(done)
        avg_tat = sum(p.turnaround_time for p in done) / len(done)
        total_t = max(p.finish_time for p in done)
        cpu_busy = sum(p.burst for p in done)
        utilization = (cpu_busy / total_t * 100) if total_t else 0

        metrics = [
            ("Algorithm", algo, ACCENT),
            ("Avg Waiting Time", f"{avg_wt:.2f} units", YELLOW),
            ("Avg Turnaround", f"{avg_tat:.2f} units", GREEN),
            ("CPU Utilization", f"{utilization:.1f}%", ACCENT2),
            ("Throughput", f"{len(done)/total_t:.3f} proc/unit" if total_t else "N/A", RED),
        ]

        row = tk.Frame(self.stats_frame, bg=PANEL)
        row.pack(fill="x", padx=8, pady=4)
        for label, val, color in metrics:
            cell = tk.Frame(row, bg=BORDER, padx=8, pady=4)
            cell.pack(side="left", padx=4, pady=2)
            tk.Label(cell, text=label, font=("Courier", 8),
                     fg=SUBTEXT, bg=BORDER).pack()
            tk.Label(cell, text=val, font=("Courier", 10, "bold"),
                     fg=color, bg=BORDER).pack()

    def _show_details(self, done):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        for p in sorted(done, key=lambda x: x.pid):
            self.detail_tree.insert("", "end", values=(
                f"P{p.pid}",
                p.arrival,
                p.burst,
                p.start_time if p.start_time is not None else "-",
                p.finish_time if p.finish_time is not None else "-",
                p.waiting_time,
                p.turnaround_time
            ))
