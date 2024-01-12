from pyomo.environ import ConcreteModel, Var, Objective, Constraint, NonNegativeReals, Binary, maximize, RangeSet, sum_product
from pyomo.environ import SolverFactory

def solve_task_scheduling(tasks, durations, rewards, prereqs, forbidden_periods):
    # Create a model
    model = ConcreteModel()

    # Sets for tasks
    model.tasks = RangeSet(len(tasks))

    # Variables
    model.x = Var(model.tasks, domain=Binary)  # Whether a task is selected
    model.start_time = Var(model.tasks, domain=NonNegativeReals)  # Start time of each task

    # Constraints
    def time_constraint_rule(model, t):
        return model.start_time[t] + durations[t] * model.x[t] <= 24
    model.time_constraint = Constraint(model.tasks, rule=time_constraint_rule)

    def prereq_constraint_rule(model, t):
        if prereqs[t]:
            return max(model.start_time[p] + durations[p] for p in prereqs[t]) <= model.start_time[t]
        else:
            return Constraint.Skip
    model.prereq_constraint = Constraint(model.tasks, rule=prereq_constraint_rule)

    # def forbidden_period_rule(model, t):
    #     for start, end in forbidden_periods:
    #         if start <= model.start_time[t] < end or start < model.start_time[t] + durations[t] <= end:
    #             return False
    #     return True
    # model.forbidden_period_constraint = Constraint(model.tasks, rule=forbidden_period_rule)

    # Objective
    model.total_reward = Objective(expr=sum_product(rewards, model.x), sense=maximize)

    # Solve
    solver = SolverFactory('cbc')
    solver.solve(model)

    # Extract solution
    solution = []
    for t in model.tasks:
        if model.x[t]() == 1:
            solution.append({'Task': tasks[t-1], 'Start Time': model.start_time[t]()})

    return solution

# Example data (you will replace this with your actual data)
tasks = ['Task1', 'Task2', 'Task3']
durations = {1: 5, 2: 3, 3: 8}  # in hours
rewards = {1: 10, 2: 15, 3: 20}
prereqs = {1: [], 2: [1], 3: []}
forbidden_periods = [(6, 8), (12, 14)]  # times when tasks cannot start or end

# Solve the problem
solution = solve_task_scheduling(tasks, durations, rewards, prereqs, forbidden_periods)
print(solution)
