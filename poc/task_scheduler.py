from pyomo.environ import *
import pyomo.environ as pyo

# Example tasks data (task_id, duration, reward)
tasks_data = {
    1: {'duration': 4, 'reward': 10},
    2: {'duration': 3, 'reward': 15},
    3: {'duration': 5, 'reward': 7},
    4: {'duration': 7, 'reward': 7},
    5: {'duration': 3, 'reward': 20},
}

# Define the model
model = ConcreteModel()

# Set of tasks
model.tasks = Set(initialize=tasks_data.keys())

# Decision variables: whether to schedule each task
model.schedule = Var(model.tasks, within=pyo.Binary)

# Define available hours, excluding unavailable time ranges
# Available: 8 am to 10 am, 11 am to 12 pm, and 1 pm to 12 am
available_hours = list(range(8, 10)) + list(range(11, 12)) + list(range(13, 24))
model.time_slots = Set(initialize=available_hours)

# Decision variables: start time for each task
model.start_time = Var(model.tasks, within=model.time_slots, bounds=(8, 23))

# Objective: Maximize total reward
def obj_rule(model):
    return sum(model.schedule[t] * tasks_data[t]['reward'] for t in model.tasks)

model.objective = Objective(rule=obj_rule, sense=maximize)

# Constraint: No overlapping tasks
def no_overlap_rule(model, t1, t2):
    if t1 >= t2:
        return Constraint.Skip
    # Task t2 can't start if t1 is scheduled and it overlaps with t1's duration
    return model.start_time[t2] >= model.start_time[t1] + tasks_data[t1]['duration'] * model.schedule[t1]

model.no_overlap = Constraint(model.tasks, model.tasks, rule=no_overlap_rule)

# Constraint: Task must not finish after the end of the day (12 am)
def end_of_day_rule(model, t):
    return model.start_time[t] + tasks_data[t]['duration'] * model.schedule[t] <= 24

model.end_of_day = Constraint(model.tasks, rule=end_of_day_rule)

# Solve the model using the CBC solver
solver = SolverFactory('cbc')
solution = solver.solve(model, tee=True)

# Display results
for t in model.tasks:
    if model.schedule[t].value > 0:
        # print(f"Task {t}: Start at {model.start_time[t].value}, Duration {tasks_data[t]['duration']}, Reward {tasks_data[t]['reward']}")

        # Update message so that end time is also displayed
        print(f"Task {t}: Start at {model.start_time[t].value}, End at {model.start_time[t].value + tasks_data[t]['duration']}, Duration {tasks_data[t]['duration']}, Reward {tasks_data[t]['reward']}")

# Total reward
print("Total Reward:", model.objective())

