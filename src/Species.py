import cobra
from cobra.exceptions import OptimizationError
import Medium

class Species:
    def __init__(self, name, model_file_path, dry_weight):
        self.name = name
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'
        self.dry_weight = dry_weight

        for reaction in self.model.exchanges:
            reaction.upper_bound = 1000.0
            reaction.lower_bound = 0.0

    def optimize(self, medium):

        for reaction in self.model.exchanges:

            if reaction.id in medium:
                reaction.lower_bound = max(-1 * medium.get_component(reaction.id) / self.dry_weight, -1000.0)

        try:
            solution = model.optimize(objective_sense='maximize', raise_error=True)
        except OptimizationError:
            print("Model infeasible")
            return

        return solution


