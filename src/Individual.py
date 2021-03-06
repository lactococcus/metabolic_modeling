from Culture import *
from DataWatcher import DataWatcher
from matplotlib import pyplot as plt
import math
import gc

class Individual:
    def __init__(self, culture, chromosome, objective, medium_volume, simulation_time=24, timestep=1, data_watcher=None):
        """Class representing an idividual in the Genetic algorithm context. An individual consists out of a bacterial culture and a chromosome. It handles the fitness evaluation"""
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

    def plot(self, save_uptake=False, medium=None, sub_plot=None, force=False, save_crossfeed=False):
        """plot the growth curves of the bacterial culture"""
        self.register_data_watcher(self.data_watcher)
        if medium is not None:
            self.score_fitness(self.fitness_function, save_uptake, medium, save_crossfeed=save_crossfeed)
        else:
            self.get_fitness(save_uptake=save_uptake, force=force, medium=medium, save_crossfeed=save_crossfeed)

        if sub_plot is not None:
            sub_plot.clear()
            for spec in self.culture.species_list:
                curve = spec.get_growth_curve()
                sub_plot.plot([self.timestep * x for x in range(len(curve))], curve, label=spec.name)
            sub_plot.legend()

        else:
            for spec in self.culture.species_list:
                curve = spec.get_growth_curve()
                plt.plot([self.timestep * x for x in range(len(curve))], curve, label=spec.name)
            plt.xlabel("Time [h]")
            plt.ylabel("Biomass [pg]")
            plt.legend()
            plt.show()

    def score_fitness(self, fitness_func, save_uptake=False, medium=None, save_crossfeed=False):
        """scores the fitness of an individual based on the fitness function passed as an argument"""
        if medium is None:
            self.culture.set_medium(self.chromosome.to_medium(self.medium_volume, self.data_watcher.get_oxygen()))
        else:
            self.culture.set_medium(medium)

        data_watcher = DataWatcher.create_new_watcher(self.data_watcher)
        self.register_data_watcher(data_watcher)

        for i in range(math.floor(self.simulation_time / self.timestep)):
            if not self.culture.update_biomass(self.timestep, save_uptake, save_crossfeed=save_crossfeed):
                break
        fitness_func()

    def fitness_function(self):
        """l2 norm fitness function"""
        total_biomass = sum([(spec.get_biomass() * 1e12) for spec in self.culture.species_list])

        fitness = 0.0
        for spec_name in self.objective:
            init_biomass = self.data_watcher.get_init_biomass(spec_name)
            biomass = self.data_watcher.get_biomass(spec_name)
            rel_biomass = biomass / total_biomass
            fitness += 1000 * (self.objective[spec_name] - rel_biomass) ** 2
            if biomass <= init_biomass and self.data_watcher.get_enforce_growth():
                fitness = -1.0
                break
        self.data_watcher.set_fitness(round(fitness, 6))
        gc.collect()

    def get_fitness(self, save_uptake=False, force=False, medium=None, save_crossfeed=False):
        """returns the fitness of the individual. Evaluates the ftness if it wasn't already"""
        if self.data_watcher.get_fitness() == None or force or medium != None or save_crossfeed or save_uptake:
            self.score_fitness(fitness_func=self.fitness_function, save_uptake=save_uptake, medium=medium, save_crossfeed=save_crossfeed)
        return self.data_watcher.get_fitness()

    def get_crossfeed_interactions(self):
        return self.data_watcher.get_crossfeeding()

    def get_uptakes(self):
        return self.data_watcher.get_uptake()

    def __lt__(self, other):
        """an indicidual is lesser than another when its fitness score is higher. higher fitness == bad"""
        return self.get_fitness() > other.get_fitness()

    def register_data_watcher(self, data_watcher):
        self.data_watcher = data_watcher
        self.culture.register_data_watcher(data_watcher)

    def copy(self):
        return Individual(self.culture.copy(), self.chromosome.copy(), self.objective, self.medium_volume, self.simulation_time, self.timestep, self.data_watcher)

    def reconstruct(self, other):
        """rebinds variables of an idividual after being copied in another thread so the garbage collector can get rid of the duplicates. Causes memory leak if not used"""
        self.culture = other.culture.copy()
        self.chromosome.reconstruct(other.chromosome)
        self.objective = other.objective
        self.medium_volume = other.medium_volume
        self.simulation_time = other.simulation_time
        self.timestep = other.timestep

    def __len__(self):
        return len(self.culture)

    def __str__(self):
        return "Individual with Fitness: {}".format(self.get_fitness())

    def __del__(self):
        del self.data_watcher
        self.chromosome = None
        self.culture = None
        self.objective = None
        self.timestep = None
        self.simulation_time = None
        self.medium_volume = None
