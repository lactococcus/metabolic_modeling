import Species
from Medium import Medium
import multiprocessing as mp

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

        total_biomass = 0
        for species in self.species_list:
            total_biomass += species.biomass

        for i in range(len(ratios)):
            ratios[i] = self.species_list[i].biomass / total_biomass

        for component in self.medium.components:
            self.rations[component] = [self.medium.components[component] / x for x in ratios]

    '''adds a species to the culture'''

    def innoculate_species(self, species, biomass):
        species.set_biomass(biomass)
        self.species[species.name] = species
        self.species_list.append(species)

    def get_biomass_of_species(self, species):
        if species.name in self.species:
            return self.species[species.name].get_biomass()
        else:
            return 0.0

    def get_abundance_of_species(self, species):
        if species.name in self.species:
            return self.species[species.name].get_biomass() // self.species[species.name].dry_weight
        else:
            return 0.0

    '''returns the number of different bacterial species in the culture'''

    def species_count(self):
        return len(self.species_list)

    '''optimizes the biomass production of all species in the culture using FBA'''

    def update_biomass(self):

        self.allocate_medium()

        for i, species in enumerate(self.species_list):
            self._update_biomass(i, species)

        '''
        processes = [mp.Process(target=self._update_biomass, args=(i, species)) for i, species in
                     enumerate(self.species_list)]

        for process in processes:
            process.start()

        for process in processes:
            process.join()
        '''

    def _update_biomass(self, i, species):

        components = {}

        for component in self.rations:
            components[component] = self.rations[component][i]

        solution = self.species[species.name].optimize(Medium.from_dict(components, self.medium.volume))
        self.medium.update_medium(solution.fluxes)
        # self.medium.print_content()
