import pyomo.environ as pyo
from pyomo.opt import SolverFactory

# Create the model
model = pyo.ConcreteModel()

# Define sets
model.T = pyo.Set(initialize=[1, 2, 3])  # Set of tasks
model.S = pyo.Set(initialize=range(24))  # Set of time periods
model.E = pyo.Set(initialize=[12, 13])  # Restricted time periods (example)

# Define parameters
model.r = pyo.Param(model.T, initialize={1: 10, 2: 15, 3: 20})  # Rewards
model.d = pyo.Param(model.T, initialize={1: 2, 2: 3, 3: 4})  # Durations
model.P = pyo.Param(model.T, initialize={2: [1], 3: [1]})  # Prerequisites

# Define variables
model.x = pyo.Var(model.T, model.S, within=pyo.Binary)  # Scheduling variables

# Define objective function
model.obj = pyo.Objective(expr=sum(model.r[i] * model.x[i, t] for i in model.T for t in model.S),
                          sense=pyo.maximize)

# Constraints:
# One task at a time: Only one task can be active at any given time period.
# sum(x_it) <= 1 for all t in S
# Task duration: Each task duration must be respected.
# sum(x_it - x_j(t+d_i-1)) >= 0 for all i, j in T and t in S, where j != i
# Prerequisite satisfaction: All prerequisite tasks must be completed before a task can start.
# x_it <= sum(x_jp) for all i in T and t in S, where j in P_i and p in S[t-d_j+1, t]
# Time horizon: The total duration of scheduled tasks cannot exceed the available time window.
# sum(d_i * sum(x_it)) <= 24 for all i in T and t in S
# Restricted time periods: No tasks can start or end in prohibited time periods.
# x_it = 0 for all i in T and t in E
# Binary variable definition: x_it must be binary (0 or 1).
# x_it in {0, 1} for all i in T and t in S


# Define constraints
def one_task_at_a_time(model, t):
    return sum(model.x[i, t] for i in model.T) <= 1


model.one_task_at_a_time = pyo.Constraint(model.S, rule=one_task_at_a_time)

def task_duration(model, i, t):
    return sum(model.x[i, t] - model.x[j, t + model.d[i] - 1] for j in model.T if j != i) >= 0

model.task_duration = pyo.Constraint(model.T, model.S, rule=task_duration)

# Solve the model
opt = SolverFactory('cbc')
results = opt.solve(model)

# Print results
print("Optimal solution:")
for i in model.T:
    for t in model.S:
        if model.x[i, t].value > 0.5:
            print(f"Task {i} starts at time period {t}")
print("Total reward:", model.obj())
