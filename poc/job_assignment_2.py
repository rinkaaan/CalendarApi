# Source
# https://www.udemy.com/course/optimization-with-python-linear-nonlinear-and-cplex-gurobi/learn/lecture/28372334#overview

import pyomo.environ as pyo
from pyomo.opt import SolverFactory

if __name__ == "__main__":
    m = pyo.ConcreteModel()

    # sets
    m.setJ = pyo.Set(initialize=["A", "B", "C", "D", "E", "F"])
    m.setD = pyo.Set(initialize=[1, 2, 3])
    m.D = {"A": 2, "B": 3, "C": 5, "D": 2, "E": 6, "F": 4}
    m.P = {"A": 200, "B": 500, "C": 300, "D": 100, "E": 1000, "F": 300}
    m.maxHours = 6

    # Example: Task dependencies
    m.preReq = {"A": [], "B": ["A"], "C": ["B", "E"], "D": [], "E": [], "F": ["D"]}

    # Unavailable hour ranges for each day
    m.unavailableHours = {1: (2, 4), 2: (), 3: (1, 3)}

    # variables
    m.x = pyo.Var(m.setJ, m.setD, within=pyo.Binary)
    m.startTime = pyo.Var(m.setJ, m.setD, within=pyo.NonNegativeReals)
    m.endTime = pyo.Var(m.setJ, m.setD, within=pyo.NonNegativeReals)

    # objective function
    m.obj = pyo.Objective(expr=sum(m.x[j, d] * m.P[j] for j in m.setJ for d in m.setD), sense=pyo.maximize)

    # constraints
    m.C1 = pyo.ConstraintList()
    m.C2 = pyo.ConstraintList()
    m.C3 = pyo.ConstraintList()
    m.C4 = pyo.ConstraintList()
    m.C5 = pyo.ConstraintList()

    # Time and overlap constraints
    for d in m.setD:
        for j in m.setJ:
            m.C4.add(m.startTime[j, d] + m.D[j] * m.x[j, d] <= m.endTime[j, d])
            m.C4.add(m.endTime[j, d] <= m.maxHours)

        if m.unavailableHours[d]:
            start, end = m.unavailableHours[d]
            for j in m.setJ:
                m.C5.add((m.startTime[j, d] + m.D[j]) * m.x[j, d] <= start or m.startTime[j, d] * m.x[j, d] >= end)

    for j1 in m.setJ:
        for j2 in m.setJ:
            if j1 != j2:
                for d in m.setD:
                    m.C5.add(m.endTime[j1, d] <= m.startTime[j2, d] or m.endTime[j2, d] <= m.startTime[j1, d])

    # Existing constraints
    for d in m.setD:
        m.C1.add(sum(m.x[j, d] * m.D[j] for j in m.setJ) <= m.maxHours)

    for j in m.setJ:
        m.C2.add(sum(m.x[j, d] for d in m.setD) <= 1)

    for j in m.setJ:
        for pre in m.preReq[j]:
            for d in m.setD:
                m.C3.add(sum(m.x[pre, dp] for dp in m.setD if dp < d) >= m.x[j, d])

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
                print("Job %s in day %d (duration %i, profit %i, start %i, end %i)" %
                      (j, d, m.D[j], m.P[j], pyo.value(m.startTime[j, d]), pyo.value(m.endTime[j, d])))
