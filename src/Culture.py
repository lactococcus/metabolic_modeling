import Species
import Medium

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
        return len(self.species_list)

    def update_biomass(self):
        medium_partition = self.medium
        if self.species_count() > 1:
            medium_partition = self.medium.partition(self.species_count())

        for species in self.species_list:

            solution = self.species[species.name].optimize(medium_partition)
            self.medium.update_medium(solution.fluxes)
            #self.medium.print_content()



