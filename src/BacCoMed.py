import GA
from Species import Species
from Culture import Culture
from DataWatcher import DataWatcher
from multiprocessing import Process, Queue
from threading import Thread
import queue
import os.path
from Medium import *
from Population import Population
from Individual import Individual
from Chromosome import *
import gc
from sys import argv

def run_headless(cofig_file):
    culture = Culture()
    data_watcher = DataWatcher()
    culture.register_data_watcher(data_watcher)
    objective = None
    medium_volume = None
    output_dir = None
    queue_fitness = None
    queue_founder = None
    callback = None
    num_cpus = None
    sim_time = None
    timestep = None
    pop_size = None
    death_per_gen = None
    iterations = None
    run_name = ""
    mutation_chance = None
    deletion_chance = None
    mutation_freq = None
    deletion_freq = None
    crossover_freq = None
    twopoint = None
    repeats = None
    chromosome = None
    objective = {}

    num_species = 0

    with open(cofig_file, 'r') as file:
        run_name = file.readline().strip('\n').split(' ')[1]
        print("Run Name {}".format(run_name))
        for line in file:
            #print(line.strip('\n'))
            if line.strip('\n') == '':
                continue
            else:
                line = line.strip('\n').split(' ')
                #print(line)
                if line[0] == '#NUM_RUNS':
                    repeats = int(line[1])
                    print("Repeats {}".format(repeats))
                    continue
                elif line[0] == '#NUM_CPUS':
                    num_cpus = int(line[1])
                    print("CPUs {}".format(num_cpus))
                    continue
                elif line[0] == '#OUTPUT_DIR':
                    output_dir = line[1]
                    print("Output Dir {}".format(output_dir))
                    continue
                elif line[0] == '#SIM_TIME':
                    sim_time = int(line[1])
                    print("Simulation Time {}".format(sim_time))
                    continue
                elif line[0] == '#TIMESTEP':
                    timestep = float(line[1])
                    print("Timestep {}".format(timestep))
                    continue
                elif line[0] == '#DEATH_RATE':
                    data_watcher.set_death_rate(float(line[1]))
                    continue
                elif line[0] == '#MEDIUM_VOLUME':
                    medium_volume = float(line[1])
                    print("Medium Volume {}".format(medium_volume))
                    continue
                elif line[0] == '#PFBA':
                    data_watcher.set_pfba(True if line[1] == 'True' else False)
                    continue
                elif line[0] == '#ENFORCE_GROWTH':
                    data_watcher.set_enforce_growth(True if line[1] == 'True' else False)
                    continue
                elif line[0] == '#AEROB_GROWTH':
                    data_watcher.set_oxygen(True if line[1] == 'True' else False)
                    continue
                elif line[0] == '#POP_SIZE':
                    pop_size = int(line[1])
                    print("Population Size {}".format(pop_size))
                    continue
                elif line[0] == '#OFFSPRING_PER_GEN':
                    death_per_gen = int(line[1])
                    print("Offspring per Gen {}".format(death_per_gen))
                    continue
                elif line[0] == '#ITERATIONS':
                    iterations = int(line[1])
                    print("Iterations {}".format(iterations))
                    continue
                elif line[0] == '#MUTATION_CHANCE':
                    mutation_chance = float(line[1])
                    print("Mutation Chance {}".format(mutation_chance))
                    continue
                elif line[0] == '#DELETION_CHANCE':
                    deletion_chance = float(line[1])
                    print("Deletion Chance {}".format(deletion_chance))
                    continue
                elif line[0] == '#MUTATION_FREQ':
                    mutation_freq = float(line[1])
                    print("Mutation Freq {}".format(mutation_freq))
                    continue
                elif line[0] == '#DELETION_FREQ':
                    deletion_freq = float(line[1])
                    print("Deletion Freq {}".format(deletion_freq))
                    continue
                elif line[0] == '#CROSSOVER_FREQ':
                    crossover_freq = float(line[1])
                    print("Crossover Freq {}".format(crossover_freq))
                    continue
                elif line[0] == '#TWO_POINT':
                    twopoint = True if line[1] == 'True' else False
                    print("Twopoint {}".format(twopoint))
                    continue
                elif line[0] == '#CHROMOSOME':
                    chromosome = line[1] if line[1] != '' else None
                    continue
                elif line[0] == '#NUM_SPECIES':
                    num_species = int(line[1])
                    break

        print("Loading Species")
        for i in range(num_species):
            line = file.readline().strip('\n')
            while line == '':
                line = file.readline().strip('\n')

            spec_name = line.split(' ')[1]
            print("Name {}".format(spec_name))
            model = file.readline().strip('\n').split(' ')[1]
            radius = float(file.readline().strip('\n').split(' ')[1])
            dryweight = float(file.readline().strip('\n').split(' ')[1])
            inn = int(file.readline().strip('\n').split(' ')[1])
            obj = float(file.readline().strip('\n').split(' ')[1])

            species = Species(spec_name, model, radius, dryweight)
            culture.innoculate_species(species, inn)
            objective[spec_name] = obj

    print("Loaded Configurations")
    run_GA(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder, callback, num_cpus,
            sim_time, timestep, pop_size, death_per_gen, iterations, run_name, mutation_chance, deletion_chance,
            mutation_freq, deletion_freq, crossover_freq, twopoint, repeats, chromosome)

def run_GA(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder,  callback, num_cpus, sim_time, timestep, pop_size, death_per_gen, iterations, run_name, mutation_chance, deletion_chance, mutation_freq, deletion_freq, crossover_freq, twopoint, repeats, chromosome):

    if chromosome == None:
        print("Finding Essential Nutrients...")
        num_essentials, essential_nutrients = GA.find_essential_nutrients(culture.species_list, len(culture.species_list) // 2)
        print("Found {} Essential Nutrients!\n".format(num_essentials))
        dicts = GA.generate_dicts(culture.species_list, essential_nutrients)
        names_to_index = dicts[0]
        index_to_names = dicts[1]
        chr = Chromosome_Quantitative(index_to_names, names_to_index, num_essentials)
        chr.initialize_medium(LB)
    else:
        chr = Chromosome_Quantitative.import_from_list(chromosome)
        chr.initialize_random(0.05)
    founder = Individual(culture, chr, objective, medium_volume, sim_time, timestep, culture.data_watcher)

    while founder.get_fitness(force=True) == -1.0:
        founder.chromosome.initialize_random(0.05)

    population = Population(founder, pop_size, death_per_gen, mutation_chance, deletion_chance, crossover_freq, mutation_freq, deletion_freq, twopoint, num_cpus)

    print("Starting Genetic Algorithm")
    GA.run_GA(population, output_dir, queue_fitness, queue_founder, callback, run_name, iterations, repeats)
    print("Finished Genetic Algorithm")

if __name__ == '__main__':
    bg_blue = "#8f9eb7"
    bg_grey = "#DDDDDD"

    if len(argv) == 2:
        run_headless(argv[1])

    else:
        from GUI import *
        open_gui()
