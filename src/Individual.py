from Culture import *
from matplotlib import pyplot as plt
import math


class Individual:
    def __init__(self, culture, chromosome, objective, medium_volume, simulation_time=24, timestep=1):
        self.culture = culture
        self.chromosome = chromosome
        self.objective = objective
        self.simulation_time = simulation_time
        self.timestep = timestep
        self.fitness = None
        self.medium_volume = medium_volume
        self.fitness_medium = None

    def plot(self, medium=None):
        if medium == None:
            self.culture.set_medium(self.chromosome.to_medium(self.medium_volume))
        else:
            self.culture.set_medium(medium)
        #self.culture.medium.print_content()
        growth = {}

        for spec in self.culture.species_list:
            spec.set_abundance(spec.init_abundance)
            growth[spec.name] = [spec.get_abundance()]

        xAxis = [0]
        for i in range(math.floor(self.simulation_time / self.timestep)):
            xAxis.append(self.timestep * i + self.timestep)
            self.culture.update_biomass(self.timestep)
            for spec in self.culture.species_list:
                growth[spec.name].append(spec.get_abundance())

        for key in growth:
            plt.plot(xAxis, growth[key], label=key)
        #plt.xticks(xAxis)
        plt.legend()
        plt.show()

    def score_fitness(self, fitness_func, medium=None):
        abundance = {}
        init_abundance = {}
        total_abundance = 0
        if medium == None:
            self.culture.set_medium(self.chromosome.to_medium(self.medium_volume))
        else:
            self.culture.set_medium(medium)

        for spec in self.culture.species_list:
            init_abundance[spec.name] = spec.init_abundance
            spec.set_abundance(spec.init_abundance)

        for i in range(math.floor(self.simulation_time / self.timestep)):
            if not self.culture.update_biomass(self.timestep):
                break


        for spec in self.culture.species_list:
            abundance[spec.name] = spec.get_abundance()
            total_abundance += spec.get_abundance()

        rel_abundance = {}

        for key in abundance:
            rel_abundance[key] = round(abundance[key] / total_abundance, 6)
            #print(key + ": " + str(rel_abundance[key]))

        fitness_func(init_abundance, abundance, rel_abundance)

    def fitness_medium_function(self, init_abundance, abundance, rel_abundance):
        fitness = 0.0
        for key in self.objective:
            #print("Name: " + key + " Init: " + str(init_abundance[key]) + " Now: " + str(abundance[key]))
            if abundance[key] > init_abundance[key]:
                fitness += abs(self.objective[key] - rel_abundance[key])
                #print("Name: " + key + " Init: " + str(init_abundance[key]) + " Now: " + str(abundance[key]))
            else:
                fitness = -1.0
                self.fitness_medium = fitness
                return

        fitness = abs(fitness - self.fitness) * 100
        fitness += len(self.chromosome)

        self.fitness_medium = round(fitness, 6)

    def fitness_function(self, init_abundance, abundance, rel_abundance):
        fitness = 0.0
        #fitness += len(self.chromosome)
        for key in self.objective:
            #print("Name: " + key + " Init: " + str(init_abundance[key]) + " Now: " + str(abundance[key]))
            if abundance[key] > init_abundance[key]:
                fitness += abs(self.objective[key] - rel_abundance[key])
                #print("Name: " + key + " Init: " + str(init_abundance[key]) + " Now: " + str(abundance[key]))
            else:
                fitness = -1.0
                break

        self.fitness = round(fitness, 6)

    def get_fitness(self):
        if self.fitness == None:
            self.score_fitness(fitness_func=self.fitness_function)
        return self.fitness

    def get_medium_fitness(self):
        if self.fitness_medium == None:
            self.score_fitness(fitness_func=self.fitness_medium_function)
        return self.fitness_medium

    def __lt__(self, other):
        """an indicidual is lesser than another when its fitness score is higher. higher fitness == bad"""
        return self.get_fitness() < other.get_fitness()

    def sort_med_fitness(ind):
        return ind.get_medium_fitness()
