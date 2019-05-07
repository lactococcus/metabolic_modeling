from Individual import Individual
from Chromosome import *
import math
from threading import Thread
from multiprocessing import Pool, Queue
from numpy.random import choice
import gc

class Population:

    def __init__(self, founder, size, deaths, mutation_chance, deletion_chance, crossover_freq, mutation_freq, deletion_freq, twopoint, num_processes):
        self.size = size
        self.deaths = deaths
        self.mutation_chance = mutation_chance
        self.deletion_chance = deletion_chance
        self.crossover_freq = crossover_freq
        self.mutation_freq = mutation_freq
        self.deletion_freq = deletion_freq
        self.twopoint = twopoint
        self.num_processes = num_processes
        self.founder = founder
        self.pool = Pool(processes=self.num_processes, maxtasksperchild=3)

        self.individuals = []

    def get_best_fitness(self):
        return self.individuals[-1].get_fitness()

    def get_average_fitness(self):
        return round(sum([individual.get_fitness() for individual in self.individuals]) / len(self.individuals), 6)

    def add_individual(self, individual):
        '''Adds an individual (or list of individuals) to the population, sortes them by fitness and keeps the pop_size constant.'''
        if isinstance(individual, list):
            for ind in individual:
                ind.reconstruct(self.founder)
                self.individuals.append(ind)
            self.individuals.sort()
            over_size = len(self.individuals) - self.size
            if over_size > 0:
                self.individuals = self.individuals[over_size:]
        else:
            individual.reconstruct(self.founder)
            self.individuals.append(individual)
            self.individuals.sort()
            if len(self.individuals) > self.size:
                self.individuals.pop(0)
        gc.collect()


    def generate_initial_population(self):
        args = [self.founder, (self.size + 1) // self.num_processes]
        data = [args for i in range(self.num_processes)]
        #print(data)
        pop = self.pool.map(_gen_individuals, data)
        flat_pop = [item for sublist in pop for item in sublist]
        flat_pop.append(self.founder)
        self.add_individual(flat_pop)


    def new_generation(self):

        amount = (self.deaths + 1) // self.num_processes

        self.individuals = self.individuals[self.deaths:]
        #print(len(self.individuals))

        total_fitness = sum([ind.get_fitness() for ind in self.individuals])

        rel_fitness = [((ind.get_fitness() / total_fitness) if ind != None else 0.0) for ind in self.individuals]

        offspring = self.pool.map(_reproduce, ([self.individuals, rel_fitness, amount, self.mutation_freq,
                                                self.deletion_freq, self.crossover_freq, self.mutation_chance,
                                                self.deletion_chance, self.twopoint] for i in range(self.num_processes)))

        flat_offspring = [item for sublist in offspring for item in sublist]
        offspring = None

        self.add_individual(flat_offspring)


    def get_best(self):
        return self.individuals[-1]

    def __len__(self):
        return len(self.individuals)

    def __del__(self):
        self.pool.close()
        self.pool.join()


def crossover(parent1, parent2, two_point=False):
    offspring1 = parent1.copy()
    offspring2 = parent2.copy()
    offspring1.chromosome.crossover(offspring2.chromosome, two_point)
    return offspring1, offspring2


def mutation(parent, chance):
    offspring = parent.copy()
    offspring.chromosome.mutate_with_chance(chance)
    return offspring


def deletion(parent, chance):
    offspring = parent.copy()
    offspring.chromosome.delete_with_chance(chance)
    return offspring


def _reproduce(input):
    population, rel_fitness, amount, mutation_freq, deletion_freq, crossover_freq, mutation_chance, deletion_chance, twopoint = input
    result = []
    for i in range(amount):
        operator = choice(a=[0, 1, 2], p=[mutation_freq, deletion_freq, crossover_freq], replace=False)
        parent1 = choice(a=population, p=rel_fitness, replace=False)
        if operator == 0:
            #print("Mutation")
            offspring = mutation(parent1, mutation_chance)
        if operator == 1:
            #print("Deletion")
            offspring = deletion(parent1, deletion_chance)
        if operator == 2:
            #print("Crossover")
            parent2 = parent1
            while parent1 == parent2:
                parent2 = choice(a=population, p=rel_fitness, replace=False)
            offspring, offspring2 = crossover(parent1, parent2, twopoint)
            if offspring2.get_fitness() > -1.0:
                result.append(offspring2)

        if offspring.get_fitness() > -1.0:
            result.append(offspring)
    population = None
    gc.collect()
    return result


def _gen_individuals(input):
    founder, amount = input
    result = []
    for i in range(amount):
        individual = founder.copy()
        individual.chromosome.initialize_random()
        while individual.get_fitness(force=True) == -1.0:
            individual.chromosome.initialize_random()
        result.append(individual)
    return result

