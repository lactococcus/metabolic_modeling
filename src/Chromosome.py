from Medium import Medium
import random
from copy import deepcopy

class Chromosome:
    def __init__(self, index_to_names, names_to_index, num_essentials=0):
        self.names_to_index = names_to_index
        self.index_to_names = index_to_names
        self.num_essentials = num_essentials
        self.chromosome = None

    def to_medium(self, volume):
        pass

    def export_chromosome(self, file_path):
        pass

    def import_chromosome(file_path):
        pass

    def mutate(self, number_of_mutation):
        pass

    def deletion(self, number_of_mutation):
        pass

    def mutate_with_chance(self, mutation_chance):
        pass

    def delete_with_chance(self, mutation_chance):
        pass

    def initialize_random(self):
        pass

    def initialize_all_true(self):
        pass

    def initialize_medium(self, stock_medium, volume=1.0):
        pass

    def make_new_chromosome(self):
        pass

    def copy(self):
        pass

    def crossover(self, other, two_point=False):
        first = random.randrange(self.num_essentials - 1, len(self.chromosome))
        second = random.randrange(first, len(self.chromosome)) if two_point == True else len(self.chromosome)

        for i in range(first, second):
            self.chromosome[i], other.chromosome[i] = other.chromosome[i], self.chromosome[i]

    def __str__(self):
        return str(self.chromosome)

    def __len__(self):
        counter = 0
        for boolean in self.chromosome:
            if boolean:
                counter += 1
        return counter

    def __del__(self):
        del self.chromosome
        self.num_essentials = None
        self.names_to_index = None
        self.index_to_names = None
        #print("Destroyed Chromosome")

class Chromosome_Qualitative(Chromosome):
    def __init__(self, index_to_names, names_to_index, num_essentials=0):
        Chromosome.__init__(self, index_to_names, names_to_index, num_essentials)
        self.chromosome = [False for i in range(len(self.index_to_names))]

        for i in range(self.num_essentials):
            self.chromosome[i] = True

    def to_medium(self, volume):
        med_dict = {}

        for i, bool in enumerate(self.chromosome):
            if bool:
                name = self.index_to_names[i]
                med_dict[name] = 1000.0 * volume

        return Medium.from_dict(med_dict, volume)

    def export_chromosome(self, file_path):
        with open(file_path, 'w') as file:
            for key in self.index_to_names:
                file.write(str(key) + ":" + self.index_to_names[key] + ":" + str(self.chromosome[int(key)]) + "\n")

    def import_chromosome(file_path):
        index_to_names = {}
        chromosome = []
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip("\n")
                words = line.split(":")
                index_to_names[int(words[0])] = words[1]
                chromosome.append(bool(words[2] == "True"))
        chr = Chromosome_Qualitative(index_to_names, None)
        chr.chromosome = chromosome
        return chr

    def mutate(self, number_of_mutation):
        for i in range(number_of_mutation):
            index = random.randrange(self.num_essentials, len(self.chromosome))
            self.chromosome[index] = not self.chromosome[index]

    def deletion(self, number_of_mutation):
        for i in range(number_of_mutation):
            index = random.randrange(self.num_essentials, len(self.chromosome))
            self.chromosome[index] = False

    def mutate_with_chance(self, mutation_chance):
        for i, bool in enumerate(self.chromosome):
            if i >= self.num_essentials:
                self.chromosome[i] = (not self.chromosome[i]) if random.random() <= mutation_chance else self.chromosome[i]

    def delete_with_chance(self, mutation_chance):
        for i, bool in enumerate(self.chromosome):
            if i >= self.num_essentials:
                self.chromosome[i] = False if random.random() <= mutation_chance else self.chromosome[i]

    def initialize_random(self):
        for i in range(self.num_essentials, len(self.chromosome)):
            self.chromosome[i] = True if random.random() <= 0.5 else False

    def initialize_all_true(self):
        for i, bool in enumerate(self.chromosome):
            self.chromosome[i] = True

    def initialize_medium(self, stock_medium, volume):
        medium = stock_medium.create_medium(volume)
        for component in medium.get_components():
            if component in self.names_to_index:
                self.chromosome[self.names_to_index[component]] = True

    def make_new_chromosome(self):
        chr = Chromosome_Qualitative(self.index_to_names, self.names_to_index, self.num_essentials)
        return chr

    def copy(self):
        chr = Chromosome_Qualitative(self.index_to_names, self.names_to_index, self.num_essentials)
        chr.chromosome = deepcopy(self.chromosome)
        return chr

class Chromosome_Quantitative(Chromosome):
    def __init__(self, index_to_names, names_to_index, num_essentials=0):
        Chromosome.__init__(self, index_to_names, names_to_index, num_essentials)
        self.chromosome = [0.0 for i in range(len(self.index_to_names))]

        for i in range(self.num_essentials):
            self.chromosome[i] = 20.0

    def to_medium(self, volume):
        med_dict = {}

        for i, amount in enumerate(self.chromosome):
            name = self.index_to_names[i]
            flux = round(amount * volume, 6)
            if flux > 0:
                med_dict[name] = flux

        return Medium.from_dict(med_dict, volume)

    def export_chromosome(self, file_path):
        with open(file_path, 'w') as file:
            for key in self.index_to_names:
                file.write("%s:%s:%f\n" % (key, self.index_to_names[key], self.chromosome[int(key)]))

    def import_chromosome(file_path):
        index_to_names = {}
        chromosome = []
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip("\n")
                words = line.split(":")
                index_to_names[int(words[0])] = words[1]
                chromosome.append(float(words[2]))
        chr = Chromosome_Quantitative(index_to_names, None)
        chr.chromosome = chromosome
        return chr

    def mutate(self, number_of_mutation):
        for i in range(number_of_mutation):
            index = random.randrange(self.num_essentials, len(self.chromosome))
            self.chromosome[index] = round(random.uniform(0.0, 1000.0),1)

    def deletion(self, number_of_mutation):
        for i in range(number_of_mutation):
            index = random.randrange(self.num_essentials, len(self.chromosome))
            self.chromosome[index] = 0.0

    def mutate_with_chance(self, mutation_chance):
        for i, amount in enumerate(self.chromosome):
            if i >= self.num_essentials:
                if random.random() <= mutation_chance:
                    self.chromosome[i] = round(random.uniform(0.0, 1000.0),1)

    def delete_with_chance(self, mutation_chance):
        for i, amount in enumerate(self.chromosome):
            if i >= self.num_essentials:
                if random.random() <= mutation_chance:
                    self.chromosome[i] = 0.0

    def initialize_random(self):
        for i in range(self.num_essentials, len(self.chromosome)):
            self.chromosome[i] = round(random.uniform(0.0, 1000.0),1)
        self.delete_with_chance(0.33)

    def initialize_all_true(self):
        for i in range(self.num_essentials, len(self.chromosome)):
            self.chromosome[i] = 1000.0

    def initialize_medium(self, stock_medium, volume):
        medium = stock_medium.create_medium(volume)
        for component in medium.get_components():
            if component in self.names_to_index:
                self.chromosome[self.names_to_index[component]] = medium.get_components()[component]

    def make_new_chromosome(self):
        chr = Chromosome_Quantitative(self.index_to_names, self.names_to_index, self.num_essentials)
        return chr

    def copy(self):
        chr = Chromosome_Quantitative(self.index_to_names, self.names_to_index, self.num_essentials)
        chr.chromosome = deepcopy(self.chromosome)
        return chr

    def reconstruct(self, other):
        self.index_to_names = other.index_to_names
        self.names_to_index = other.names_to_index
        self.num_essentials = other.num_essentials
        self.chromosome = deepcopy(self.chromosome)

    def __len__(self):
        counter = 0
        for amount in self.chromosome:
            if amount > 0.0:
                counter += 1
        return counter