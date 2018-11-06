import cobra
from cobra.exceptions import OptimizationError
import Medium

class Species:
    def __init__(self, name, model_file_path, dry_weight_pg=0.28):
        self.name = name
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'
        self.dry_weight = dry_weight_pg / 1000000000

        for reaction in self.model.exchanges:
            reaction.upper_bound = 1000.0
            reaction.lower_bound = 0.0

    def optimize(self, medium):

        if medium != None:
            for reaction in self.model.exchanges:
                if reaction.id in medium:
                    reaction.lower_bound = max(-1 * medium.get_component(reaction.id) / self.dry_weight, -10.0)

        try:
            solution = self.model.optimize(objective_sense='maximize', raise_error=True)
        except OptimizationError:
            print(self.name + " Model infeasible")
            return

        #print(self.model.summary())

        for i in range(len(solution.fluxes.index)):
            name = solution.fluxes.index[i]
            if name[:3] == "EX_":
                solution.fluxes.iloc[i] *= self.dry_weight

        return solution


