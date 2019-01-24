from Culture import Culture
from Medium import *
from Species import Species
from Chromosome import Chromosome
from Individual import Individual
import multiprocessing as mp
import itertools
from cobra.flux_analysis import find_essential_reactions
from copy import deepcopy
from matplotlib import pyplot as plt
from DataWatcher import DataWatcher
#import threading as th

def generate_dicts(species_list, essentials):
    names_to_index = {}
    index_to_names = {}
    counter = len(essentials)

    for nutrient in essentials:
        names_to_index[nutrient] = essentials[nutrient]

    for species in species_list:
        for ex in species.model.exchanges:
            if ex.id not in names_to_index:
                names_to_index[ex.id] = counter
                counter += 1

    for key in names_to_index:
        index_to_names[names_to_index[key]] = key

    return names_to_index, index_to_names

def find_essential_nutrients(species_list, cpu_count):
    essentials = {}
    counter = 0
    for species in species_list:
        for exchange in species.model.exchanges:
            exchange.lower_bound = -1000.0
            exchange.upper_bound = 1000.0
        ess = find_essential_reactions(species.model, 0.001, cpu_count)
        for reaction in ess:
            if reaction.id[:3] == "EX_":
                if reaction.id not in essentials:
                    essentials[reaction.id] = counter
                    counter += 1
                #print(reaction.id)
    return counter, essentials

def average_num_nutrients(population):
    average = 0
    for ind in population:
        average += len(ind.chromosome)
    average /= len(population)
    return round(average, 3)

def minimize_medium(individual):
    ref_medium = individual.chromosome.to_medium(individual.medium_volume).get_components()
    size_before = len(ref_medium)
    #individual.score_fitness()
    med = individual.culture.medium
    used_medium = individual.culture.medium.components_over_time
    min_medium = {}
    #med.plot_nutrients_over_time()
    for key in ref_medium:
        if key in used_medium:
            progress = used_medium[key]
            #print(progress)
            start = progress[0]
            for timepoint in progress:
                if timepoint < start:
                    min_medium[key] = ref_medium[key]
                    break
                start = timepoint
    #med.plot_nutrients_over_time()
    size_after = len(min_medium)
    print("Before: " + str(size_before) + " After: " + str(size_after))

    return Medium.from_dict(min_medium, individual.medium_volume)

def generate_population(founder, pop_size, cpu_count, proc_num, queue=None):
    population = []
    population_size = 0

    if proc_num == 0:
        population_size = pop_size // cpu_count + pop_size % cpu_count
    else:
        population_size = pop_size // cpu_count

    for i in range(population_size):
        chromosome = Chromosome(founder.chromosome.index_to_names, founder.chromosome.num_essentials)
        chromosome.chromosome = deepcopy(founder.chromosome.chromosome)
        chromosome.mutate_with_chance(0.01)
        individual = Individual(founder.culture, chromosome, founder.objective, founder.medium_volume, founder.simulation_time, founder.timestep, founder.data_watcher)
        #print(individual.get_fitness())
        if individual.get_fitness() >= 0.0:
            population.append(individual)

    if proc_num == 0:
        population.append(founder)

    queue.put(population)

def main(suffix="", graphs=False):
    num_cpu = 4 #mp.cpu_count()
    medium_volume = 0.05
    simulation_time = 12
    timestep = 1
    info_file_path = "U:/Masterarbeit/GA_Results/run_info%s.txt" % suffix

    spec1 = Species('Lactococcus', "U:/Masterarbeit/iNF517.xml", 1.0)
    spec2 = Species('Klebsiella', "U:/Masterarbeit/Klebsiella/Klebsiella.xml", 1.0)

    data_watcher = DataWatcher()

    culture = Culture()
    culture.register_data_watcher(data_watcher)

    culture.innoculate_species(spec1, 50000000)
    culture.innoculate_species(spec2, 50000000)

    objective = {"Lactococcus": 0.5, "Klebsiella": 0.5}

    print("Finding Essential Nutrients...")
    num_essentials, essential_nutrients = find_essential_nutrients(culture.species_list, num_cpu)
    print("Found %d Essential Nutrients!\n" % num_essentials)

    with open(info_file_path, 'w') as file:
        file.write("Starting Run\n")
        file.write("Found %d Essential Nutrients!\n" % num_essentials)

    dicts = generate_dicts(culture.species_list, essential_nutrients)
    names_to_index = dicts[0]
    index_to_names = dicts[1]

    founder = Individual(culture, Chromosome(index_to_names, num_essentials), objective, medium_volume, simulation_time, timestep, data_watcher)
    founder.chromosome.initialize_all_true()

    pop_size = 100
    fitness = [founder.get_fitness()]
    for i in range(10):
        population = []
        res = mp.Queue()

        if num_cpu > 1:
            processes = [mp.Process(target=generate_population, args=(founder, pop_size, num_cpu, x, res)) for x in range(num_cpu)]
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
            generate_population(founder, pop_size, num_cpu, 0, res)
            population.append(res.get())

        population = list(itertools.chain.from_iterable(population))

        population.sort(reverse=True)
        founder = population[0]
        fitness.append(founder.get_fitness())
        founder.register_data_watcher(founder.data_watcher)
        #print infos
        with open(info_file_path, 'a') as file:
            print("Iteration: %d Fitness: %f" % (i+1, founder.get_fitness()))
            print("Feasible: %d/%d" % (len(population),pop_size+1))
            file.write("Iteration: %d Fitness: %f\n" % (i+1, founder.get_fitness()))
            file.write("Feasible: %d/%d\n" % (len(population),pop_size+1))
            total = 0
            for spec in founder.culture.species_list:
                total += spec.get_abundance()
            for spec in founder.culture.species_list:
                print("%s : %d : %f" % (spec.name, spec.get_abundance(), spec.get_abundance() / total))
                file.write("%s : %d : %f\n" % (spec.name, spec.get_abundance(), spec.get_abundance() / total))
            print("Average # Nutrients: %f Founder: %d\n" % (average_num_nutrients(population), len(founder.chromosome)))
            file.write("Average # Nutrients: %f Founder: %d\n\n" % (average_num_nutrients(population), len(founder.chromosome)))

        if founder.get_fitness() < 0.002:
            break

    Medium.export_medium(founder.chromosome.to_medium(0.05), "U:/Masterarbeit/GA_Results/medium_founder%s.txt" % suffix)
    founder.chromosome.export_chromosome("U:/Masterarbeit/GA_Results/chromosome%s.txt" % suffix)

    with open(info_file_path, 'a') as file:
        for spec in founder.culture.species_list:
            print("%s: %d" % (spec.name, spec.get_abundance()))
            file.write("%s: %d\n" % (spec.name, spec.get_abundance()))

    medium = minimize_medium(founder)
    Medium.export_medium(medium, "U:/Masterarbeit/GA_Results/medium_minimized%s.txt" % suffix)

    if graphs:
        founder.plot()
        plt.plot(fitness, label="fitness")
        plt.legend()
        plt.show()
        founder.plot(medium)

if __name__ == '__main__':
    for i in range(1):
        print("Run: %d" % i)
        main(str(i), True)