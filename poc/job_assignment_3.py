# Source
# https://www.udemy.com/course/optimization-with-python-linear-nonlinear-and-cplex-gurobi/learn/lecture/28372334#overview

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

if __name__ == "__main__":
    m = pyo.ConcreteModel()

    # sets
    m.setJ = pyo.Set(initialize=["A", "B", "C", "D", "E", "F"])
    m.setD = pyo.Set(initialize=[1, 2, 3])
    m.D = {"A": 200, "B": 3, "C": 5, "D": 2, "E": 6, "F": 4}
    m.P = {"A": 200, "B": 500, "C": 300, "D": 100, "E": 1000, "F": 300}
    m.maxHours = 6

    # Example: Task dependencies (B depends on A, C depends on B and E, etc.)
    m.preReq = {"A": ["D"], "B": ["A"], "C": ["B", "E"], "D": [], "E": [], "F": ["D"]}

    # # New: Unavailable hour ranges for each day (e.g., (start hour, end hour))
    # m.unavailableHours = {1: (2, 4), 2: (), 3: (1, 3)}  # Format: day: (startHour, endHour)

    # variables
    m.x = pyo.Var(m.setJ, m.setD, within=pyo.Binary)

    # objective function
    m.obj = pyo.Objective(expr=sum([m.x[j, d] * m.P[j] for j in m.setJ for d in m.setD]), sense=pyo.maximize)

    # constraints
    # m.C1 = pyo.ConstraintList()
    m.C2 = pyo.ConstraintList()
    m.C3 = pyo.ConstraintList()
    m.C4 = pyo.ConstraintList()

    # for d in m.setD:
    #     if m.unavailableHours[d]:
    #         start, end = m.unavailableHours[d]
    #         m.C1.add(sum([m.x[j, d] * m.D[j] for j in m.setJ]) + (end - start) <= m.maxHours)
    #     else:
    #         m.C1.add(sum([m.x[j, d] * m.D[j] for j in m.setJ]) <= m.maxHours)

    for j in m.setJ:
        m.C2.add(sum([m.x[j, d] for d in m.setD]) <= 1)

    # Task dependency constraints
    for j in m.setJ:
        for pre in m.preReq[j]:
            for d in m.setD:
                m.C3.add(sum([m.x[pre, dp] for dp in m.setD if dp < d]) >= m.x[j, d])

    # solve
    opt = SolverFactory("cbc")
    m.results = opt.solve(m)

    # print
    m.pprint()

    print("\n\n")
    print("Profit Total:", pyo.value(m.obj))
    for d in m.setD:
        for j in m.setJ:
            if pyo.value(m.x[j, d]) > 0.9:
                print("Job %s in day %d (duration %i, profit %i)" % (j, d, m.D[j], m.P[j]))
