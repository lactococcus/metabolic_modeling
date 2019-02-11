from Culture import Culture
from Medium import *
from Species import Species
from Chromosome import Chromosome
from Individual import Individual
from multiprocessing import Process, Queue
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

def run_GA(culture, objective, medium_volume, output_dir, num_essentials, essential_nutrients, queue_fitness, queue_founder, callback, num_cpu=1, simulation_time=12, timestep=1, pop_size=50, iter=10, suffix=""):

    info_file_path = "%s/run_info_%s.txt" % (output_dir, suffix)

    with open(info_file_path, 'w') as file:
        file.write("Starting Run\n")
        file.write("Found %d Essential Nutrients!\n" % num_essentials)

    dicts = generate_dicts(culture.species_list, essential_nutrients)
    names_to_index = dicts[0]
    index_to_names = dicts[1]

    founder = Individual(culture, Chromosome(index_to_names, num_essentials), objective, medium_volume, simulation_time, timestep, culture.data_watcher)
    founder.chromosome.initialize_all_true()

    print("pre callback")
    queue_fitness.put_nowait(founder.get_fitness())
    queue_founder.put_nowait(founder)
    callback.update_graphs()
    print("post callback")

    for i in range(iter):
        population = []
        res = Queue()

        if num_cpu > 1:
            processes = [Process(target=generate_population, args=(founder, pop_size, num_cpu, x, res)) for x in range(num_cpu)]
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
        queue_founder.put_nowait(founder)
        queue_fitness.put_nowait(founder.get_fitness())
        callback.update_graphs()

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

        if founder.get_fitness() < 0.005:
            break

    #Medium.export_medium(founder.chromosome.to_medium(0.05), "U:/Masterarbeit/GA_Results/medium_founder%s.txt" % suffix)
    founder.chromosome.export_chromosome("%s/chromosome_%s.txt" % (output_dir, suffix))

    medium = minimize_medium(founder)
    Medium.export_medium(medium, "%s/medium_minimized_%s.txt" % (output_dir, suffix))

    return medium



if __name__ == '__main__':

    runs = 10
    nutrient_dist = {}

    for i in range(runs):
        print("Run: %d" % i)
        medium = run_GA(species_list, objective,  medium_volume, output_dir, num_essentials, essential_nutrients, num_cpu, simulation_time, timestep, pop_size, iteration, str(i), False)
        for comp in medium.get_components():
            if comp in nutrient_dist:
                nutrient_dist[comp] += 1
            else:
                nutrient_dist[comp] = 1

    else:
        with open("U:/Masterarbeit/GA_Results/nutrient_heatmap.txt", 'w') as file:
            file.write("Number of Runs: %d\n" % runs)
            for key in nutrient_dist:
                nutrient_dist[key] /= runs
                file.write("%s;%f\n" % (key, nutrient_dist[key]))