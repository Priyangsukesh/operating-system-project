import streamlit as st
import matplotlib.pyplot as plt
from collections import deque

st.title("CPU Scheduling Simulator")

# -------- Gantt Chart --------
def gantt_chart(schedule, title):
    fig, ax = plt.subplots()
    for p, start, end in schedule:
        ax.barh(1, end-start, left=start)
        ax.text((start+end)/2, 1, f"P{p}", ha='center', va='center')
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_yticks([])
    return fig


# -------- Average Calculation --------
def calculate_avg(processes, completion):
    wt, tat = [], []
    for i in range(len(processes)):
        tat.append(completion[i] - processes[i][1])
        wt.append(tat[i] - processes[i][2])
    return sum(wt)/len(wt), sum(tat)/len(tat)


# -------- FCFS --------
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

    wt, tat = calculate_avg(processes, comp)
    return wt, tat, schedule


# -------- SJF --------
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

    wt, tat = calculate_avg(processes, comp)
    return wt, tat, schedule


# -------- ROUND ROBIN --------
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

    wt, tat = calculate_avg(processes, comp)
    return wt, tat, schedule


# -------- INPUT SECTION --------

st.header("Process Input")

n = st.number_input("Number of Processes", min_value=1, max_value=10, step=1)

processes = []

for i in range(n):
    col1, col2, col3 = st.columns(3)

    at = col1.number_input(f"P{i} Arrival Time", min_value=0, key=f"at{i}")
    bt = col2.number_input(f"P{i} Burst Time", min_value=1, key=f"bt{i}")
    pr = col3.number_input(f"P{i} Priority", min_value=1, key=f"pr{i}")

    processes.append([i, at, bt, pr])

time_quantum = st.number_input("Round Robin Time Quantum", min_value=1, step=1)

# -------- RUN SIMULATION --------

if st.button("Run Scheduling Algorithms"):

    avg_wt = []
    avg_tat = []
    algos = ["FCFS", "SJF", "ROUND ROBIN"]

    wt_fcfs, tat_fcfs, sch_fcfs = fcfs(processes)
    st.subheader("FCFS")
    st.pyplot(gantt_chart(sch_fcfs, "FCFS Gantt Chart"))
    avg_wt.append(wt_fcfs)
    avg_tat.append(tat_fcfs)

    wt_sjf, tat_sjf, sch_sjf = sjf(processes)
    st.subheader("SJF")
    st.pyplot(gantt_chart(sch_sjf, "SJF Gantt Chart"))
    avg_wt.append(wt_sjf)
    avg_tat.append(tat_sjf)

    wt_rr, tat_rr, sch_rr = round_robin(processes, time_quantum)
    st.subheader("Round Robin")
    st.pyplot(gantt_chart(sch_rr, "RR Gantt Chart"))
    avg_wt.append(wt_rr)
    avg_tat.append(tat_rr)

    # Comparison graphs
    fig1 = plt.figure()
    plt.bar(algos, avg_wt)
    plt.title("Average Waiting Time Comparison")
    st.pyplot(fig1)

    fig2 = plt.figure()
    plt.bar(algos, avg_tat)
    plt.title("Average Turnaround Time Comparison")
    st.pyplot(fig2)

    best = algos[avg_tat.index(min(avg_tat))]
    st.success(f"Best Scheduling Algorithm (based on TAT): {best}")
