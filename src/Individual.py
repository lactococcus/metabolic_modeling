from Culture import *
from DataWatcher import DataWatcher
from matplotlib import pyplot as plt
import math


class Individual:
    def __init__(self, culture, chromosome, objective, medium_volume, simulation_time=24, timestep=1, data_watcher=None):
        self.culture = culture
        self.chromosome = chromosome
        self.objective = objective
        self.simulation_time = simulation_time
        self.timestep = timestep
        self.medium_volume = medium_volume
        self.data_watcher = None

        if data_watcher == None:
            data_watcher = DataWatcher()
            self.register_data_watcher(data_watcher)
            self.data_watcher.init_data_watcher(self)
        else:
            data_watcher2 = DataWatcher.create_new_watcher(data_watcher)
            self.register_data_watcher(data_watcher2)

    def plot(self, medium=None):
        if medium == None:
            self.culture.set_medium(self.chromosome.to_medium(self.medium_volume))
        else:
            self.culture.set_medium(medium)
        #self.culture.medium.print_content()
        growth = {}

        for spec in self.culture.species_list:
            spec.set_abundance(spec.get_init_abundance())
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
        if medium == None:
            self.culture.set_medium(self.chromosome.to_medium(self.medium_volume))
        else:
            self.culture.set_medium(medium)

        for spec in self.culture.species_list:
            spec.set_abundance(spec.get_init_abundance())

        for i in range(math.floor(self.simulation_time / self.timestep)):
            if not self.culture.update_biomass(self.timestep):
                break

        fitness_func()

    def fitness_function(self):
        total_abundance = 0
        for spec in self.data_watcher.get_species():
            total_abundance += self.data_watcher.get_species()[spec][1]
        fitness = 0.0
        for key in self.objective:
            init_abundance = self.data_watcher.get_species()[key][0]
            abundance = self.data_watcher.get_species()[key][1]
            rel_abundance = abundance / total_abundance
            if abundance > init_abundance:
                fitness += abs(self.objective[key] - rel_abundance) * 100
            else:
                fitness = -1.0
                break
        self.set_fitness(round(fitness, 6))

    def get_fitness(self):
        if self.data_watcher.get_fitness() == None:
            self.score_fitness(fitness_func=self.fitness_function)
        return self.data_watcher.get_fitness()

    def set_fitness(self, fitness):
        self.data_watcher.set_fitness(fitness)

    def __lt__(self, other):
        """an indicidual is lesser than another when its fitness score is higher. higher fitness == bad"""
        return self.get_fitness() > other.get_fitness()

    def sort_med_fitness(ind):
        return ind.get_medium_fitness()

    def register_data_watcher(self, data_watcher):
        self.data_watcher = data_watcher
        self.culture.register_data_watcher(data_watcher)
