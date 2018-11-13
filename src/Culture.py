import Species
from Medium import Medium

class Culture:

    def __init__(self, medium=None):
        self.species = {}
        self.species_list = []
        self.medium = medium
        self.rations = {}

    def allocate_medium(self):
        ratios =[0 for species in self.species_list]

        total_biomass = 0
        for species in self.species_list:
            total_biomass += species.biomass

        for i in range(len(ratios)):
            ratios[i] = self.species_list[i].biomass / total_biomass

        for component in self.medium.components:
            self.rations[component] = [self.medium.components[component] / x for x in ratios]


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

    def species_count(self):
        return len(self.species_list)

    def update_biomass(self):

        self.allocate_medium()

        for i, species in enumerate(self.species_list):

            components = {}

            for component in self.rations:
                components[component] = self.rations[component][i]

            solution = self.species[species.name].optimize(Medium.from_dict(components, self.medium.volume))
            self.medium.update_medium(solution.fluxes)
            #self.medium.print_content()



