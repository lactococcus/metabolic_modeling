import cobra
from cobra.exceptions import OptimizationError
import Medium
import math
#from cobra.flux_analysis import pfba

class Species:
    """class representing a bacterial species"""
    def __init__(self, name, model_file_path, radius_microm, dry_weight_pg=0.3, init_abundance=0):
        self.name = name
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'
        self.dry_weight = dry_weight_pg / 1000000000000
        self.surface_area = 4 * math.pi * radius_microm ** 2
        self.volume = 4 / 3 * math.pi * radius_microm ** 3
        self.biomass = 0.0
        self.init_abundance = 0

        for reaction in self.model.exchanges:
            reaction.bounds = (0.0, 1000.0)

    def optimize(self, medium):
        """does FBA for the bacterial species. sets bounds of exchange reactions based on medium"""
        if medium != None:
            for reaction in self.model.exchanges:
                if reaction.id in medium:
                    reaction.lower_bound = max(-1 * medium.get_component(reaction.id) / self.get_biomass(), -10.0)

        try:
            solution = self.model.optimize(objective_sense='maximize', raise_error=True)
            #self.model.summary()
        except OptimizationError:
            print(self.name + " Model infeasible")
            return

        self.set_biomass(self.biomass * solution.objective_value + self.biomass)


        for i in range(len(solution.fluxes.index)):
            name = solution.fluxes.index[i]
            if name[:3] == "EX_":
                solution.fluxes.iloc[i] *= self.get_biomass()

        return solution


    def set_biomass(self, biomass):
        self.biomass = biomass


    def set_abundance(self, abundance):
        self.biomass = abundance * self.dry_weight


    def get_abundance(self):
        return self.biomass // self.dry_weight


    def get_biomass(self):
        return self.biomass


    def add_to_culture(self, culture):
        self.culture = culture
