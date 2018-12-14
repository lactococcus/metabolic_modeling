from Culture import Culture
from Medium import *
from Species import Species
from Chromosome import Chromosome
from Individual import Individual
import multiprocessing as mp
import itertools
from cobra.flux_analysis import find_essential_reactions
from copy import deepcopy
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
                if timepoint > start:
                    break
                start = timepoint
            else:
                min_medium[key] = ref_medium[key]
    #med.plot_nutrients_over_time()
    size_after = len(min_medium)
    print("Before: " + str(size_before) + " After: " + str(size_after))

    return min_medium

def generate_population(culture, pop_size, cpu_count, proc_num, medium_volume, simulation_time, timestep, index_to_names, essentials, objective, founder=None, queue=None):
    population = []

    chromosome = None
    population_size = 0

    if proc_num == 0:
        population_size = pop_size // cpu_count + pop_size % cpu_count
    else:
        population_size = pop_size // cpu_count

    if founder == None:
        for i in range(1):
            chromosome = Chromosome(index_to_names, essentials)
            chromosome.initialize_all_true()
            individual = Individual(culture, chromosome, objective, medium_volume, simulation_time, timestep)
            if individual.get_fitness() >= 0.0:
                population.append(individual)

    else:
        if proc_num == 0:
            population.append(founder)

        for i in range(population_size):
            chromosome = deepcopy(founder.chromosome)
            chromosome.mutate_with_chance(0.01)
            individual = Individual(culture, chromosome, objective, medium_volume, simulation_time, timestep)
            if individual.get_fitness() >= 0.0:
                population.append(individual)

    queue.put(population)

def main():
    num_cpu = 4 #mp.cpu_count()
    info_file_path = "U:/Masterarbeit/GA_Results/run_info.txt"

    spec1 = Species('Lactococcus', "U:/Masterarbeit/iNF517.xml", 1.0)
    spec2 = Species('Klebsiella', "U:/Masterarbeit/Klebsiella/Klebsiella.xml", 1.0)

    culture = Culture()
    culture.innoculate_species(spec1, 1000000)
    culture.innoculate_species(spec2, 1000000)

    objective = {"Lactococcus": 0.5, "Klebsiella": 0.5}

    print("Finding Essential Nutrients...")
    num_essentials, essential_nutrients = find_essential_nutrients(culture.species_list, num_cpu)
    print("Found " + str(num_essentials) + " Essential Nutrients!")

    with open(info_file_path, 'w') as file:
        file.write("Starting Run\n")
        file.write("Found " + str(num_essentials) + " Essential Nutrients!\n")

    dicts = generate_dicts(culture.species_list, essential_nutrients)
    names_to_index = dicts[0]
    index_to_names = dicts[1]
    #for key in names_to_index:
        #print(key + ": " + str(names_to_index[key]))

    founder = None

    pop_size = 150

    for i in range(30):
        population = []
        res = mp.Queue()
        culture_copy = deepcopy(culture)

        if num_cpu > 1:
            processes = [mp.Process(target=generate_population, args=(culture_copy, pop_size, num_cpu, x, 0.05, 10, 1, index_to_names, num_essentials, objective, founder, res)) for x in range(num_cpu)]
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
            generate_population(culture_copy, pop_size, 1, 1, 0.05, 10, 1, index_to_names, num_essentials, objective, founder, res)
            population.append(res.get())

        population = list(itertools.chain.from_iterable(population))

        population.sort()
        founder = population[-1]

        with open(info_file_path, 'a') as file:
            print("Feasible: " + str(len(population)) + "/" + str(pop_size+1))
            print("Average # Nutrients: " + str(average_num_nutrients(population)) + " Founder: " + str(len(founder.chromosome)))
            print("Iteration: " + str(i+1) + " Fitness: " + str(founder.get_fitness()))
            file.write("Feasible: " + str(len(population)) + "/" + str(pop_size+1) + "\n")
            file.write("Average # Nutrients: " + str(average_num_nutrients(population)) + " Founder: " + str(len(founder.chromosome)) + "\n")
            file.write("Iteration: " + str(i+1) + " Fitness: " + str(founder.get_fitness()) + "\n")

        if founder.get_fitness() < 0.0002:
            break

    Medium.export_medium(founder.chromosome.to_medium(0.05), "U:/Masterarbeit/GA_Results/medium_founder.txt")
    medium = minimize_medium(founder)
    Medium.export_medium(Medium.from_dict(medium, 0.05), "U:/Masterarbeit/GA_Results/medium.txt")
    founder.chromosome.export_chromosome("U:/Masterarbeit/GA_Results/chromosome.txt")

    with open(info_file_path, 'a') as file:
        for spec in founder.culture.species_list:
            print(spec.name + ": " + str(spec.get_abundance()))
            file.write(spec.name + ": " + str(spec.get_abundance()) + "\n")

    founder.plot()

if __name__ == '__main__':
    main()