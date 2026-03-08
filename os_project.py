import matplotlib.pyplot as plt
from collections import deque

# ---------------- INPUT ----------------
n = int(input("Enter number of processes: "))

processes = []
for i in range(n):
    at = int(input(f"Arrival Time of P{i}: "))
    bt = int(input(f"Burst Time of P{i}: "))
    pr = int(input(f"Priority of P{i}: "))
    processes.append([i, at, bt, pr])

time_quantum = int(input("Enter Time Quantum (RR): "))

# ---------------- UTILITY ----------------
def gantt_chart(schedule, title):
    fig, ax = plt.subplots()
    for p, start, end in schedule:
        ax.barh(1, end-start, left=start)
        ax.text((start+end)/2, 1, f"P{p}", ha='center', va='center')
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_yticks([])
    plt.show()

def calculate_avg(processes, completion):
    wt, tat = [], []
    for i in range(len(processes)):
        tat.append(completion[i] - processes[i][1])
        wt.append(tat[i] - processes[i][2])
    return sum(wt)/len(wt), sum(tat)/len(tat)

# ---------------- FCFS ----------------
def fcfs(processes):
    t = 0
    comp = [0]*len(processes)
    schedule = []

    for p in sorted(processes, key=lambda x: x[1]):
        if t < p[1]:
            t = p[1]
        start = t
        t += p[2]
        comp[p[0]] = t
        schedule.append((p[0], start, t))

    gantt_chart(schedule, "FCFS Gantt Chart")
    return calculate_avg(processes, comp)

# ---------------- SJF ----------------
def sjf(processes):
    t, done = 0, 0
    visited = [False]*len(processes)
    comp = [0]*len(processes)
    schedule = []

    while done < len(processes):
        ready = [p for p in processes if p[1] <= t and not visited[p[0]]]
        if ready:
            p = min(ready, key=lambda x: x[2])
            start = t
            t += p[2]
            comp[p[0]] = t
            visited[p[0]] = True
            done += 1
            schedule.append((p[0], start, t))
        else:
            t += 1

    gantt_chart(schedule, "SJF Gantt Chart")
    return calculate_avg(processes, comp)

# ---------------- SRTF ----------------
def srtf(processes):
    rem = {p[0]: p[2] for p in processes}
    t, done = 0, 0
    comp = [0]*len(processes)
    schedule = []
    last = None
    start = 0

    while done < len(processes):
        ready = [p for p in processes if p[1] <= t and rem[p[0]] > 0]
        if ready:
            p = min(ready, key=lambda x: rem[x[0]])
            if last != p[0]:
                if last is not None:
                    schedule.append((last, start, t))
                start = t
                last = p[0]

            rem[p[0]] -= 1
            t += 1

            if rem[p[0]] == 0:
                comp[p[0]] = t
                done += 1
        else:
            t += 1

    if last is not None:
        schedule.append((last, start, t))

    gantt_chart(schedule, "SRTF Gantt Chart")
    return calculate_avg(processes, comp)

# ---------------- PRIORITY ----------------
def priority_sched(processes):
    t, done = 0, 0
    visited = [False]*len(processes)
    comp = [0]*len(processes)
    schedule = []

    while done < len(processes):
        ready = [p for p in processes if p[1] <= t and not visited[p[0]]]
        if ready:
            p = min(ready, key=lambda x: x[3])
            start = t
            t += p[2]
            comp[p[0]] = t
            visited[p[0]] = True
            done += 1
            schedule.append((p[0], start, t))
        else:
            t += 1

    gantt_chart(schedule, "Priority Scheduling Gantt Chart")
    return calculate_avg(processes, comp)

# ---------------- ROUND ROBIN ----------------
def round_robin(processes, tq):
    t = 0
    q = deque()
    rem = {p[0]: p[2] for p in processes}
    comp = [0]*len(processes)
    arrived = [False]*len(processes)
    schedule = []

    while True:
        for p in processes:
            if p[1] <= t and not arrived[p[0]]:
                q.append(p)
                arrived[p[0]] = True

        if q:
            p = q.popleft()
            start = t
            exec_time = min(tq, rem[p[0]])
            t += exec_time
            rem[p[0]] -= exec_time
            schedule.append((p[0], start, t))

            for pr in processes:
                if pr[1] <= t and not arrived[pr[0]]:
                    q.append(pr)
                    arrived[pr[0]] = True

            if rem[p[0]] > 0:
                q.append(p)
            else:
                comp[p[0]] = t
        else:
            if all(arrived):
                break
            t += 1

    gantt_chart(schedule, "Round Robin Gantt Chart")
    return calculate_avg(processes, comp)

# ---------------- RUN ALL ----------------
algos = ["FCFS", "SJF", "SRTF", "PRIORITY", "ROUND ROBIN"]
avg_wt, avg_tat = [], []

avg_wt.append(fcfs(processes)[0])
avg_tat.append(fcfs(processes)[1])

avg_wt.append(sjf(processes)[0])
avg_tat.append(sjf(processes)[1])

avg_wt.append(srtf(processes)[0])
avg_tat.append(srtf(processes)[1])

avg_wt.append(priority_sched(processes)[0])
avg_tat.append(priority_sched(processes)[1])

avg_wt.append(round_robin(processes, time_quantum)[0])
avg_tat.append(round_robin(processes, time_quantum)[1])

# ---------------- COMPARISON GRAPHS ----------------
plt.figure()
plt.bar(algos, avg_wt)
plt.title("Average Waiting Time Comparison")
plt.ylabel("Time")
plt.show()

plt.figure()
plt.bar(algos, avg_tat)
plt.title("Average Turnaround Time Comparison")
plt.ylabel("Time")
plt.show()

best = algos[avg_tat.index(min(avg_tat))]
print("\nBest Scheduling Algorithm:", best)
