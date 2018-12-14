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
                med_dict[self.index_to_names[i]] = 10.0 * volume

        return Medium.from_dict(med_dict, volume)

    def export_chromosome(self, file_path):
        with open(file_path, 'w') as file:
            for key in self.index_to_names:
                file.write(self.index_to_names[key] + "\n")
            file.write("-chrom-\n")
            file.write(str(self.chromosome))

    def import_chromosome(file_path):
        index_to_names = {}
        chromosome = []
        flag = True
        counter = 0
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip("\n")
                if line == "-chrom-":
                    flag = False
                if flag:
                    index_to_names[counter] = line
                    counter += 1
                else:
                    line = line.strip("[")
                    line = line.strip("]")
                    values = line.split(", ")
                    for value in values[1:]:
                        chromosome.append(bool(value == "True"))
        chr = Chromosome(index_to_names)
        chr.chromosome = chromosome
        return chr

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

    def __len__(self):
        counter = 0
        for boolean in self.chromosome:
            if boolean:
                counter += 1
        return counter
