from Medium import Medium
import random

class Chromosome:
    def __init__(self, names_to_index, index_to_names, essentials=None):
        self.names_to_index = names_to_index
        self.index_to_names = index_to_names
        self.chromosome = [False for i in range(len(names_to_index))]
        self.essentials = essentials

        if self.essentials == None:
            self.essentials = [False for i in range(len(names_to_index))]

    def to_medium(self, volume):
        med_dict = {}

        for i, bool in enumerate(self.chromosome):
            if bool or self.essentials[i]:
                med_dict[self.index_to_names[i]] = 10.0

        return Medium.from_dict(med_dict, volume)

    def mutate(self, number_of_mutation):
        for i in range(number_of_mutation):
            index = random.randrange(len(self.chromosome))
            self.chromosome[index] = not self.chromosome[index]

    def mutate_with_chance(self, mutation_chance):
        for i, bool in enumerate(self.chromosome):
            self.chromosome[i] = (not self.chromosome[i]) if random.random() <= mutation_chance else self.chromosome[i]

    def initialize_random(self):
        for i, bool in enumerate(self.chromosome):
            self.chromosome[i] = True if random.random() <= 0.8 else False

    def initialize_all_true(self):
        for i, bool in enumerate(self.chromosome):
            self.chromosome[i] = True

