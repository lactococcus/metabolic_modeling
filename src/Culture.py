import Species
from Medium import Medium
import threading

class Culture:
    """class representing a bacterial culture. a culture consists of 1 medium and n different bacterial species"""
    def __init__(self, medium=None):
        self.species = {}
        self.species_list = []
        self.medium = medium
        self.rations = {}

    def allocate_medium(self):
        """partitions the available resources of the medium based on the volume each bacterial species occupies in the medium"""
        ratios = [0 for species in self.species_list]

        total_volume = self.medium.volume * 10**15
        used_volume = 0

        for species in self.species_list:
            used_volume += species.volume * species.get_abundance()

        if total_volume <= used_volume:
            for component in self.medium.components:
                self.rations[component] = [0 for x in ratios]

        else:
            for i in range(len(ratios)):
                spec = self.species_list[i]
                ratios[i] = (spec.get_abundance() * spec.volume) / total_volume

            for component in self.medium.components:
                self.rations[component] = [self.medium.components[component] / x for x in ratios]

    def innoculate_species(self, species, abundance):
        """adds a species to the culture"""
        species.set_abundance(abundance)
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

    def update_biomass(self):
        """optimizes the biomass production of all species in the culture using FBA"""
        self.allocate_medium()

        solutions = []

        threads = [threading.Thread(target=self._update_biomass, args=(i, species, solutions)) for i, species in
                     enumerate(self.species_list)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        counter = 0
        for solution in solutions:
            self.medium.update_medium(solution.fluxes)
            if solution.objective_value < 0.0001:
                counter += 1

        if counter == len(self.species_list):
            return False
        else:
            return True

    def _update_biomass(self, i, species, list):

        components = {}

        for component in self.rations:
            components[component] = self.rations[component][i]

        solution = self.species[species.name].optimize(Medium.from_dict(components, self.medium.volume))
        list.append(solution)


    def set_medium(self, medium):
        self.medium = medium


