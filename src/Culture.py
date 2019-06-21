import Species
from Medium import Medium
import threading
from decimal import *

class Culture:
    """class representing a bacterial culture. a culture consists of 1 medium and n different bacterial species"""
    def __init__(self, medium=None):
        self.species = {}
        self.species_list = []
        self.medium = medium
        self.rations = {}
        self.data_watcher = None

    def allocate_medium(self):
        """partitions the available resources of the medium based on the volume each bacterial species occupies in the medium"""
        ratios = [0 for species in self.species_list]

        total_volume = self.medium.volume * 10**15
        used_volume = 0

        for species in self.species_list:
            #print(species.name, species.data_watcher, species.get_abundance())
            used_volume += species.volume * species.get_abundance()

        if total_volume <= used_volume:
            for component in self.medium.components:
                self.rations[component] = [0 for x in ratios]

        else:
            for i in range(len(ratios)):
                spec = self.species_list[i]
                ratios[i] = 100 * Decimal(spec.get_abundance()) * Decimal(spec.volume) / Decimal(total_volume)

            for component in self.medium.components:
                self.rations[component] = [Decimal(self.medium.components[component]) * x for x in ratios]
                #print(self.rations[component])

    def innoculate_species(self, species, abundance):
        """adds a species to the culture"""
        species.set_data_watcher(self.data_watcher)
        species.set_abundance(abundance)
        species.set_init_abundance(abundance)
        self.species[species.name] = species
        self.species_list.append(species)

    def get_biomass_of_species(self, species):
        if species.name in self.species:
            return self.species[species.name].get_biomass()
        else:
            return 0.0

    def get_abundance_of_species(self, species):
        if species.name in self.species:
            return self.species[species.name].get_abundance()
        else:
            return 0

    def species_count(self):
        """returns the number of different bacterial species in the culture"""
        return len(self.species_list)

    def update_biomass(self, timestep):
        """optimizes the biomass production of all species in the culture using FBA"""
        self.allocate_medium()

        solutions = []

        if len(self.species_list) >= 2:

            threads = [threading.Thread(target=self._update_biomass, args=(i, species, solutions, timestep)) for i, species in
                         enumerate(self.species_list)]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

        else:
            components = {}
            for i, species in enumerate(self.species_list):
                for component in self.rations:
                    components[component] = self.rations[component][i]
                solution = self.species[species.name].optimize(Medium.from_dict(components, self.medium.volume), timestep)
                solutions.append(solution)

        counter = 0
        if len(solutions) != len(self.species_list):
            print("Not all Species have a Solution in FBA")
            return False
        for solution in solutions:
            self.medium.update_medium(solution.fluxes)
            if solution.objective_value < 0.001:
                counter += 1
            del solution

        if counter == len(self.species_list):
            return False
        else:
            return True

    def _update_biomass(self, i, species, list, timestep):

        components = {}

        for component in self.rations:
            components[component] = self.rations[component][i]

        solution = self.species[species.name].optimize(Medium.from_dict(components, self.medium.volume), timestep)
        if solution != None:
            list.append(solution)

    def set_medium(self, medium):
        self.medium = medium

    def register_data_watcher(self, data_watcher):
        self.data_watcher = data_watcher
        for species in self.species_list:
            species.data_watcher = data_watcher

    def copy(self):
        culture = Culture()
        culture.species = self.species
        culture.species_list = self.species_list
        culture.data_watcher = self.data_watcher
        culture.medium = self.medium
        return culture

    def __len__(self):
        return len(self.species_list)

    def __del__(self):
        del self.medium
        del self.rations
        self.species_list = None
        self.species = None
        #print("Destroyed Culture")




