# Source
# https://www.udemy.com/course/optimization-with-python-linear-nonlinear-and-cplex-gurobi/learn/lecture/28372334#overview

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

if __name__ == "__main__":
    m = pyo.ConcreteModel()

    # Sets
    m.setJ = pyo.Set(initialize=["A", "B", "C", "D", "E", "F"])
    m.setD = pyo.Set(initialize=[1, 2, 3])
    m.setB = pyo.Set(initialize=[0, 1])  # Set for auxiliary variables

    # Parameters
    m.D = {"A": 2, "B": 3, "C": 5, "D": 2, "E": 6, "F": 4}
    m.P = {"A": 200, "B": 500, "C": 300, "D": 100, "E": 1000, "F": 300}
    m.maxHours = 6
    m.unavailable = {1: (0, 0), 2: (3, 5), 3: (6, 8)}  # Unavailable time ranges

    # Variables
    m.x = pyo.Var(m.setJ, m.setD, within=pyo.Binary)
    m.start_time = pyo.Var(m.setJ, m.setD, within=pyo.NonNegativeReals)
    m.end_time = pyo.Var(m.setJ, m.setD, within=pyo.NonNegativeReals)
    m.y = pyo.Var(m.setJ, m.setD, m.setB, within=pyo.Binary)  # Auxiliary variables

    # Objective Function
    m.obj = pyo.Objective(expr=sum([m.x[j, d] * m.P[j] for j in m.setJ for d in m.setD]), sense=pyo.maximize)

    # Constraints
    m.C1 = pyo.ConstraintList()
    m.C2 = pyo.ConstraintList()
    m.C3 = pyo.ConstraintList()

    # Big-M
    M = 24

    for d in m.setD:
        m.C1.add(sum([m.x[j, d] * m.D[j] for j in m.setJ]) <= m.maxHours)
        for j in m.setJ:
            m.C3.add(m.start_time[j, d] + m.D[j] * m.x[j, d] <= m.end_time[j, d])
            m.C3.add(m.end_time[j, d] <= 24 * m.x[j, d])
            m.C3.add(m.start_time[j, d] >= m.unavailable[d][1] - M * (1 - m.y[j, d, 1]))
            m.C3.add(m.end_time[j, d] <= m.unavailable[d][0] + M * m.y[j, d, 0])

    for j in m.setJ:
        m.C2.add(sum([m.x[j, d] for d in m.setD]) <= 1)

    # Solve
    opt = SolverFactory("cbc")
    m.results = opt.solve(m)

    # Print results
    m.pprint()

    print("\n\n")
    print("Profit Total:", pyo.value(m.obj))
    for d in m.setD:
        for j in m.setJ:
            if pyo.value(m.x[j, d]) > 0.9:
                print("Job %s in day %d (duration %i, profit %i, start %i, end %i)" % (
                    j, d, m.D[j], m.P[j], pyo.value(m.start_time[j, d]), pyo.value(m.end_time[j, d])))
