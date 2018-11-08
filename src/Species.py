import cobra
from cobra.exceptions import OptimizationError
import Medium
import math
import cplex

class Species:
    def __init__(self, name, model_file_path, radius_microm, dry_weight_pg=0.28):
        self.name = name
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'
        self.dry_weight = dry_weight_pg / 1000000000000
        self.surface_area = 4 * math.pi * radius_microm**2
        self.volume = 4/3 * math.pi * radius_microm**3
        self.last_solution = None

        for reaction in self.model.exchanges:
            reaction.upper_bound = 1000.0
            reaction.lower_bound = 0.0

    def optimize(self, medium):

        volume_factor = 150000 * self.volume / (medium.volume * 10**15)
        #print(volume_factor)

        if medium != None:
            for reaction in self.model.exchanges:
                if reaction.id in medium:
                    reaction.lower_bound = max(-1 * medium.get_component(reaction.id) * volume_factor / self.dry_weight, -1000.0)
                    #print(reaction.lower_bound)

        #if self.last_solution != None:
            #cplex.MIP_starts.add(self.last_solution)

        try:
            solution = self.model.optimize(objective_sense='maximize', raise_error=True)
        except OptimizationError:
            print(self.name + " Model infeasible")
            return

        self.last_solution = solution
        #print(self.model.summary())
        #print(solution.objective_value)

        for i in range(len(solution.fluxes.index)):
            name = solution.fluxes.index[i]
            if name[:3] == "EX_":
                solution.fluxes.iloc[i] *= self.dry_weight
        #print(solution.fluxes)
        return solution


