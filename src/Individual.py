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
        total_abundance = 0
        for i in range(self.simulation_time):
            self.culture.update_biomass()
        else:
            for spec in self.culture.species_list:
                abundance[spec.name] = spec.get_abundance()
                total_abundance += spec.get_abundance()

        rel_abundance = {}

        for key in abundance:
            rel_abundance[key] = abundance[key] / total_abundance

        return self.fitness_function(rel_abundance)

    def fitness_function(self, rel_abundance):
        fitness = 0.0

        for key in self.objective:
            fitness += abs(self.objective[key] - rel_abundance[key]) + len(self.culture.medium.components)

        self.fitness = fitness

    def get_fitness(self):
        if self.fitness == None:
            self.score_fitness

        return self.fitness

    def __lt__(self, other):
        return self.get_fitness() > other.get_fitness()
