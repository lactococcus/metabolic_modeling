import cobra
from cobra.exceptions import OptimizationError
import Medium
import math
from cobra.flux_analysis import pfba

class Species:
    """class representing a bacterial species"""
    def __init__(self, name, model_file_path, radius_microm, dry_weight_pg=0.3):
        self.name = name
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'
        self.dry_weight = dry_weight_pg
        self.surface_area = 4 * math.pi * radius_microm ** 2
        self.volume = 4 / 3 * math.pi * radius_microm ** 3
        self.data_watcher = None

        for reaction in self.model.exchanges:
            reaction.bounds = (0.0, 1000.0)

    def optimize(self, medium, timestep, pfba):
        """does FBA for the bacterial species. sets bounds of exchange reactions based on medium"""
        if medium != None:
            for reaction in self.model.exchanges:
                if reaction.id in medium:
                    reaction.lower_bound = max(-1 * medium.get_component(reaction.id) / self.get_biomass(), -10.0)

        try:
            if pfba:
                solution = cobra.flux_analysis.pfba(self.model)
            else:
                solution = self.model.optimize(objective_sense='maximize', raise_error=True)
        except OptimizationError:
            print(self.name + " Model infeasible")
            return

        self.set_biomass(self.get_biomass() * solution.objective_value * timestep + self.get_biomass())

        for i in range(len(solution.fluxes.index)):
            name = solution.fluxes.index[i]
            if name[:3] == "EX_":
                solution.fluxes.iloc[i] *= (self.get_biomass() * timestep)

        return solution

    def get_growth_curve(self):
        return self.data_watcher.get_growth_curve(self.name)

    def set_data_watcher(self, data_watcher):
        self.data_watcher = data_watcher
        self.data_watcher.data["species"][self.name] = [None, []]  # [init_abundance, biomass]

    def set_biomass(self, biomass):
        self.data_watcher.set_abundance(self.name, biomass // self.get_dryweight())

    def set_abundance(self, abundance):
        self.data_watcher.set_abundance(self.name, abundance)

    def set_init_abundance(self, abundance):
        self.data_watcher.set_init_abundance(self.name, abundance)

    def get_init_abundance(self):
        return self.data_watcher.get_init_abundance(self.name)

    def get_abundance(self):
        return self.data_watcher.get_abundance(self.name)

    def get_biomass(self):
        return self.data_watcher.get_abundance(self.name) * self.get_dryweight()

    def get_dryweight(self):
        return self.dry_weight / 1000000000000

    def add_to_culture(self, culture):
        self.culture = culture
