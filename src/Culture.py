import Species
from Medium import Medium
import threading

'''class representing a bacterial culture. a culture consists of 1 medium and n different bacterial species'''
class Culture:

    def __init__(self, medium=None):
        self.species = {}
        self.species_list = []
        self.medium = medium
        self.rations = {}

    '''partitions the available resources of the medium based on co-culture composition'''

    def allocate_medium(self):
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

    '''adds a species to the culture'''

    def innoculate_species(self, species, abundance):
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

    '''returns the number of different bacterial species in the culture'''

    def species_count(self):
        return len(self.species_list)

    '''optimizes the biomass production of all species in the culture using FBA'''

    def update_biomass(self):

        self.allocate_medium()

        #for i, species in enumerate(self.species_list):
            #self._update_biomass(i, species)
        solutions = []

        threads = [threading.Thread(target=self._update_biomass, args=(i, species, solutions)) for i, species in
                     enumerate(self.species_list)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        for solutions in solutions:
            self.medium.update_medium(solutions.fluxes)


    def _update_biomass(self, i, species, list):

        components = {}

        for component in self.rations:
            components[component] = self.rations[component][i]

        solution = self.species[species.name].optimize(Medium.from_dict(components, self.medium.volume))
        list.append(solution)
        #self.medium.update_medium(solution.fluxes)
        # self.medium.print_content()

    def set_medium(self, medium):
        self.medium = medium
