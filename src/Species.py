import cobra
from cobra.exceptions import OptimizationError
import Medium
import math
from cobra.flux_analysis import pfba
from cobra.core.solution import get_solution

class Species:
    """class representing a bacterial species"""
    def __init__(self, name, model_file_path, radius_microm=0.2, dry_weight_pg=0.3):
        self.name = name
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'
        self.model.solver.solution_target = 'global'
        self.model.solver.lp_method = 'barrier'
        self.dry_weight = dry_weight_pg
        self.surface_area = 4 * math.pi * radius_microm ** 2
        self.volume = 4 / 3 * math.pi * radius_microm ** 3
        self.data_watcher = None

        for reaction in self.model.exchanges:
            reaction.bounds = (0.0, 1000.0)
        #print(f"Species {self.name} got created")

    def optimize(self, medium, timestep):
        """does FBA for the bacterial species. sets bounds of exchange reactions based on medium"""
        with self.model as model:
            if medium != None:
                for reaction in self.model.exchanges:
                    if reaction.id in medium:
                        tmp = -1 * round(medium.get_component(reaction.id) / self.get_biomass(), 3)
                        reaction.lower_bound = max(tmp, -1000)
                    else:
                        reaction.lower_bound = 0.0

            try:
                if self.data_watcher.get_pfba():
                    cobra.flux_analysis.parsimonious.add_pfba(model)

                objective_value = self.model.slim_optimize()
                solution = get_solution(self.model, reactions=self.model.exchanges)
            except OptimizationError:
                print(self.name + " Model infeasible")
                return

            self.set_biomass((self.get_biomass() * round(solution.objective_value, 6) * timestep + self.get_biomass()) * (1 - self.data_watcher.get_death_rate()))

            for i in range(len(solution.fluxes.index)):
                name = solution.fluxes.index[i]
                if name[:3] == "EX_":
                    solution.fluxes.iloc[i] = (round(solution.fluxes.iloc[i], 6) * self.get_biomass() * timestep)

            return solution

    def get_growth_curve(self):
        return self.data_watcher.get_growth_curve(self.name)

    def set_data_watcher(self, data_watcher):
        self.data_watcher = data_watcher
        self.data_watcher.data["species"][self.name] = [None, []]  # [init_abundance, biomass]


    def set_biomass(self, biomass):
        self.data_watcher.set_abundance(self.name, biomass * 1000000000000 // self.dry_weight)

    def set_abundance(self, abundance):
        self.data_watcher.set_abundance(self.name, abundance)

    def set_init_abundance(self, abundance):
        self.data_watcher.set_init_abundance(self.name, abundance)

    def get_init_abundance(self):
        return self.data_watcher.get_init_abundance(self.name)

    def get_abundance(self):
        return self.data_watcher.get_abundance(self.name)

    def get_biomass(self):
        """returns biomass in gram"""
        return self.data_watcher.get_abundance(self.name) * self.dry_weight / 1000000000000

    def get_dryweight(self):
        """returns dryweight in gram"""
        return self.dry_weight / 1000000000000

    def add_to_culture(self, culture):
        self.culture = culture

    def __del__(self):
        #print(f"Species {self.name} got destroyed")
        del self.model
        del self.name
        del self.volume
        del self.dry_weight
        del self.surface_area
        self.data_watcher = None
        self.culture = None

