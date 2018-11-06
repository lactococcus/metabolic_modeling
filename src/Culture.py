import Species
import Medium

class Culture:

    def __init__(self, medium=None):
        self.species = {}
        self.medium = medium

    def innoculate_species(self, species, biomass):
        self.species[species.name] = (species, biomass)

    def get_biomass_of_species(self, species):

        if species.name in self.species:
            return self.species[species.name][1]
        else:
            return 0.0

    def species_count(self):
        return len(self.species)

    def update_biomass(self):

        for species in self.species:

            solution = self.species[species][0].optimize(self.medium)
            self.medium.update_medium(solution.fluxes)
            #self.medium.print_content()
            self.species[species] = (self.species[species][0], self.species[species][1] * solution.objective_value + self.species[species][1])


