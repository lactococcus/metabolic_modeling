from Culture import *
from DataWatcher import DataWatcher
from matplotlib import pyplot as plt
import math


class Individual:
    def __init__(self, culture, chromosome, objective, medium_volume, simulation_time=24, timestep=1, data_watcher=None, enforce_growth=True, oxigen=True):
        self.culture = culture
        self.chromosome = chromosome
        self.objective = objective
        self.simulation_time = simulation_time
        self.timestep = timestep
        self.medium_volume = medium_volume
        self.data_watcher = None

        if data_watcher == None:
            data_watcher = DataWatcher()
            data_watcher.set_oxigen(oxigen)
            data_watcher.set_enforce_growth(enforce_growth)
            self.register_data_watcher(data_watcher)
            self.data_watcher.init_data_watcher(self)
        else:
            data_watcher2 = DataWatcher.create_new_watcher(data_watcher)
            data_watcher2.set_oxigen(oxigen)
            data_watcher2.set_enforce_growth(enforce_growth)
            self.register_data_watcher(data_watcher2)

    def plot(self, medium=None, sub_plot=None):
        if medium is not None:
            self.score_fitness(self.fitness_function, medium)
        else:
            self.get_fitness()

        if sub_plot is not None:
            sub_plot.clear()
            for spec in self.culture.species_list:
                curve = spec.get_growth_curve()
                sub_plot.plot(range(len(curve)), curve, label=spec.name)
            sub_plot.legend()

        else:
            for spec in self.culture.species_list:
                curve = spec.get_growth_curve()
                plt.plot(range(len(curve)), curve, label=spec.name)
            plt.xlabel("Time")
            plt.ylabel("Abundance")
            plt.legend()
            plt.show()

    def score_fitness(self, fitness_func, medium=None, pfba=False):
        if medium is None:
            self.culture.set_medium(self.chromosome.to_medium(self.medium_volume))
        else:
            self.culture.set_medium(medium)

        data_watcher = DataWatcher.create_new_watcher(self.data_watcher)
        self.register_data_watcher(data_watcher)

        for i in range(math.floor(self.simulation_time / self.timestep)):
            if not self.culture.update_biomass(self.timestep, pfba):
                break

        fitness_func()

    def fitness_function(self):
        total_abundance = 0
        for spec in self.culture.species_list:
            total_abundance += spec.get_abundance()
        fitness = 0.0
        for spec_name in self.objective:
            init_abundance = self.data_watcher.get_init_abundance(spec_name)
            abundance = self.data_watcher.get_abundance(spec_name)
            rel_abundance = abundance / total_abundance
            fitness += 1000 * (self.objective[spec_name] - rel_abundance) ** 2
            if abundance <= init_abundance and self.data_watcher.get_enforce_growth():
                fitness = -1.0
                break
        self.data_watcher.set_fitness(round(fitness, 6))

    def get_fitness(self, pfba=False):
        if self.data_watcher.get_fitness() == None:
            self.score_fitness(fitness_func=self.fitness_function, pfba=pfba)
        return self.data_watcher.get_fitness()

    def __lt__(self, other):
        """an indicidual is lesser than another when its fitness score is higher. higher fitness == bad"""
        return self.get_fitness() > other.get_fitness()

    def register_data_watcher(self, data_watcher):
        self.data_watcher = data_watcher
        self.culture.register_data_watcher(data_watcher)

    def __len__(self):
        return len(self.culture)
