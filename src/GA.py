from Culture import Culture
from Medium import *
from Species import Species
from Chromosome import Chromosome
from Individual import Individual
import multiprocessing as mp

def generate_dicts(species_list):
    names_to_index = {}
    index_to_names = {}
    counter = 0
    for species in species_list:
        for ex in species.model.exchanges:
            if ex.id not in names_to_index:
                names_to_index[ex.id] = counter
                counter += 1

    for key in names_to_index:
        index_to_names[names_to_index[key]] = key

    return names_to_index, index_to_names



def generate_population(culture, pop_size, medium_volume, simulation_time, timestep, names_to_index, index_to_names, objective, founder=None):
    population = []

    chromosome = None

    if founder == None:
        for i in range(pop_size):
            chromosome = Chromosome(names_to_index, index_to_names)
            chromosome.initialize_random()
            individual = Individual(culture, chromosome, objective, medium_volume, simulation_time, timestep)
            individual.score_fitness()
            population.append(individual)

    else:
        for i in range(pop_size):
            chromosome = founder.chromosome
            chromosome.mutate(1)
            individual = Individual(culture, chromosome, objective, medium_volume, simulation_time, timestep)
            individual.score_fitness()
            population.append(individual)

    return population


def main():
    spec1 = Species('Lactococcus', "U:/Masterarbeit/Lactococcus/Lactococcus.xml", 1.0, 0.52)
    spec2 = Species('Klebsiella', "U:/Masterarbeit/Klebsiella/Klebsiella.xml", 1.0)

    culture = Culture()
    culture.innoculate_species(spec1, 100)
    culture.innoculate_species(spec2, 100)

    objective = {"Lactococcus": 0.8, "Klebsiella": 0.2}

    dicts = generate_dicts(culture.species_list)
    names_to_index = dicts[0]
    index_to_names = dicts[1]

    founder = None
    for i in range(20):
        print(i + 1)
        population = generate_population(culture, 10, 0.05, 10, 1, names_to_index, index_to_names, objective, founder)
        population.sort()
        founder = population[-1]
        if founder.get_fitness() == 0.0:
            break

    print(founder.chromosome.to_medium(0.05).print_content())





if __name__ == '__main__':
    main()