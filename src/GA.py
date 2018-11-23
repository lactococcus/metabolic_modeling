from Culture import Culture
from Medium import *
from Species import Species
from Chromosome import Chromosome
from Individual import Individual
import multiprocessing as mp
import itertools
from cobra.flux_analysis import flux_variability_analysis
#import threading as th

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

def find_essential_nutrients(species_list, names_to_index):
    essentials = [False for x in range(len(names_to_index))]

    for species in species_list:
        for exchange in species.model.exchanges:
            exchange.lower_bound = -1000.0
            exchange.upper_bound = 1000.0
        fva = flux_variability_analysis(species.model, species.model.exchanges, fraction_of_optimum=0.9, loopless=True)
        for i in range(len(fva.index)):
            if fva.iloc[i]['minimum'] < 0 and fva.iloc[i]['minimum'] < 0:
                essentials[names_to_index[fva.iloc[i].name]] = True
    return essentials


def generate_population(culture, pop_size, cpu_count, proc_num, medium_volume, simulation_time, timestep, names_to_index, index_to_names, essentials, objective, founder=None, queue=None):
    population = []

    chromosome = None
    population_size = 0

    if proc_num == 0:
        population_size = pop_size // cpu_count + pop_size % cpu_count
    else:
        population_size = pop_size // cpu_count

    if founder == None:
        for i in range(population_size):
            chromosome = Chromosome(names_to_index, index_to_names, essentials)
            chromosome.initialize_random()
            individual = Individual(culture, chromosome, objective, medium_volume, simulation_time, timestep)
            individual.score_fitness()
            population.append(individual)

    else:
        for i in range(population_size - 1):
            chromosome = founder.chromosome
            chromosome.mutate(1)
            individual = Individual(culture, chromosome, objective, medium_volume, simulation_time, timestep)
            individual.score_fitness()
            population.append(individual)
        population.append(founder)

    queue.put(population)

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
    print("Start FVA")
    essentials = find_essential_nutrients(culture.species_list, names_to_index)
    #essentials = None
    print("End FVA")
    #print(essentials)
    #test(names_to_index, index_to_names)

    founder = None

    num_cpu = mp.cpu_count()
    pop_size = 200

    for i in range(20):
        population = []
        res = mp.Queue()

        if num_cpu > 1:
            processes = [mp.Process(target=generate_population, args=(culture, pop_size, num_cpu, x, 0.05, 12, 1, names_to_index, index_to_names, essentials, objective, founder, res)) for x in range(num_cpu)]
            #processes = [(mp.Process(target=test, args=(res, x))) for x in range(10)]

            for process in processes:
                process.start()
            #print("started")

            for process in processes:
                population.append(res.get())
            #print("got data")

            for process in processes:
                process.join()
                #process.terminate()
            #print("joined")
        else:
            generate_population(culture, pop_size, 1, 1, 0.05, 12, 1, names_to_index, index_to_names, essentials, objective, founder, res)

        population = list(itertools.chain.from_iterable(population))

        population.sort()
        founder = population[-1]
        print("Iteration: " + str(i+1) + " Fitness: " + str(founder.get_fitness()))

        if founder.get_fitness() == 0.0:
            break

    Medium.export_medium(founder.chromosome.to_medium(0.05), "U:/Masterarbeit/GA_Results/medium.txt")

def test(names_to_index, index_to_names):
    c = Chromosome(names_to_index, index_to_names)
    c.initialize_random()
    Medium.export_medium(c.to_medium(0.05), "U:/Masterarbeit/GA_Results/medium_full.txt")
    print("fertig")

if __name__ == '__main__':
    main()