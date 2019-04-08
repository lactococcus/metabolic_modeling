from Culture import Culture
from Medium import *
from Species import Species
from Chromosome import *
from Individual import Individual
from multiprocessing import Process, Queue
import itertools
from cobra.flux_analysis import find_essential_reactions
from copy import deepcopy
from matplotlib import pyplot as plt
from DataWatcher import DataWatcher
from tkinter import END, DISABLED, NORMAL

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
    """removes unused components from the medium"""
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
                #start = timepoint
    #med.plot_nutrients_over_time()
    size_after = len(min_medium)
    print("Before: " + str(size_before) + " After: " + str(size_after))

    return Medium.from_dict(min_medium, individual.medium_volume)

def minimize_medium2(individual, medium, threshold):
    original = medium.copy()
    med = original.copy()
    #original.print_content()
    print(len(original))
    individual.score_fitness(individual.fitness_function, medium=med)
    old_fitness = individual.get_fitness()
    print("old fitness: %f" % old_fitness)

    for component in medium.get_components():
        med = original.copy()
        med.remove_component(component)
        individual.score_fitness(individual.fitness_function, medium=med)
        new_fitness = individual.get_fitness()
        print(component)
        print("New fitness: %f diff: %f\n" % (new_fitness, new_fitness - old_fitness))
        if new_fitness < 0.0:
            continue
        if (new_fitness - old_fitness) <= threshold * len(individual):
            original.remove_component(component)
    print("Now: %d" % len(original))
    return original

def generate_population(founder, pop_size, cpu_count, proc_num, queue=None, pfba=False, enforce_growth=True, oxigen=True):
    population = []
    population_size = 0

    if proc_num == 0:
        population_size = pop_size // cpu_count + pop_size % cpu_count
    else:
        population_size = pop_size // cpu_count

    for i in range(population_size):
        chromosome = founder.chromosome.copy()
        chromosome.mutate_with_chance(0.01)
        individual = Individual(founder.culture, chromosome, founder.objective, founder.medium_volume, founder.simulation_time, founder.timestep, founder.data_watcher, enforce_growth, oxigen)
        #print(individual.get_fitness())
        if individual.get_fitness(pfba) >= 0.0:
            population.append(individual)

    if proc_num == 0:
        population.append(founder)

    queue.put(population)

def run_GA(culture, objective, medium_volume, output_dir, num_essentials, essential_nutrients, queue_fitness, queue_founder, callback=None, num_cpu=1, simulation_time=12, timestep=1, pop_size=50, iter=10, suffix="", pfba=False, enforce_growth=True, oxigen=True):

    info_file_path = "%s/run_info_%s.txt" % (output_dir, suffix)

    if callback is not None and callback.flag:
        return

    dicts = generate_dicts(culture.species_list, essential_nutrients)
    names_to_index = dicts[0]
    index_to_names = dicts[1]

    founder = Individual(culture, Chromosome_Quantitative(index_to_names, names_to_index, num_essentials), objective, medium_volume, simulation_time, timestep, culture.data_watcher)
    founder.chromosome.initialize_all_true()

    if callback is not None:
        queue_fitness.put(founder.get_fitness(pfba))
        queue_founder.put(founder)
        callback.update_graphs()

    for i in range(iter):
        population = []
        res = Queue()

        if num_cpu > 1:
            processes = [Process(target=generate_population, args=(founder, pop_size, num_cpu, x, res, pfba, enforce_growth, oxigen)) for x in range(num_cpu)]
            #processes = [(mp.Process(target=test, args=(res, x))) for x in range(10)]

            for process in processes:
                process.daemon = True
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
            generate_population(founder, pop_size, num_cpu, 0, res, pfba, enforce_growth, oxigen)
            population.append(res.get())

        population = list(itertools.chain.from_iterable(population))

        population.sort(reverse=True)
        founder = population[0]

        founder.register_data_watcher(founder.data_watcher)

        if callback is not None:
            queue_founder.put(founder)
            queue_fitness.put(founder.get_fitness())
            callback.update_graphs()

        callback.graph_page.text.config(state=NORMAL)
        with open(info_file_path, 'a') as file:
            callback.graph_page.text.insert(END, "Iteration: %d Fitness: %f\n" % (i+1, founder.get_fitness()))
            callback.graph_page.text.insert(END, "Feasible: %d/%d\n" % (len(population),pop_size+1))
            file.write("Iteration: %d Fitness: %f\n" % (i+1, founder.get_fitness()))
            file.write("Feasible: %d/%d\n" % (len(population),pop_size+1))
            total = 0
            for spec in founder.culture.species_list:
                total += spec.get_abundance()
            for spec in founder.culture.species_list:
                callback.graph_page.text.insert(END, "%s : %d : %f\n" % (spec.name, spec.get_abundance(), spec.get_abundance() / total))
                file.write("%s : %d : %f\n" % (spec.name, spec.get_abundance(), spec.get_abundance() / total))
            callback.graph_page.text.insert(END, "Founder: %d\n\n" % len(founder.chromosome))
            #file.write("Average # Nutrients: %f Founder: %d\n\n" % (average_num_nutrients(population), len(founder.chromosome)))
        callback.graph_page.text.config(state=DISABLED)

        if founder.get_fitness() <= 0.00002 * len(founder.culture):
            break

        if callback is not None and callback.flag:
            break

    if callback is not None:
       callback.update_graphs()

    founder.chromosome.export_chromosome("%s/chromosome_%s.txt" % (output_dir, suffix))

    medium = minimize_medium(founder)
    #small_medium = minimize_medium2(founder, medium, 0.01)
    #Medium.export_medium(small_medium, "%s/medium_minimized_%s.txt" % (output_dir, suffix))

    if callback is not None:
        callback.graph_page.text.config(state=NORMAL)
        callback.graph_page.text.insert(END, "Finished")
        callback.graph_page.text.config(state=DISABLED)

        callback.graph_page.medium_control.add_medium(medium)

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