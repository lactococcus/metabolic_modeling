import tkinter as tk
from tkinter import filedialog
import GA
from Species import Species
from Culture import Culture
from DataWatcher import DataWatcher
from multiprocessing import Process, Queue
from threading import Thread
import queue
import matplotlib
#import matplotlib.animation as animation
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.style.use("ggplot")

def choose_file(entry):
    entry.insert(0, filedialog.askopenfilename())

def choose_directory(entry):
    entry.insert(0, filedialog.askdirectory())

def new_bacteria(parent, controller, parent_page):
    bacteria_page = BacteriaPage(parent, controller, parent_page)
    bacteria_page.grid(row=0, column=0, sticky="nsew")
    bacteria_page.tkraise()

def add_bacterium(parent, controller, bacterium):
    for widget in bacterium.parent_page.widgets:
        if widget.species == bacterium:
            widget.update()
            break
    else:
        species_widget = SpeciesWidget(parent, controller, bacterium)
        bacterium.parent_page.widgets.append(species_widget)
    bacterium.parent_page.update()
    bacterium.controller.show_frame(SetupPage)

def run_GA(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder,  callback, num_cpus, sim_time, timestep, pop_size, iterations, run_name):
    print("Finding Essential Nutrients...")
    num_essentials, essential_nutrients = GA.find_essential_nutrients(culture.species_list, num_cpus)
    print("Found %d Essential Nutrients!\n" % num_essentials)

    GA.run_GA(culture, objective, medium_volume, output_dir, num_essentials, essential_nutrients, queue_fitness, queue_founder, callback, num_cpus, sim_time, timestep, pop_size, iterations, run_name)

def quit_and_back():
    run.terminate_process()
    app.show_frame(SetupPage)

def start(setup):
    #app.frames[RunPage].start_animations()
    app.show_frame(RunPage)

    run.run_name = setup.entry_run_name.get()
    run.num_cpus = int(setup.entry_cpus.get())
    run.medium_volume = float(setup.entry_medium.get())
    run.sim_time = int(setup.entry_sim_time.get())
    run.timestep = float(setup.entry_timestep.get())
    run.pop_size = int(setup.entry_pop_size.get())
    run.iterations = int(setup.entry_iter.get())
    run.output_dir = setup.entry_output.get()

    objective = {}
    data_watcher = DataWatcher()
    culture = Culture()
    culture.register_data_watcher(data_watcher)

    for widget in setup.widgets:
        objective[widget.species.entry_name.get()] = float(widget.entry_objective.get())
        species = Species(widget.species.entry_name.get(), widget.species.entry_model.get(), float(widget.species.entry_radius.get()), float(widget.species.entry_dryweight.get()))
        culture.innoculate_species(species, int(widget.species.entry_innoculation.get()))

    run.objective = objective
    run.culture = culture

    run.graph_page = app.frames[RunPage]

    run.start_process()
    #process = Process(target=run_GA, args=(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder, num_cpus, sim_time, timestep, pop_size, iterations, run_name))


class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("500x500")
        self.iconbitmap("U:/Bilder/icon.ico")
        self.configure(bg=bg_colour)
        self.title("Bac Co-Med")
        self.container = tk.Frame(self, bg=bg_colour)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (SetupPage, StartPage, RunPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, frame):
        if frame in self.frames:
            frame = self.frames[frame]
            frame.tkraise()
        else:
            print("Frame %s not existing!" % frame)

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=bg_colour)
        self.logo_image = tk.PhotoImage(file="U:/Bilder/logo.gif")
        label = tk.Label(self, image=self.logo_image, bg=bg_colour).grid(row=0, column=0)
        button = tk.Button(self, text="New Run", font="none 18 bold", bg=bg_colour, command=lambda :controller.show_frame(SetupPage)).grid(row=1, column=0)
        button = tk.Button(self, text="Exit", font="none 18 bold", bg=bg_colour, command=exit).grid(row=2, column=0)

class SetupPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=bg_colour)
        self.widgets = []
        self.bacteria_image = tk.PhotoImage(file="U:/Bilder/bacterium.gif").subsample(3)
        self.start_image = tk.PhotoImage(file="U:/Bilder/start.gif")
        self.file_image = tk.PhotoImage(file="U:/Bilder/file.gif")
        title = tk.Label(self, text="Setup Run", font="none 18 bold", bg=bg_colour).grid(row=0, column=0)
        label = tk.Label(self, text="Run Name:", font="none 14", bg=bg_colour).grid(row=1, column=0)
        label = tk.Label(self, text="Bacteria:", font="none 14", bg=bg_colour).grid(row=2, column=0)
        self.add_bacteria_button = tk.Button(self, text="Add Bacteria", image=self.bacteria_image, bg=bg_colour, height=20, width=100, compound="left", command=lambda :new_bacteria(parent, controller, self))
        self.add_bacteria_button.grid(row=3+len(self.widgets), column=0)
        label = tk.Label(self, text="General Settings:", bg=bg_colour, font="none 14").grid(row=989, column=0)
        label = tk.Label(self, text="Number of CPUs", bg=bg_colour).grid(row=990, column=0)
        label = tk.Label(self, text="Medium volume", bg=bg_colour).grid(row=991, column=0)
        label = tk.Label(self, text="Simulation time", bg=bg_colour).grid(row=992, column=0)
        label = tk.Label(self, text="Timestep", bg=bg_colour).grid(row=993, column=0)
        label = tk.Label(self, text="Population size:", bg=bg_colour).grid(row=994, column=0)
        label = tk.Label(self, text="Iterations:", bg=bg_colour).grid(row=995, column=0)
        label = tk.Label(self, text="Output directory", bg=bg_colour).grid(row=996, column=0)
        start_button = tk.Button(self, text="Start Run", image=self.start_image, bg=bg_colour, command=lambda :start(self), compound="left").grid(row=1000, column=0)
        exit_button = tk.Button(self, text="Exit", command=exit, bg=bg_colour).grid(row=1000, column=1)
        #button = tk.Button(self, text="Test", command=lambda :controller.show_frame(RunPage), bg=bg_colour).grid(row=1000, column=2)

        self.entry_run_name = tk.Entry(self)
        self.entry_run_name.grid(row=1, column=1)
        self.entry_cpus = tk.Entry(self)
        self.entry_cpus.insert(0, "4")
        self.entry_cpus.grid(row=990, column=1)
        self.entry_medium = tk.Entry(self)
        self.entry_medium.insert(0, "0.04")
        self.entry_medium.grid(row=991, column=1)
        self.entry_sim_time = tk.Entry(self)
        self.entry_sim_time.insert(0, "24")
        self.entry_sim_time.grid(row=992, column=1)
        self.entry_timestep = tk.Entry(self)
        self.entry_timestep.insert(0, "1")
        self.entry_timestep.grid(row=993, column=1)
        self.entry_pop_size = tk.Entry(self)
        self.entry_pop_size.insert(0, "50")
        self.entry_pop_size.grid(row=994, column=1)
        self.entry_iter = tk.Entry(self)
        self.entry_iter.insert(0, "10")
        self.entry_iter.grid(row=995, column=1)
        self.entry_output = tk.Entry(self)
        self.entry_output.grid(row=996, column=1)

        file_button = tk.Button(self, image=self.file_image, bg=bg_colour, command=lambda: choose_directory(self.entry_output)).grid(row=996, column=2)

    def update(self):
        self.add_bacteria_button.grid(row=3 + len(self.widgets), column=0)
        for i, widget in enumerate(self.widgets):
            widget.grid(row=3+i, column=0, columnspan=6, sticky="nsew")

class SpeciesWidget(tk.Frame):
    def __init__(self, parent, controller, species):
        tk.Frame.__init__(self, parent)
        self.species = species
        self.parent = parent
        self.configure(bg=bg_colour)
        self.cross_image = tk.PhotoImage(file="U:/Bilder/cross.gif")
        self.edit_image = tk.PhotoImage(file="U:/Bilder/pencil.gif")
        self.name = tk.StringVar()
        self.name.set(self.species.entry_name.get())
        label_name = tk.Label(self, textvariable=self.name, bg=bg_colour).grid(row=0, column=0)
        label = tk.Label(self, text="Objective:", bg=bg_colour).grid(row=0, column=2)
        self.entry_objective = tk.Entry(self)
        self.entry_objective.grid(row=0, column=3)
        button = tk.Button(self, bg=bg_colour, image=self.edit_image, command=lambda: species.tkraise()).grid(row=0, column=4)
        button = tk.Button(self, bg=bg_colour, image=self.cross_image, command=lambda: self.remove()).grid(row=0, column=5)

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
        self.configure(bg=bg_colour)
        self.file_image = tk.PhotoImage(file="U:/Bilder/file.gif")
        label = tk.Label(self, text="Bacterium", font="none 18 bold", bg=bg_colour).grid(row=0, column=1)
        label = tk.Label(self, text="Name:", bg=bg_colour).grid(row=1, column=0)
        label = tk.Label(self, text="Model:", bg=bg_colour).grid(row=2, column=0)
        label = tk.Label(self, text="Radium in micrometer:", bg=bg_colour).grid(row=3, column=0)
        label = tk.Label(self, text="Dryweight in picogram:", bg=bg_colour).grid(row=4, column=0)
        label = tk.Label(self, text="Innoculation size:", bg=bg_colour).grid(row=5, column=0)
        button = tk.Button(self, text="Save Bacterium", bg=bg_colour, command=lambda :add_bacterium(parent_page, controller, self)).grid(row=6, column=0)
        button = tk.Button(self, text="back", bg=bg_colour, command=lambda :controller.show_frame(SetupPage)).grid(row=100, column=0)

        self.entry_name = tk.Entry(self)
        self.entry_name.grid(row=1, column=1)
        self.entry_model = tk.Entry(self)
        self.entry_model.grid(row=2, column=1)
        self.entry_radius = tk.Entry(self)
        self.entry_radius.insert(0, "0.2")
        self.entry_radius.grid(row=3, column=1)
        self.entry_dryweight = tk.Entry(self)
        self.entry_dryweight.insert(0, "0.3")
        self.entry_dryweight.grid(row=4, column=1)
        self.entry_innoculation = tk.Entry(self)
        self.entry_innoculation.insert(0, "10000")
        self.entry_innoculation.grid(row=5, column=1)

        button = tk.Button(self, bg=bg_colour, image=self.file_image, command=lambda :choose_file(self.entry_model)).grid(row=2, column=2)

class RunPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=bg_colour)
        self.fig1 = Figure(figsize=(4,4), dpi=100)
        self.plot_fitness = self.fig1.add_subplot(111)
        self.fig2 = Figure(figsize=(4,4), dpi=100)
        self.plot_founder = self.fig2.add_subplot(111)

        self.queue_fitness = Queue()
        self.queue_founder = Queue()
        self.fitness = []

        self.canvas1 = FigureCanvasTkAgg(self.fig1, self)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self)
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas1.get_tk_widget().grid(row=1, column=0)
        self.canvas2.get_tk_widget().grid(row=3, column=0)
        label = tk.Label(self, text="Fitness", font="none 14 bold", bg=bg_colour).grid(row=0, column=0)
        label = tk.Label(self, text="Current Best:", font="none 14 bold", bg=bg_colour).grid(row=2, column=0)
        button = tk.Button(self, text="Back", bg=bg_colour, command=quit_and_back).grid(row=0, column=1)

    def __getstate__(self):
        return (self.queue_fitness, self.queue_founder)

    def __setstate__(self, state):
        self.queue_fitness, self.queue_founder = state

    def update_fitness_plot(self):
        fit = None
        try:
            fit = self.queue_fitness.get(timeout=1.0)
        except queue.Empty:
            pass
        if fit is not None:
            self.fitness.append(fit)
            self.plot_fitness.clear()
            self.plot_fitness.plot(range(1, len(self.fitness)+1), self.fitness)

    def update_founder_plot(self):
        founder = None
        try:
            founder = self.queue_founder.get(timeout=1.0)
        except queue.Empty:
            pass
        if founder is not None:
            self.plot_founder.clear()
            founder.plot(sub_plot=self.plot_founder)

class RunObject:
    def __init__(self):
        self.run_name = None
        self.num_cpus = None
        self.medium_volume = None
        self.sim_time = None
        self.timestep = None
        self.pop_size = None
        self.iterations = None
        self.output_dir = None
        self.objective = None
        self.culture = None

        self.graph_page = None
        self.process = None

    def start_process(self):
        self.process = Process(target=run_GA, args=(self.culture, self.objective, self.medium_volume, self.output_dir, self.graph_page.queue_fitness, self.graph_page.queue_founder, self, self.num_cpus, self.sim_time, self.timestep, self.pop_size, self.iterations, self.run_name))
        self.process.start()

    def terminate_process(self):
        if self.process is not None:
            self.process.terminate()
            self.process.join()

    def __getstate__(self):
        return (self.run_name, self.num_cpus, self.medium_volume, self.sim_time, self.timestep, self.pop_size, self.iterations, self.output_dir, self.objective, self.culture)

    def __setstate__(self, state):
        self.run_name, self.num_cpus, self.medium_volume, self.sim_time, self.timestep, self.pop_size, self.iterations, self.output_dir, self.objective, self.culture = state

    def update_graphs(self):
        self.graph_page.update_fitness_plot()
        self.graph_page.update_founder_plot()
        print("graphs")


if __name__ == '__main__':
    bg_colour = "#8f9eb7"
    app = Application()
    run = RunObject()
    app.mainloop()