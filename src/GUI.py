import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import GA
from Species import Species
from Culture import Culture
from DataWatcher import DataWatcher
from multiprocessing import Process, Queue
from threading import Thread
import queue
import matplotlib
import matplotlib.animation as animation
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.style.use("ggplot")
from CustomEntryWidgets import *
import os.path
from MediumTreeView import MediumTreeView
from Medium import Medium

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
        bacterium.controller.show_frame(SetupPage)

def run_GA(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder,  callback, num_cpus, sim_time, timestep, pop_size, iterations, run_name, mutation_chance, deletion_chance, repeats):
    print("Finding Essential Nutrients...")
    num_essentials, essential_nutrients = GA.find_essential_nutrients(culture.species_list, len(culture.species_list)//2)
    print(f"Found {num_essentials} Essential Nutrients!\n")
    print("Starting Genetic Algorithm")
    GA.run_GA(culture, objective, medium_volume, output_dir, num_essentials, essential_nutrients, queue_fitness, queue_founder, callback, num_cpus, sim_time, timestep, pop_size, iterations, run_name, mutation_chance, deletion_chance, repeats)
    print("Finished Genetic Algorithm")

def quit_and_back():
    app.show_frame(SetupPage)
    run.terminate_process()

def start(setup):

    run.run_name = setup.entry_run_name.get()
    run.num_cpus = setup.entry_cpus.get()
    run.medium_volume = setup.entry_medium.get()
    run.sim_time = setup.entry_sim_time.get()
    run.timestep = setup.entry_timestep.get()
    run.pop_size = setup.entry_pop_size.get()
    run.iterations = setup.entry_iter.get()
    run.output_dir = setup.entry_output.get()
    run.pfba = False if setup.var_pfba.get() is 0 else True
    run.enforce_growth = False if setup.var_growth.get() is 0 else True
    run.oxigen = False if setup.var_oxigen.get() is 0 else True
    run.mutation_chance = setup.entry_mutation_chance.get()
    run.deletion_chance = setup.entry_deletion_chance.get()
    run.repeats = setup.entry_repeats.get()
    run.death_rate = setup.entry_death_rate.get()

    if not os.path.isdir(run.output_dir):
        print(f"'{run.output_dir}' is not a valid directory")
        return

    objective = {}
    data_watcher = DataWatcher()
    data_watcher.set_oxigen(run.oxigen)
    data_watcher.set_enforce_growth(run.enforce_growth)
    data_watcher.set_pfba(run.pfba)
    data_watcher.set_death_rate(run.death_rate)
    culture = Culture()
    culture.register_data_watcher(data_watcher)

    if len(setup.widgets) < 2:
        print("Less than two Species added")
        return

    for widget in setup.widgets:
        objective[widget.species.entry_name.get()] = float(widget.entry_objective.get())
        model = widget.species.entry_model.get()
        if not os.path.isfile(model):
            print(f"Can not find file: {model}")
            return
        print(f"Loading Model of Species: {widget.species.entry_name.get()}")
        species = Species(widget.species.entry_name.get(), model, float(widget.species.entry_radius.get()), float(widget.species.entry_dryweight.get()))
        culture.innoculate_species(species, int(widget.species.entry_innoculation.get()))

    run.objective = objective
    run.culture = culture

    run_page = RunPage(app.container, app)
    run_page.grid(row=0, column=0, sticky="nsew")
    run.graph_page = run_page

    run_page.tkraise()

    run.start_process()


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("500x600")
        self.iconbitmap("U:/Bilder/icon.ico")

        self.title("Bac Co-Med")
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (SetupPage, StartPage):
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

        self.logo_image = tk.PhotoImage(file="U:/Bilder/logo.png")

        ttk.Label(self, image=self.logo_image).grid(row=0, column=0)
        ttk.Button(self, text="New Run", command=lambda :controller.show_frame(SetupPage), style='bigger.TButton').grid(row=1, column=0)
        ttk.Button(self, text="Exit", command=_quit, style='bigger.TButton').grid(row=2, column=0)

class SetupPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.widgets = []

        self.bacteria_image = tk.PhotoImage(file="U:/Bilder/add.gif")
        self.start_image = tk.PhotoImage(file="U:/Bilder/start.gif")
        self.file_image = tk.PhotoImage(file="U:/Bilder/file.gif")
        self.info_image = tk.PhotoImage(file="U:/Bilder/info.gif")

        ttk.Label(self, text="Setup Run", style='bigger.TLabel').grid(row=0, column=1)
        ttk.Label(self, text="Run Name:", style='big.TLabel').grid(row=1, column=0, sticky='w')
        ttk.Separator(self, orient="horizontal").grid(row=2, columnspan=5, sticky='ew')
        ttk.Label(self, text="Bacteria:", style='big.TLabel').grid(row=3, column=0, sticky='w')
        self.add_bacteria_button = ttk.Button(self, text="Add Bacteria", image=self.bacteria_image, compound="left", command=lambda :new_bacteria(parent, controller, self))
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
        ttk.Separator(self, orient="horizontal").grid(row=799, columnspan=5, sticky='ew')

        ttk.Label(self, text="GA Settings:", style='big.TLabel').grid(row=800, column=0, sticky='w')
        ttk.Label(self, text="Population size:").grid(row=885, column=0, sticky='w')
        ttk.Label(self, text="Iterations:").grid(row=886, column=0, sticky='w')
        ttk.Label(self, text="Mutation chance:").grid(row=887, column=0, sticky='w')
        ttk.Label(self, text="Deletion chance:").grid(row=888, column=0, sticky='w')
        ttk.Separator(self, orient="horizontal").grid(row=891, columnspan=5, sticky='ew')

        ttk.Button(self, text="Start Run", image=self.start_image, command=lambda :start(self), compound="left").grid(row=1000, column=0)
        ttk.Button(self, text="Exit", command=_quit).grid(row=1000, column=1)
        #ttk.Button(self, text="Test", command=lambda :controller.show_frame(RunPage)).grid(row=1000, column=2)
        ttk.Button(self, image=self.file_image, command=lambda: choose_directory(self.entry_output)).grid(row=682, column=2, sticky='w')
        ttk.Button(self, image=self.info_image, command=lambda :tk.messagebox.showinfo("Info pFBA", "pFBA also minimizes the amount of metabolites used. However it takes 2x as long.")).grid(row=788, column=2, sticky='w')

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
        self.entry_timestep.set("1")
        self.entry_timestep.grid(row=784, column=1)
        self.entry_death_rate = FloatEntry(self)
        self.entry_death_rate.set("0.0")
        self.entry_death_rate.grid(row=785, column=1)

        self.entry_pop_size = IntEntry(self)
        self.entry_pop_size.set("50")
        self.entry_pop_size.grid(row=885, column=1)
        self.entry_iter = IntEntry(self)
        self.entry_iter.set("10")
        self.entry_iter.grid(row=886, column=1)
        self.entry_mutation_chance = FloatEntry(self)
        self.entry_mutation_chance.set("0.01")
        self.entry_mutation_chance.grid(row=887, column=1)
        self.entry_deletion_chance = FloatEntry(self)
        self.entry_deletion_chance.set("0.0")
        self.entry_deletion_chance.grid(row=888, column=1)

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

    def update(self):
        self.add_bacteria_button.grid(row=4 + len(self.widgets), column=0)
        for i, widget in enumerate(self.widgets):
            widget.grid(row=4+i, column=0, columnspan=6, sticky="nsew")

class SpeciesWidget(tk.Frame):
    def __init__(self, parent, controller, species):
        tk.Frame.__init__(self, parent)
        self.species = species
        self.parent = parent
        #self.configure(bg=bg_colour)
        self.cross_image = tk.PhotoImage(file="U:/Bilder/cross.gif")
        self.edit_image = tk.PhotoImage(file="U:/Bilder/pencil.gif")
        self.name = tk.StringVar()
        self.name.set(self.species.entry_name.get())
        tk.Label(self, textvariable=self.name).grid(row=0, column=0, sticky='w')
        tk.Label(self, text="Objective:").grid(row=0, column=2, sticky='e')
        self.entry_objective = FloatEntry(self)
        self.entry_objective.grid(row=0, column=3, sticky='e')
        ttk.Button(self, image=self.edit_image, command=lambda: species.tkraise()).grid(row=0, column=4, sticky='w')
        ttk.Button(self, image=self.cross_image, command=lambda: self.remove()).grid(row=0, column=5, sticky='w')

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
        self.file_image = tk.PhotoImage(file="U:/Bilder/file.gif")
        ttk.Label(self, text="Bacterium", style='big.TLabel').grid(row=0, column=1)
        ttk.Label(self, text="Name:").grid(row=1, column=0, sticky='w')
        ttk.Label(self, text="Model:").grid(row=2, column=0, sticky='w')
        ttk.Label(self, text="Radium in micrometer:").grid(row=3, column=0, sticky='w')
        ttk.Label(self, text="Dryweight in picogram:").grid(row=4, column=0, sticky='w')
        ttk.Label(self, text="Innoculation size:").grid(row=5, column=0, sticky='w')
        ttk.Button(self, text="Save Bacterium", command=lambda :add_bacterium(parent_page, controller, self)).grid(row=6, column=0)
        ttk.Button(self, text="Back", command=lambda :controller.show_frame(SetupPage)).grid(row=100, column=0)
        ttk.Button(self, image=self.file_image, command=lambda: choose_file(self.entry_model)).grid(row=2, column=2, sticky='w')

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
        #self.configure(bg=bg_colour)
        self.fig1 = Figure(figsize=(4,4), dpi=100)
        self.plot_fitness = self.fig1.add_subplot(111)
        self.fig2 = Figure(figsize=(4,4), dpi=100)
        self.plot_founder = self.fig2.add_subplot(111)
        self.fig3 = Figure(figsize=(4, 4), dpi=100)
        self.plot_test_medium = self.fig3.add_subplot(111)

        self.queue_fitness = None
        self.queue_founder = None
        self.fitness = None

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)
        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self)
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        self.canvas1.get_tk_widget().grid(row=1, column=0, padx=10)
        self.canvas2.get_tk_widget().grid(row=4, column=0, padx=10)
        self.canvas3.get_tk_widget().grid(row=4, column=2, padx=10)


        ttk.Label(self, text="Fitness:", style='big.TLabel').grid(row=0, column=0)
        ttk.Label(self, text="Current Best:", style='big.TLabel').grid(row=3, column=0)
        ttk.Label(self, text="Minimized Medium:", style='big.TLabel').grid(row=3, column=2)
        ttk.Button(self, text="Back", command=quit_and_back).grid(row=0, column=1)

        self.anim_fitness = animation.FuncAnimation(self.fig1, self._draw_fitness, interval=2000)
        self.anim_founder = animation.FuncAnimation(self.fig2, self._draw_founder, interval=2000)
        self.anim_medium = animation.FuncAnimation(self.fig3, self._draw_medium, interval=2000)

        self.text = tk.Text(self, state=tk.DISABLED)
        self.text.grid(row=1, column=2)

        #medium = Medium.import_medium("U:\Masterarbeit\GA_Results\medium_minimized_9901.txt")
        self.medium_control = MediumTreeView(self, parent, run_object=run)
        #self.medium_control.add_medium(medium)
        self.medium_control.grid(row=1, column=3, padx=30, rowspan=4, columnspan=3, sticky='n')

    def _draw_fitness(self, i):
        self.canvas1.draw()

    def _draw_founder(self, i):
        self.canvas2.draw()

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
            for fitness in self.fitness:
                self.plot_fitness.plot(range(len(fitness)), fitness)
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
            founder.plot(sub_plot=self.plot_founder)
            self.plot_founder.set_xlabel("Time [h]")
            self.plot_founder.set_ylabel("Abundance")
            self.fig2.align_labels(self.plot_founder)

class RunObject:
    def __init__(self):
        self.run_name = None
        self.num_cpus = None
        self.medium_volume = 0.05
        self.sim_time = 48
        self.timestep = 0.5
        self.pop_size = 50
        self.iterations = 20
        self.output_dir = None
        self.objective = None
        self.culture = None
        self.pfba = False
        self.enforce_growth = True
        self.oxigen = True
        self.mutation_chance = 0.01
        self.deletion_chance = 0.0
        self.repeats=1
        self.death_rate=0.0

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
        self.process = Thread(target=run_GA, args=(self.culture, self.objective, self.medium_volume, self.output_dir, self.graph_page.queue_fitness, self.graph_page.queue_founder, self, self.num_cpus, self.sim_time, self.timestep, self.pop_size, self.iterations, self.run_name, self.mutation_chance, self.deletion_chance, self.repeats))
        self.process.start()

    def terminate_process(self):
        if self.process is not None:
            self.flag = True
            self.process.join()
            self.graph_page = None
            print("Tasks terminated")

    def update_graphs(self):
        if self.graph_page != None:
            self.graph_page.update_fitness_plot()
            self.graph_page.update_founder_plot()

if __name__ == '__main__':
    bg_blue = "#8f9eb7"
    bg_grey = "#DDDDDD"

    run = RunObject()

    app = Application()

    style = ttk.Style()
    style.configure('.', font=('Helvetica', 10))
    style.configure('big.TLabel', font=('Helvetica', 14))
    style.configure('bigger.TLabel', font=('Helvetica', 18))
    style.configure('bigger.TButton', font=('Helvetica', 18, 'bold'))
    style.configure('TButton', font=('bold'))

    app.mainloop()