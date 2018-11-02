import cobra
from cobra.exceptions import OptimizationError
import Medium

class Species:
    def __init__(self, model_file_path):
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'

    def optimize(self, medium):

        for reaction in self.model.exchanges:
            reaction.upper_bound = 1000.0

            if reaction.id in medium:
                reaction.lower_bound = -1 * medium.get_component(reaction.id)

            else:
                reaction.lower_bound = 0.0

        try:
            solution = model.optimize(objective_sense='maximize', raise_error=True)
        except OptimizationError:
            print("Model infeasible")
            return

        return solution


