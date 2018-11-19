import cobra
from cobra.exceptions import OptimizationError
import Medium
import math
import cplex
import optlang.cplex_interface

'''class representing a bacterial species'''
class Species:
    def __init__(self, name, model_file_path, radius_microm, dry_weight_pg=0.28):
        self.name = name
        self.model = cobra.io.read_sbml_model(model_file_path)
        self.model.solver = 'cplex'
        self.dry_weight = dry_weight_pg / 1000000000000
        self.surface_area = 4 * math.pi * radius_microm**2
        self.volume = 4/3 * math.pi * radius_microm**3
        self.last_solution = None
        self.biomass = 0.0
        self.abundance = 0.0

        for reaction in self.model.exchanges:
            reaction.upper_bound = 1000.0
            reaction.lower_bound = 0.0

    '''does FBA for the bacterial species. sets bounds of exchange reactions based on medium'''
    def optimize(self, medium):

        if medium != None:
            for reaction in self.model.exchanges:
                if reaction.id in medium:
                    reaction.lower_bound = max(-1 * medium.get_component(reaction.id) * self.abundance / self.dry_weight, -1000.0)
                    #print(reaction.lower_bound)

        #self.add_warmstart()

        try:
            solution = self.model.optimize(objective_sense='maximize', raise_error=True)
        except OptimizationError:
            print(self.name + " Model infeasible")
            return

        self.last_solution = solution
        self.set_biomass(self.biomass * solution.objective_value + self.biomass)
        #print(self.model.summary())
        #print(solution.objective_value)

        for i in range(len(solution.fluxes.index)):
            name = solution.fluxes.index[i]
            if name[:3] == "EX_":
                solution.fluxes.iloc[i] *= self.dry_weight * self.biomass
        #print(solution.fluxes)
        return solution

    def set_biomass(self,biomass):
        self.biomass = biomass
        self.abundance = biomass // self.dry_weight

    def set_abundance(self, abundance):
        self.abundance = abundance
        self.biomass = abundance * self.dry_weight

    def get_abundance(self):
        return self.abundance

    def get_biomass(self):
        return self.biomass

    def add_to_culture(self, culture):
        self.culture = culture

    '''adds the last solution as a warmstart for cplex solver (does not work rn)'''
    def add_warmstart(self):
        cpx = self.model.solver.problem

        if self.last_solution != None:
            fluxes = self.last_solution.fluxes
            ind = []
            val = []
            for i in range(len(fluxes.index)):
                ind.append(fluxes.index[i])
                val.append(fluxes.iloc[i])

            sol = [ind, val]

            if cpx.MIP_starts.get_num() > 0:
                if self.name in cpx.MIP_starts.get_names():
                    cpx.MIP_starts.change(self.name, sol, cpx.MIP_starts.effort_level.auto)
                    return

            cpx.MIP_starts.add(sol, cpx.MIP_starts.effort_level.auto, self.name)
            print("Test")
