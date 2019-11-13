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

def run_headless(config_file):
    """reads in settings of the GA from settings file"""

    (culture, objective, medium_volume, output_dir, queue_fitness, queue_founder, callback, num_cpus,
     sim_time, timestep, pop_size, death_per_gen, iterations, run_name, mutation_chance, deletion_chance,
     mutation_freq, deletion_freq, crossover_freq, twopoint, repeats, chromosome) = load_runfile(config_file)

    run_GA(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder, callback, num_cpus,
            sim_time, timestep, pop_size, death_per_gen, iterations, run_name, mutation_chance, deletion_chance,
            mutation_freq, deletion_freq, crossover_freq, twopoint, repeats, chromosome)

def load_runfile(config_file):
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

    with open(config_file, 'r') as file:
        run_name = file.readline().strip('\n').split(' ')[1]
        print("Run Name {}".format(run_name))
        for line in file:
            # print(line.strip('\n'))
            if line.strip('\n') == '':
                continue
            else:
                line = line.strip('\n').split(' ')
                # print(line)
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
                    #print(num_species)
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
    return (culture, objective, medium_volume, output_dir, queue_fitness, queue_founder, callback, num_cpus,
            sim_time, timestep, pop_size, death_per_gen, iterations, run_name, mutation_chance, deletion_chance,
            mutation_freq, deletion_freq, crossover_freq, twopoint, repeats, chromosome)

def save_runfile(individual, population, output_dir, run_name, iterations, num_runs, chromosome_file=None):
    """Writes a settings file of the current run"""
    print("Writing setup to file: at {}".format(output_dir + "/" + run_name + "_runfile.txt"))
    with open(output_dir + "/" + run_name + "_runfile.txt", 'w') as file:
        file.write("#RUN_NAME {}\n".format(run_name))
        file.write("\nGENERAL\n")
        file.write("#NUM_RUNS {}\n".format(num_runs))
        file.write("#NUM_CPUS {}\n".format(population.num_processes))
        file.write("#OUTPUT_DIR {}\n".format(output_dir))
        file.write("\nFBA\n")
        file.write("#SIM_TIME {}\n".format(individual.simulation_time))
        file.write("#TIMESTEP {}\n".format(individual.timestep))
        file.write("#DEATH_RATE {}\n".format(individual.data_watcher.get_death_rate()))
        file.write("#MEDIUM_VOLUME {}\n".format(individual.medium_volume))
        file.write("#PFBA {}\n".format(individual.data_watcher.get_pfba()))
        file.write("#ENFORCE_GROWTH {}\n".format(individual.data_watcher.get_enforce_growth()))
        file.write("#AEROB_GROWTH {}\n".format(individual.data_watcher.get_oxygen()))
        file.write("\nGA\n")
        file.write("#POP_SIZE {}\n".format(population.size))
        file.write("#OFFSPRING_PER_GEN {}\n".format(population.deaths))
        file.write("#ITERATIONS {}\n".format(iterations))
        file.write("#MUTATION_CHANCE {}\n".format(population.mutation_chance))
        file.write("#DELETION_CHANCE {}\n".format(population.deletion_chance))
        file.write("#MUTATION_FREQ {}\n".format(population.mutation_freq))
        file.write("#DELETION_FREQ {}\n".format(population.deletion_freq))
        file.write("#CROSSOVER_FREQ {}\n".format(population.crossover_freq))
        file.write("#TWO_POINT {}\n".format(population.twopoint))
        file.write("#CHROMOSOME {}\n".format(chromosome_file if chromosome_file is not None else ""))
        file.write("\nSPECIES\n")
        file.write("#NUM_SPECIES {}\n".format(len(individual.culture)))
        file.write("\n")

        for spec in individual.culture.species_list:
            file.write("#NAME {}\n".format(spec.name))
            file.write("#MODEL {}\n".format(spec.model_file))
            file.write("#RADIUS {}\n".format(spec.get_radius()))
            file.write("#DRYWEIGHT {}\n".format(spec.dry_weight))
            file.write("#INNOCULATION_SIZE {}\n".format(int(spec.get_init_abundance())))
            file.write("#OBJECTIVE {}\n".format(individual.objective[spec.name]))
            file.write("\n")

def run_GA(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder,  callback, num_cpus, sim_time, timestep, pop_size, death_per_gen, iterations, run_name, mutation_chance, deletion_chance, mutation_freq, deletion_freq, crossover_freq, twopoint, repeats, chromosome):

    if chromosome == None:
        if callback != None:
            from tkinter import END, DISABLED, NORMAL
            callback.graph_page.text.config(state=NORMAL)
            callback.graph_page.text.insert(END, "Finding Essential Nutrients...\n")
            callback.graph_page.text.config(state=DISABLED)

        print("Finding Essential Nutrients...")
        num_essentials, essential_nutrients = GA.find_essential_nutrients(culture.species_list, len(culture.species_list) // 2)
        
        if callback != None:
            callback.graph_page.text.config(state=NORMAL)
            callback.graph_page.text.insert(END, "Found {} Essential Nutrients!\n".format(num_essentials))
            callback.graph_page.text.config(state=DISABLED)

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

    if callback != None:
        callback.graph_page.text.config(state=NORMAL)
        callback.graph_page.text.insert(END, "Starting Genetic Algorithm\n")
        callback.graph_page.text.config(state=DISABLED)

    save_runfile(founder, population, output_dir, run_name, iterations, repeats, chromosome)
    print("Starting Genetic Algorithm")
    GA.run_GA(population, output_dir, queue_fitness, queue_founder, callback, run_name, iterations, repeats)

    if callback != None:
        callback.graph_page.text.config(state=NORMAL)
        callback.graph_page.text.insert(END, "Finished Genetic Algorithm\n")
        callback.graph_page.text.config(state=DISABLED)

    print("Finished Genetic Algorithm")

if __name__ == '__main__':
    """if no settings file is provided start GUI"""
    SEED_to_Names = {}
    with open("data/seed_mtabolites_edited.tsv") as file:
        file.readline()
        for line in file:
            line = line.split('\t')
            SEED_to_Names[line[0]] = line[2]

    if len(argv) == 2:
        run_headless(argv[1])

    else:
        from GUI import *
        open_gui()
