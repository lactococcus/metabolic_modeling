from Medium import Medium
import random

class Chromosome:
    def __init__(self, index_to_names, num_essentials=0):
        #self.names_to_index = names_to_index
        self.index_to_names = index_to_names
        self.num_essentials = num_essentials
        self.chromosome = [False for i in range(len(self.index_to_names))]

        for i in range(self.num_essentials):
            self.chromosome[i] = True

    def to_medium(self, volume):
        med_dict = {}

        for i, bool in enumerate(self.chromosome):
            if bool:
                med_dict[self.index_to_names[i]] = 10.0

        return Medium.from_dict(med_dict, volume)

    def mutate(self, number_of_mutation):
        for i in range(number_of_mutation):
            index = random.randrange(self.num_essentials, len(self.chromosome))
            self.chromosome[index] = not self.chromosome[index]

    def mutate_with_chance(self, mutation_chance):
        for i, bool in enumerate(self.chromosome):
            if i >= self.num_essentials:
                self.chromosome[i] = (not self.chromosome[i]) if random.random() <= mutation_chance else self.chromosome[i]

    def initialize_random(self):
        for i in range(self.num_essentials, len(self.chromosome)):
            self.chromosome[i] = True if random.random() <= 0.8 else False

    def initialize_all_true(self):
        for i, bool in enumerate(self.chromosome):
            self.chromosome[i] = True

