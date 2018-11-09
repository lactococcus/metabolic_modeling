import Species
import Medium
from random import shuffle

class Culture:

    def __init__(self, medium=None):
        self.species = {}
        self.species_list = []
        self.medium = medium

    def innoculate_species(self, species, biomass):
        species.set_biomass(biomass)
        self.species[species.name] = species
        self.species_list.append(species)

    def get_biomass_of_species(self, species):

        if species.name in self.species:
            return self.species[species.name].get_biomass()
        else:
            return 0.0

    def species_count(self):
        return len(self.species)

    def update_biomass(self):

        shuffle(self.species_list)

        for species in self.species_list:

            solution = self.species[species.name].optimize(self.medium)
            self.medium.update_medium(solution.fluxes)
            #self.medium.print_content()



