from Culture import *


class Individual:
    def __init__(self, culture, chromosome, objective, medium_volume, simulation_time=24, timestep=1):
        self.culture = culture
        self.chromosome = chromosome
        self.objective = objective
        self.simulation_time = simulation_time
        self.timestep = timestep
        self.fitness = None

        self.culture.set_medium(self.chromosome.to_medium(medium_volume))

    def score_fitness(self):
        abundance = {}
        init_abundance = {}
        total_abundance = 0

        for spec in self.culture.species_list:
            init_abundance[spec.name] = spec.get_abundance()

        for i in range(self.simulation_time):
            if not self.culture.update_biomass():
                break

        for spec in self.culture.species_list:
            abundance[spec.name] = spec.get_abundance()
            total_abundance += spec.get_abundance()
            spec.set_abundance(init_abundance[spec.name])

        rel_abundance = {}

        for key in abundance:
            rel_abundance[key] = abundance[key] / total_abundance

        self.fitness = self.fitness_function(init_abundance, abundance, rel_abundance)

    def fitness_function(self, init_abundance, abundance, rel_abundance):
        fitness = 0.0

        for key in self.objective:
            fitness += abs(self.objective[key] - rel_abundance[key]) * 100
            #print("Init: " + str(init_abundance[key]) + " Now: " + str(abundance[key]))
            if abundance[key] <= init_abundance[key]:
                fitness += 1000
        fitness += 2 * len(self.culture.medium)
        # print(len(self.culture.medium))

        return fitness

    def get_fitness(self):
        if self.fitness == None:
            self.score_fitness

        return self.fitness

    def __lt__(self, other):
        return self.get_fitness() > other.get_fitness()
