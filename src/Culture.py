import Species
import Medium

class Culture:

    def __init__(self, medium, species=None):
        self.species = species
        self.medium = medium

    def add_species(self, species):
        self.species.append(species)

    def species_count(self):
        return len(self.species)

    def update_biomass(self):

        for species in self.species:

            solution = species.optimize(self.medium)
            self.medium.update_medium(solution.fluxes)


