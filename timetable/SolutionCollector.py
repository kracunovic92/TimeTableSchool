from ortools.sat.python import cp_model


class SolutionCollector(cp_model.CpSolverSolutionCallback):
    
    def __init__(self,variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solutions = []
        self.variables = variables


    
    def OnSolutionCallback(self):
        solution = {var :self.Value(var) for var in self.variables if self.Value(var) == 1}
        self.solutions.append(solution)
        print('Solutin: ', solution)

    
    def print_solution(self):
        pass