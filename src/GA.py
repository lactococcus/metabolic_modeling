from Culture import Culture
from Medium import *
from Species import Species
from Chromosome import *
from Individual import Individual
from multiprocessing import Process, Queue
import itertools
from copy import deepcopy
from matplotlib import pyplot as plt
from DataWatcher import DataWatcher
import gc
import time

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
    from cobra.flux_analysis import find_essential_reactions
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
    """removes unused components from the medium and minimizes nutrient amount"""
    ref_medium = individual.chromosome.to_medium(individual.medium_volume).get_components()
    size_before = len(ref_medium)
    individual.get_fitness()
    med = individual.culture.medium
    used_medium = individual.culture.medium.components_over_time
    min_medium = {}
    # med.plot_nutrients_over_time()
    for key in ref_medium:
        if key in used_medium:
            progress = used_medium[key]
            # print(progress)
            start = progress[0]
            minimum = min(progress)
            # print(f"Start: {start} Min: {minimum}")
            if minimum < start:
                min_medium[key] = ref_medium[key]

    size_after = len(min_medium)
    print("Before: " + str(size_before) + " After: " + str(size_after))

    return Medium.from_dict(min_medium, individual.medium_volume)


def run_GA(population, output_dir, queue_fitness, queue_founder, callback, suffix, iter, loop):

    ind_solutions = []

    for n in range(loop):

        info_file_path = "{}/run_info_{}{}.txt".format(output_dir, suffix, n)

        with open(info_file_path, 'w') as file:
            file.write("Starting Genetic Algorithm\n")

        if callback != None and callback.flag:
            return

        population.refresh()
        population.generate_initial_population()

        if callback != None:
            from tkinter import END, DISABLED, NORMAL
            fit = (n, population.get_best_fitness(), population.get_average_fitness())
            queue_fitness.put(fit)
            queue_founder.put(population.get_best())
            callback.update_graphs()

        for i in range(iter):

            start = time.time()
            population.new_generation()
            end = time.time()

            if callback != None and callback.flag:
                return

            if callback != None:
                fit = (n, population.get_best_fitness(), population.get_average_fitness())
                queue_fitness.put(fit)
                queue_founder.put(population.get_best())
                callback.update_graphs()

                callback.graph_page.text.config(state=NORMAL)
                callback.graph_page.text.insert(END, "Iteration: {} Fitness: Best: {} Average: {}\n".format(i+1, population.get_best_fitness(), population.get_average_fitness()))
                callback.graph_page.text.insert(END, "Iteration: {} took {} minutes\n".format(i+1, round((end - start) / 60, 2)))
                callback.graph_page.text.config(state=DISABLED)
         
            with open(info_file_path, 'a') as file:
                file.write("Iteration: {} Fitness: Best: {} Average: {}\n".format(i+1, population.get_best_fitness(), population.get_average_fitness()))
                file.write("Iteration: {} took {} min\n".format(i+1, round((end-start) / 60, 2)))

            gc.collect()
            if population.get_best_fitness() <= 0.03:
                break

        if callback != None:
            if callback.flag:
                return
            callback.update_graphs()

        population.get_best().chromosome.export_chromosome("{}/chromosome_{}{}.txt".format(output_dir, suffix, n))

        medium = minimize_medium(population.get_best())
        Medium.export_medium(medium, "{}/medium_minimized_{}{}.txt".format(output_dir, suffix, n))

        if callback != None:
            callback.graph_page.text.config(state=NORMAL)
            callback.graph_page.text.insert(END, "Finished")
            callback.graph_page.text.config(state=DISABLED)

            #callback.graph_page.medium_control.add_medium(medium)

        if population.get_best().get_fitness() <= 0.1:
            ind_solutions.append(medium)

    heatmap = {}
    for sol in ind_solutions:
        for comp in sol.get_components():
            if comp in heatmap:
                heatmap[comp] += 1
            else:
                heatmap[comp] = 1
    for comp in heatmap:
        heatmap[comp] /= len(ind_solutions)

    with open(output_dir + "/medium_heatmap.csv", 'w') as file:
        file.write("ID;%\n")
        for comp in heatmap:
            file.write("{};{}\n".format(comp, heatmap[comp]))

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