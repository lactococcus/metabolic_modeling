from Culture import *


class Individual:
    def __init__(self, culture, chromosome, objective, medium_volume, simulation_time=24, timestep=1):
        self.culture = culture
        self.chromosome = chromosome
        self.objective = objective
        self.simulation_time = simulation_time
        self.timestep = timestep
        self.fitness = None
        self.medium_volume = medium_volume

    def score_fitness(self):
        abundance = {}
        init_abundance = {}
        total_abundance = 0
        self.culture.set_medium(self.chromosome.to_medium(self.medium_volume))

        for spec in self.culture.species_list:
            init_abundance[spec.name] = spec.init_abundance

        for i in range(self.simulation_time):
            if not self.culture.update_biomass():
                break

        for spec in self.culture.species_list:
            abundance[spec.name] = spec.get_abundance()
            total_abundance += spec.get_abundance()
            spec.set_abundance(spec.init_abundance)

        rel_abundance = {}

        for key in abundance:
            rel_abundance[key] = round(abundance[key] / total_abundance, 6)
            #print(key + ": " + str(rel_abundance[key]))

        self.fitness = self.fitness_function(init_abundance, abundance, rel_abundance)

    def fitness_function(self, init_abundance, abundance, rel_abundance):
        fitness = 0.0

        for key in self.objective:
            #print("Name: " + key + " Init: " + str(init_abundance[key]) + " Now: " + str(abundance[key]))
            if abundance[key] > init_abundance[key]:
                fitness += abs(self.objective[key] - rel_abundance[key])
                #print("Name: " + key + " Init: " + str(init_abundance[key]) + " Now: " + str(abundance[key]))
            else:
                fitness = -1.0
                break

        return round(fitness, 6)

    def get_fitness(self):
        if self.fitness == None:
            self.score_fitness

        return self.fitness

    def __lt__(self, other):
        """an indicidual is lesser than another when its fitness score is higher. higher fitness == bad"""
        return self.get_fitness() > other.get_fitness()
