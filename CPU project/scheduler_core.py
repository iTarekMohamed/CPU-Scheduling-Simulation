PROCESS_COLORS = [
    "#00e5ff", "#7b2fff", "#00ff9d", "#ffd166",
    "#ff4d6d", "#ff9f43", "#54a0ff", "#ee5a24",
    "#0abde3", "#10ac84"
]


class Process:
    def __init__(self, pid, arrival, burst, priority=1):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.color = PROCESS_COLORS[pid % len(PROCESS_COLORS)]


def run_fcfs(processes):
    procs = sorted([Process(p.pid, p.arrival, p.burst, p.priority) for p in processes],
                   key=lambda x: x.arrival) ## deep copy w sort by arrival 
    
    timeline, t = [], 0
    for p in procs:
        if t < p.arrival:
            timeline.append(("idle", t, p.arrival))
            t = p.arrival # lw eltime smaller mn arrival, n3ml idle l7d arrival
        p.start_time = t
        timeline.append((p.pid, t, t + p.burst))
        t += p.burst
        p.finish_time = t
        p.turnaround_time = p.finish_time - p.arrival
        p.waiting_time = p.turnaround_time - p.burst
    return timeline, procs


def run_sjf(processes):
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    timeline, t, done = [], 0, []
    remaining = procs[:]
    while remaining:
        available = [p for p in remaining if p.arrival <= t]
        if not available:
            next_t = min(p.arrival for p in remaining)
            timeline.append(("idle", t, next_t))
            t = next_t
            continue # lw mafeesh process available, n3ml idle l7d a5r arrival w eltime = a5r arrival 
        p = min(available, key=lambda x: x.burst)
        remaining.remove(p)
        p.start_time = t
        timeline.append((p.pid, t, t + p.burst))
        t += p.burst
        p.finish_time = t
        p.turnaround_time = p.finish_time - p.arrival 
        p.waiting_time = p.turnaround_time - p.burst ## calculating time metrics
        done.append(p)
    return timeline, done


def run_round_robin(processes, quantum):
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    procs.sort(key=lambda x: x.arrival)
    queue, timeline, t = [], [], 0
    remaining = procs[:]
    arrived = []
    i = 0
    # filling elqueue b processes elly arrived at time 0
    while i < len(remaining) and remaining[i].arrival <= t:
        queue.append(remaining[i])
        arrived.append(remaining[i])
        i += 1
    # # # # # # # # # # # # # # # # # # # # # 
    while queue or i < len(remaining): ## 48ala tool ma feeh processes fel queue aw mfee4 processes gayeen
        if not queue: # lw eltaboor fadi w feeh processes gayeen, n3ml jump l elremaining process elly a5r arrival w eltime = arrival
            t = remaining[i].arrival
            while i < len(remaining) and remaining[i].arrival <= t:
                if remaining[i] not in arrived:
                    queue.append(remaining[i])
                    arrived.append(remaining[i])
                i += 1
        if not queue:
            break
        p = queue.pop(0)
        run_for = min(quantum, p.remaining) ## eg burst 10 , q 3 , run 3 , run 3 , run 3 , run 1
        timeline.append((p.pid, t, t + run_for))
        t += run_for
        p.remaining -= run_for
        # adding processes that arrived during this quantum to the queue
        while i < len(remaining) and remaining[i].arrival <= t: 
            if remaining[i] not in arrived:
                queue.append(remaining[i])
                arrived.append(remaining[i])
            i += 1
        if p.remaining > 0:
            queue.append(p)
        else:
            p.finish_time = t
            p.turnaround_time = p.finish_time - p.arrival
            p.waiting_time = p.turnaround_time - p.burst
    done = [p for p in procs if p.finish_time is not None]
    return timeline, done


def run_priority(processes):
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    timeline, t, done = [], 0, []
    remaining = procs[:]
    while remaining:
        available = [p for p in remaining if p.arrival <= t]
        if not available:
            next_t = min(p.arrival for p in remaining)
            timeline.append(("idle", t, next_t))
            t = next_t
            continue
        p = min(available, key=lambda x: x.priority)
        remaining.remove(p)
        p.start_time = t
        timeline.append((p.pid, t, t + p.burst))
        t += p.burst
        p.finish_time = t
        p.turnaround_time = p.finish_time - p.arrival
        p.waiting_time = p.turnaround_time - p.burst
        done.append(p)
    return timeline, done
