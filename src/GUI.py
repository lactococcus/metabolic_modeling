import BacCoMed
import GA
from Species import Species
from Culture import Culture
from DataWatcher import DataWatcher
from multiprocessing import Process, Queue
from threading import Thread
import queue
import matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure
import os.path
from Medium import *
from Population import Population
from Individual import Individual
from Chromosome import *
import gc
from sys import argv
import matplotlib
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from CustomEntryWidgets import *
from MediumTreeView import MediumTreeView
import matplotlib.animation as animation
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
matplotlib.style.use("ggplot")
from optlang import available_solvers

def open_gui():
    global run
    run = RunObject()

    global app
    app = Application()

    style = ttk.Style()
    style.configure('.', font=('Helvetica', 10))
    style.configure('big.TLabel', font=('Helvetica', 14))
    style.configure('bigger.TLabel', font=('Helvetica', 18))
    style.configure('bigger.TButton', font=('Helvetica', 18, 'bold'))
    style.configure('TButton', font=('bold'))

    app.mainloop()

def _quit():
    app.quit()
    app.destroy()
    run.terminate_process()
    exit(0)

def choose_file(entry):
    entry.set(filedialog.askopenfilename())

def choose_directory(entry):
    entry.set(filedialog.askdirectory())

def new_bacteria(parent, controller, parent_page):
    bacteria_page = BacteriaPage(parent, controller, parent_page)
    bacteria_page.grid(row=0, column=0, sticky="nsew")
    bacteria_page.tkraise()

def add_bacterium(parent, controller, bacterium):
    flag = True
    if flag:
        for widget in bacterium.parent_page.widgets:
            if widget.species == bacterium:
                widget.update()
                break
        else:
            species_widget = SpeciesWidget(parent, controller, bacterium)
            bacterium.parent_page.widgets.append(species_widget)
        bacterium.parent_page.update()
        bacterium.parent_page.tkraise()

def quit_and_back():
    app.show_frame(SetupPage)
    run.terminate_process()

def start(setup):
    """loads all the settings from the gui and starts the genetic algorithm"""
    run.run_name = setup.entry_run_name.get()
    run.num_cpus = setup.entry_cpus.get()
    run.medium_volume = setup.entry_medium.get()
    run.sim_time = setup.entry_sim_time.get()
    run.timestep = setup.entry_timestep.get()
    run.pop_size = setup.entry_pop_size.get()
    run.death_per_gen = setup.entry_num_deaths.get()
    run.iterations = setup.entry_iter.get()
    run.output_dir = setup.entry_output.get()
    run.pfba = False if setup.var_pfba.get() is 0 else True
    run.enforce_growth = False if setup.var_growth.get() is 0 else True
    run.oxigen = False if setup.var_oxigen.get() is 0 else True
    run.mutation_chance = setup.entry_mutation_chance.get()
    run.deletion_chance = setup.entry_deletion_chance.get()
    run.repeats = setup.entry_repeats.get()
    run.death_rate = setup.entry_death_rate.get()
    run.mutation_freq = setup.entry_mutation_freq.get()
    run.deletion_freq = setup.entry_deletion_freq.get()
    run.crossover_freq = setup.entry_crossover_freq.get()
    run.twopoint = False if setup.var_twopoint is 0 else True
    run.chromosome = setup.entry_chromosome.get()
    run.solver = setup.solver_var.get()


    if run.mutation_freq + run.deletion_freq + run.crossover_freq != 1:
        print(f"Mutation: {run.mutation_freq} + Deletion: {run.deletion_freq} + Crossover: {run.crossover_freq} is not eaqual to 1")
        return

    if not os.path.isdir(run.output_dir):
        print(f"'{run.output_dir}' is not a valid directory")
        return

    if run.chromosome == '':
        run.chromosome = None
    else:
        if not os.path.isfile(run.chromosome):
            print(f"'{run.chromosome}' does not exist")
            return

    objective = {}
    data_watcher = DataWatcher()
    data_watcher.set_oxygen(run.oxigen)
    data_watcher.set_enforce_growth(run.enforce_growth)
    data_watcher.set_pfba(run.pfba)
    data_watcher.set_death_rate(run.death_rate)
    culture = Culture()
    culture.register_data_watcher(data_watcher)

    if len(setup.widgets) < 2:
        print("Less than two Species added")
        return

    run.objective = objective
    run.culture = culture

    run_page = RunPage(app.container, app)
    run_page.grid(row=0, column=0, sticky="nsew")
    run.graph_page = run_page

    run_page.tkraise()

    for widget in setup.widgets:
        objective[widget.species.entry_name.get()] = widget.entry_objective.get()
        model = widget.species.entry_model.get()
        if not os.path.isfile(model):
            print(f"Can not find file: {model}")
            return

        if run.graph_page != None:
            from tkinter import END, DISABLED, NORMAL
            run.graph_page.text.config(state=NORMAL)
            run.graph_page.text.insert(END, f"Loading Model of Species: {widget.species.entry_name.get()}\n")
            run.graph_page.text.config(state=DISABLED)

        print(f"Loading Model of Species: {widget.species.entry_name.get()}")
        species = Species(widget.species.entry_name.get(), model, widget.species.entry_radius.get(), widget.species.entry_dryweight.get(), run.solver.lower())
        culture.innoculate_species(species, widget.species.entry_innoculation.get())

    run.start_process()


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #self.attributes('-fullscreen', True)
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.iconbitmap("assets/icon.ico")

        self.title("Bac Co-Med")
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        global file_image
        file_image = tk.PhotoImage(file="assets/file.gif")
        global bacteria_image
        bacteria_image = tk.PhotoImage(file="assets/add.gif")
        global start_image
        start_image = tk.PhotoImage(file="assets/start.gif")
        global info_image
        info_image = tk.PhotoImage(file="assets/info.gif")
        global cross_image
        cross_image = tk.PhotoImage(file="assets/cross.gif")
        global edit_image
        edit_image = tk.PhotoImage(file="assets/pencil.gif")

        for F in (SetupPage, StartPage, RefinePage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, frame):
        if frame in self.frames:
            self.frames[frame].tkraise()
        else:
            print("Frame %s not existing!" % frame)

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.logo_image = tk.PhotoImage(file="assets/logo.png")

        ttk.Label(self, image=self.logo_image).grid(row=0, column=0)
        ttk.Button(self, text="Run GA", command=lambda :controller.show_frame(SetupPage), style='bigger.TButton').grid(row=1, column=0)
        ttk.Button(self, text="Refine Medium", command=lambda :controller.show_frame(RefinePage), style='bigger.TButton').grid(row=2, column=0)
        ttk.Button(self, text="Exit", command=_quit, style='bigger.TButton').grid(row=3, column=0)

class SetupPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        """Page that allows the user to specify the parameters for the FBA and the genetic algorithm"""

        self.widgets = []
        self.solvers = []
        self.solver_var = tk.StringVar(self)
        for solver in available_solvers.keys():
            if available_solvers[solver]:
                self.solvers.append(solver)
        self.solver_var.set(self.solvers[0])

        ttk.Label(self, text="Setup Run", style='bigger.TLabel').grid(row=0, column=1)
        ttk.Label(self, text="Run Name:", style='big.TLabel').grid(row=1, column=0, sticky='w')
        ttk.Separator(self, orient="horizontal").grid(row=2, columnspan=5, sticky='ew')
        ttk.Label(self, text="Bacteria:", style='big.TLabel').grid(row=3, column=0, sticky='w')
        self.add_bacteria_button = ttk.Button(self, text="Add Bacteria", image=bacteria_image, compound="left", command=lambda :new_bacteria(parent, controller, self))
        self.add_bacteria_button.grid(row=4+len(self.widgets), column=0)

        ttk.Separator(self, orient="horizontal").grid(row=678, columnspan=5, sticky='ew')
        ttk.Label(self, text="General Settings:", style='big.TLabel').grid(row=679, column=0, sticky='w')
        ttk.Label(self, text="Number of runs: ").grid(row=680, column=0, sticky='w')
        ttk.Label(self, text="Number of CPUs:").grid(row=681, column=0, sticky='w')
        ttk.Label(self, text="Output directory:").grid(row=682, column=0, sticky='w')
        ttk.Separator(self, orient="horizontal").grid(row=699, columnspan=5, sticky='ew')

        ttk.Label(self, text="FBA Settings:", style='big.TLabel').grid(row=700, column=0, sticky='w')
        ttk.Label(self, text="Medium volume:").grid(row=787, column=0, sticky='w')
        ttk.Label(self, text="Simulation time:").grid(row=783, column=0, sticky='w')
        ttk.Label(self, text="Timestep:").grid(row=784, column=0, sticky='w')
        ttk.Label(self, text="Death rate:").grid(row=785, column=0, sticky='w')
        ttk.Label(self, text="pFBA:").grid(row=788, column=0, sticky='w')
        ttk.Label(self, text="Enforce growth:").grid(row=789, column=0, sticky='w')
        ttk.Label(self, text="Aerob growth:").grid(row=790, column=0, sticky='w')
        ttk.Label(self, text="LP-Solver:").grid(row=791, column=0, sticky='w')
        ttk.Separator(self, orient="horizontal").grid(row=799, columnspan=5, sticky='ew')

        ttk.Label(self, text="GA Settings:", style='big.TLabel').grid(row=800, column=0, sticky='w')
        ttk.Label(self, text="Population size:").grid(row=885, column=0, sticky='w')
        ttk.Label(self, text="Offspring per generation:").grid(row=886, column=0, sticky='w')
        ttk.Label(self, text="Iterations:").grid(row=887, column=0, sticky='w')
        ttk.Label(self, text="Mutation chance:").grid(row=888, column=0, sticky='w')
        ttk.Label(self, text="Deletion chance:").grid(row=889, column=0, sticky='w')
        ttk.Label(self, text="Mutation frequency:").grid(row=890, column=0, sticky='w')
        ttk.Label(self, text="Deletion frequency:").grid(row=891, column=0, sticky='w')
        ttk.Label(self, text="Crossover frequency:").grid(row=892, column=0, sticky='w')
        ttk.Label(self, text="Two-point crossover:").grid(row=893, column=0, sticky='w')
        ttk.Label(self, text="Chemical list:").grid(row=894, column=0, sticky='w')
        ttk.Separator(self, orient="horizontal").grid(row=899, columnspan=5, sticky='ew')

        ttk.Button(self, text="Start Run", image=start_image, command=lambda :start(self), compound="left").grid(row=1000, column=0)
        ttk.Button(self, text="Back", command=lambda :controller.show_frame(StartPage)).grid(row=1000, column=1)
        #ttk.Button(self, text="Test", command=lambda :controller.show_frame(RunPage)).grid(row=1000, column=2)
        ttk.Button(self, image=file_image, command=lambda: choose_directory(self.entry_output)).grid(row=682, column=2, sticky='w')
        ttk.Button(self, image=info_image, command=lambda :tk.messagebox.showinfo("Info pFBA", "pFBA also minimizes the amount of metabolites used. However it takes 2x as long.")).grid(row=788, column=2, sticky='w')
        ttk.Button(self, image=file_image, command=lambda: choose_file(self.entry_chromosome)).grid(row=894, column=2, sticky='w')

        self.entry_run_name = StringEntry(self)
        self.entry_run_name.grid(row=1, column=1)

        self.entry_repeats = IntEntry(self)
        self.entry_repeats.set("1")
        self.entry_repeats.grid(row=680, column=1)
        self.entry_cpus = IntEntry(self)
        self.entry_cpus.set("4")
        self.entry_cpus.grid(row=681, column=1)
        self.entry_output = FileEntry(self)
        self.entry_output.grid(row=682, column=1)

        self.entry_medium = FloatEntry(self)
        self.entry_medium.set("0.04")
        self.entry_medium.grid(row=787, column=1)
        self.entry_sim_time = IntEntry(self)
        self.entry_sim_time.set( "48")
        self.entry_sim_time.grid(row=783, column=1)
        self.entry_timestep = FloatEntry(self)
        self.entry_timestep.set("0.5")
        self.entry_timestep.grid(row=784, column=1)
        self.entry_death_rate = FloatEntry(self)
        self.entry_death_rate.set("0.0")
        self.entry_death_rate.grid(row=785, column=1)


        self.entry_pop_size = IntEntry(self)
        self.entry_pop_size.set("100")
        self.entry_pop_size.grid(row=885, column=1)
        self.entry_num_deaths = IntEntry(self)
        self.entry_num_deaths.set(str(self.entry_pop_size.get() // 2))
        self.entry_num_deaths.grid(row=886, column=1)
        self.entry_iter = IntEntry(self)
        self.entry_iter.set("100")
        self.entry_iter.grid(row=887, column=1)
        self.entry_mutation_chance = FloatEntry(self)
        self.entry_mutation_chance.set("0.02")
        self.entry_mutation_chance.grid(row=888, column=1)
        self.entry_deletion_chance = FloatEntry(self)
        self.entry_deletion_chance.set("0.01")
        self.entry_deletion_chance.grid(row=889, column=1)
        self.entry_mutation_freq = FloatEntry(self)
        self.entry_mutation_freq.grid(row=890, column=1)
        self.entry_mutation_freq.set("0.5")
        self.entry_deletion_freq = FloatEntry(self)
        self.entry_deletion_freq.grid(row=891, column=1)
        self.entry_deletion_freq.set("0.2")
        self.entry_crossover_freq = FloatEntry(self)
        self.entry_crossover_freq.grid(row=892, column=1)
        self.entry_crossover_freq.set("0.3")
        self.entry_chromosome = StringEntry(self)
        self.entry_chromosome.grid(row=894, column=1)

        self.var_pfba = tk.IntVar()
        self.radio_button_pfba_yes = ttk.Radiobutton(self, text="Yes", variable=self.var_pfba, value=1)
        self.radio_button_pfba_yes.grid(row=788, column=1, sticky='e')
        self.radio_button_pfba_no = ttk.Radiobutton(self, text="No", variable=self.var_pfba, value=0)
        self.radio_button_pfba_no.grid(row=788, column=1, sticky='w')

        self.var_growth = tk.IntVar()
        self.var_growth.set(1)
        self.radio_button_growth_no = ttk.Radiobutton(self, text="No", variable=self.var_growth, value=0)
        self.radio_button_growth_no.grid(row=789, column=1, sticky='w')
        self.radio_button_growth_yes = ttk.Radiobutton(self, text="Yes", variable=self.var_growth, value=1)
        self.radio_button_growth_yes.grid(row=789, column=1, sticky='e')

        self.var_oxigen = tk.IntVar()
        self.var_oxigen.set(1)
        self.radio_button_oxigen_no = ttk.Radiobutton(self, text="No", variable=self.var_oxigen, value=0)
        self.radio_button_oxigen_no.grid(row=790, column=1, sticky='w')
        self.radio_button_oxigen_yes = ttk.Radiobutton(self, text="Yes", variable=self.var_oxigen, value=1)
        self.radio_button_oxigen_yes.grid(row=790, column=1, sticky='e')

        self.var_twopoint = tk.IntVar()
        self.var_twopoint.set(1)
        self.radio_button_twopoint_no = ttk.Radiobutton(self, text="No", variable=self.var_oxigen, value=0)
        self.radio_button_twopoint_no.grid(row=893, column=1, sticky='w')
        self.radio_button_twopoint_yes = ttk.Radiobutton(self, text="Yes", variable=self.var_oxigen, value=1)
        self.radio_button_twopoint_yes.grid(row=893, column=1, sticky='e')

        self.solver_menue = ttk.OptionMenu(self, self.solver_var, self.solver_var.get(), *self.solvers)
        self.solver_menue.grid(row=791, column=1, sticky='w')

    def update(self):
        self.add_bacteria_button.grid(row=4 + len(self.widgets), column=0)
        for i, widget in enumerate(self.widgets):
            widget.grid(row=4+i, column=0, columnspan=6, sticky="nsew")

class SpeciesWidget(tk.Frame):
    def __init__(self, parent, controller, species):
        tk.Frame.__init__(self, parent)

        self.species = species
        self.parent = parent

        self.name = tk.StringVar()
        self.name.set(self.species.entry_name.get())

        tk.Label(self, textvariable=self.name).grid(row=0, column=0, sticky='w')
        tk.Label(self, text="Objective:").grid(row=0, column=2, sticky='e')

        self.entry_objective = FloatEntry(self)
        self.entry_objective.grid(row=0, column=3, sticky='e')

        ttk.Button(self, image=edit_image, command=lambda: species.tkraise()).grid(row=0, column=4, sticky='w')
        ttk.Button(self, image=cross_image, command=lambda: self.remove()).grid(row=0, column=5, sticky='w')

    def update(self):
        self.name.set(self.species.entry_name.get())

    def remove(self):
        self.parent.widgets.remove(self)
        self.grid_remove()
        self.parent.update()

class BacteriaPage(tk.Frame):
    def __init__(self, parent, controller, parent_page):
        tk.Frame.__init__(self, parent)
        self.parent_page = parent_page
        self.controller = controller
        #self.configure(bg=bg_colour)
        ttk.Label(self, text="Bacterium", style='big.TLabel').grid(row=0, column=1)
        ttk.Label(self, text="Name:").grid(row=1, column=0, sticky='w')
        ttk.Label(self, text="Model:").grid(row=2, column=0, sticky='w')
        ttk.Label(self, text="Radius in micrometer:").grid(row=3, column=0, sticky='w')
        ttk.Label(self, text="Dryweight in picogram:").grid(row=4, column=0, sticky='w')
        ttk.Label(self, text="Inoculation size:").grid(row=5, column=0, sticky='w')
        ttk.Button(self, text="Save Bacterium", command=lambda :add_bacterium(parent_page, controller, self)).grid(row=6, column=0)
        ttk.Button(self, text="Back", command=lambda :controller.show_frame(SetupPage)).grid(row=100, column=0)
        ttk.Button(self, image=file_image, command=lambda: choose_file(self.entry_model)).grid(row=2, column=2, sticky='w')

        self.entry_name = StringEntry(self)
        self.entry_name.grid(row=1, column=1)
        self.entry_model = FileEntry(self)
        self.entry_model.grid(row=2, column=1)
        self.entry_radius = FloatEntry(self)
        self.entry_radius.set("0.2")
        self.entry_radius.grid(row=3, column=1)
        self.entry_dryweight = FloatEntry(self)
        self.entry_dryweight.set("0.3")
        self.entry_dryweight.grid(row=4, column=1)
        self.entry_innoculation = IntEntry(self)
        self.entry_innoculation.set("10000")
        self.entry_innoculation.grid(row=5, column=1)

class RunPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.fig1 = Figure(figsize=(4,4), dpi=100)
        self.plot_fitness = self.fig1.add_subplot(111)
        self.fig2 = Figure(figsize=(4,4), dpi=100)
        self.plot_founder = self.fig2.add_subplot(111)

        self.queue_fitness = None
        self.queue_founder = None
        self.fitness = None

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)

        self.canvas1.draw()
        self.canvas2.draw()

        self.canvas1.get_tk_widget().grid(row=1, column=0, padx=10)
        self.canvas2.get_tk_widget().grid(row=1, column=4, padx=10)

        ttk.Label(self, text="Fitness:", style='big.TLabel').grid(row=0, column=0)
        ttk.Label(self, text="Current Best:", style='big.TLabel').grid(row=0, column=4)

        ttk.Button(self, text="Back", command=quit_and_back).grid(row=2, column=0)
        ttk.Button(self, text="Refresh", command=self.update_founder_plot).grid(row=2, column=4)

        self.anim_fitness = animation.FuncAnimation(self.fig1, self._draw_fitness, interval=10000)
        self.anim_founder = animation.FuncAnimation(self.fig2, self._draw_founder, interval=10000)

        self.text = tk.Text(self, state=tk.DISABLED)
        self.text.grid(row=1, column=8)


    def _draw_fitness(self, i):
        try:
            self.canvas1.draw()
        except:
            self.anim_fitness = animation.FuncAnimation(self.fig1, self._draw_fitness, interval=10000)

    def _draw_founder(self, i):
        try:
            self.canvas2.draw()
        except:
            self.anim_founder = animation.FuncAnimation(self.fig2, self._draw_founder, interval=10000)

    def _draw_medium(self, i):
        self.canvas3.draw()

    def __getstate__(self):
        return (self.plot_fitness, self.plot_founder, self.fig1, self.fig2, self.canvas1, self.canvas2, self.fitness)

    def __setstate__(self, state):
        self.plot_fitness, self.plot_founder, self.fig1, self.fig2, self.canvas1, self.canvas2, self.fitness = state

    def update_fitness_plot(self):
        fit = None
        try:
            fit = self.queue_fitness.get(timeout=1.0)
        except queue.Empty:
            pass
        if fit != None:
            self.fitness[fit[0]].append(fit[1])
            self.plot_fitness.clear()
            #self.plot_fitness.xticks(range(run.iterations))
            for fitness in self.fitness:
                self.plot_fitness.plot(fitness)
            self.plot_fitness.set_xlabel("Iteration")
            self.plot_fitness.set_ylabel("Fitness Score")
            self.fig1.align_labels(self.plot_fitness)

    def update_founder_plot(self):
        founder = None
        try:
            founder = self.queue_founder.get(timeout=1.0)
        except queue.Empty:
            pass
        if founder != None:
            founder.plot(sub_plot=self.plot_founder, force=False)
            self.plot_founder.set_xlabel("Time [h]")
            self.plot_founder.set_ylabel("Biomass [pg]")
            self.fig2.align_labels(self.plot_founder)

class RunObject:
    def __init__(self):
        self.run_name = None
        self.num_cpus = None
        self.medium_volume = 0.05
        self.sim_time = 48
        self.timestep = 0.5
        self.pop_size = 50
        self.death_per_gen = 25
        self.iterations = 20
        self.output_dir = None
        self.objective = None
        self.culture = None
        self.pfba = False
        self.enforce_growth = True
        self.oxigen = True
        self.mutation_chance = 0.01
        self.deletion_chance = 0.0
        self.repeats = 1
        self.death_rate = 0.0
        self.mutation_freq = 0.0
        self.deletion_freq = 0.0
        self.crossover_freq = 0.0
        self.twopoint = True
        self.chromosome = None
        self.solver = None


        self.graph_page = None
        self.process = None

        self.flag = False

    def start_process(self):
        self.graph_page.fitness = [[] for i in range(self.repeats)]
        self.graph_page.plot_fitness.clear()
        self.graph_page.plot_founder.clear()
        self.graph_page.queue_fitness = Queue(maxsize=2)
        self.graph_page.queue_founder = Queue(maxsize=2)
        self.flag = False
        self.process = Thread(target=BacCoMed.run_GA, args=(self.culture, self.objective, self.medium_volume, self.output_dir, self.graph_page.queue_fitness, self.graph_page.queue_founder, self, self.num_cpus, self.sim_time, self.timestep, self.pop_size, self.death_per_gen, self.iterations, self.run_name, self.mutation_chance, self.deletion_chance, self.mutation_freq, self.deletion_freq, self.crossover_freq, self.twopoint, self.repeats, self.chromosome))
        self.process.start()

    def terminate_process(self):
        if self.process is not None:
            self.flag = True
            self.process.join()
            self.graph_page = None
            print("Tasks terminated")
            gc.collect()

    def update_graphs(self):
        if self.graph_page != None:
            self.graph_page.update_fitness_plot()
            self.graph_page.update_founder_plot()


class RefinePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        """Page that allows the user to tweak and test a solution of the genetic algorithm"""
        self.individual = None
        self.chrom = None
        self.save = None

        self.fig = Figure(figsize=(4, 4), dpi=100)
        self.plot_growth = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=5, padx=10, rowspan=20)

        #self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        #self.toolbar.update()
        #self.canvas._tkcanvas.grid(row=0, column=0)

        ttk.Label(self, text="Simulated Growth:", style='big.TLabel').grid(row=0, column=5)
        ttk.Label(self, text='Medium refinement', style='big.TLabel').grid(row=0, column=0)

        ttk.Label(self, text="Save File:").grid(row=1, column=0)
        ttk.Label(self, text="Input Chromosome:").grid(row=2, column=0)

        self.entry_chromosome = StringEntry(self)
        self.entry_chromosome.grid(row=2, column=1)
        self.entry_savefile = StringEntry(self)
        self.entry_savefile.grid(row=1, column=1)

        ttk.Button(self, image=file_image, command=lambda: choose_file(self.entry_chromosome)).grid(row=2, column=2, sticky='w')
        ttk.Button(self, image=file_image, command=lambda: choose_file(self.entry_savefile)).grid(row=1, column=2, sticky='w')
        ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage)).grid(row=3, column=0)
        ttk.Button(self, text="Import", command=self.load).grid(row=3, column=1)

    def load(self):
        if self.chrom != self.entry_chromosome.get() or self.save != self.entry_savefile.get():
            chr = Chromosome_Quantitative.import_chromosome(self.entry_chromosome.get())
            self.chrom = self.entry_chromosome.get()

            (culture, objective, medium_volume, output_dir, queue_fitness, queue_founder, callback, num_cpus,
             sim_time, timestep, pop_size, death_per_gen, iterations, run_name, mutation_chance, deletion_chance,
             mutation_freq, deletion_freq, crossover_freq, twopoint, repeats, chromosome) = BacCoMed.load_runfile(self.entry_savefile.get())
            self.save = self.entry_savefile.get()

            self.medium = MediumTreeView(self)
            self.medium.grid(row=1, column=6, rowspan=40)
            self.medium.add_medium(chr.to_medium(medium_volume), medium_volume)

            self.individual = Individual(culture, chr, objective, medium_volume, sim_time, timestep, data_watcher=culture.data_watcher)
        self.plot()

    def plot(self):
        if self.individual != None:
            self.medium.plot_medium(self.individual, self.plot_growth)
            self.canvas.draw()


if __name__ == '__main__':
    bg_blue = "#8f9eb7"
    bg_grey = "#DDDDDD"

    if len(argv) == 2:
        run_headless(argv[1])

    else:
        import tkinter as tk
        from tkinter import filedialog
        from tkinter import ttk
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from CustomEntryWidgets import *
        from MediumTreeView import MediumTreeView

        matplotlib.use("TkAgg")
        matplotlib.style.use("ggplot")
        run = RunObject()

        app = Application()

        style = ttk.Style()
        style.configure('.', font=('Helvetica', 10))
        style.configure('big.TLabel', font=('Helvetica', 14))
        style.configure('bigger.TLabel', font=('Helvetica', 18))
        style.configure('bigger.TButton', font=('Helvetica', 18, 'bold'))
        style.configure('TButton', font=('bold'))

        app.mainloop()