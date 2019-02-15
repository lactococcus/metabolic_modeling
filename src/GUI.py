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
import matplotlib.animation as animation
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
matplotlib.style.use("ggplot")

def _quit():
    app.quit()
    app.destroy()
    exit(0)

def choose_file(entry):
    entry.insert(0, filedialog.askopenfilename())

def choose_directory(entry):
    entry.insert(0, filedialog.askdirectory())

def new_bacteria(parent, controller, parent_page):
    bacteria_page = BacteriaPage(parent, controller, parent_page)
    bacteria_page.grid(row=0, column=0, sticky="nsew")
    bacteria_page.tkraise()

def add_bacterium(parent, controller, bacterium):
    flag = True
    bg_right = "white"
    bg_wrong = "red"

    if bacterium.entry_name.get() == "":
        flag = False
        bacterium.entry_name.config(bg=bg_wrong)
    else:
        bacterium.entry_name.config(bg=bg_right)

    if bacterium.entry_model.get() == "":
        flag = False
        bacterium.entry_model.config(bg=bg_wrong)
    else:
        bacterium.entry_model.config(bg=bg_right)

    try:
        float(bacterium.entry_radius.get())
        bacterium.entry_radius.config(bg=bg_right)
    except ValueError:
        flag = False
        bacterium.entry_radius.config(bg=bg_wrong)

    try:
        float(bacterium.entry_dryweight.get())
        bacterium.entry_dryweight.config(bg=bg_right)
    except ValueError:
        flag = False
        bacterium.entry_dryweight.config(bg=bg_wrong)

    try:
        int(bacterium.entry_innoculation.get())
        bacterium.entry_innoculation.config(bg=bg_right)
    except ValueError:
        flag = False
        bacterium.entry_innoculation.config(bg=bg_wrong)

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

def run_GA(culture, objective, medium_volume, output_dir, queue_fitness, queue_founder,  callback, num_cpus, sim_time, timestep, pop_size, iterations, run_name):
    print("Finding Essential Nutrients...")
    num_essentials, essential_nutrients = GA.find_essential_nutrients(culture.species_list, 1)
    print("Found %d Essential Nutrients!\n" % num_essentials)

    GA.run_GA(culture, objective, medium_volume, output_dir, num_essentials, essential_nutrients, queue_fitness, queue_founder, callback, num_cpus, sim_time, timestep, pop_size, iterations, run_name)

def quit_and_back():
    run.terminate_process()
    app.show_frame(SetupPage)

def start(setup):
    flag = False
    bg_wrong = "red"
    bg_right = "white"

    run.run_name = setup.entry_run_name.get()
    if run.run_name == "":
        flag = True
        setup.entry_run_name.config(bg=bg_wrong)
    else:
        setup.entry_run_name.config(bg=bg_right)

    try:
        run.num_cpus = int(setup.entry_cpus.get())
        setup.entry_cpus.config(bg=bg_right)
    except ValueError:
        flag = True
        setup.entry_cpus.config(bg=bg_wrong)

    try:
        run.medium_volume = float(setup.entry_medium.get())
        setup.entry_medium.config(bg=bg_right)
    except ValueError:
        flag = True
        setup.entry_medium.config(bg=bg_wrong)

    try:
        run.sim_time = int(setup.entry_sim_time.get())
        setup.entry_sim_time.config(bg=bg_right)
    except ValueError:
        flag = True
        setup.entry_sim_time.config(bg=bg_wrong)

    try:
        run.timestep = float(setup.entry_timestep.get())
        setup.entry_timestep.config(bg=bg_right)
    except ValueError:
        flag = True
        setup.entry_timestep.config(bg=bg_wrong)

    try:
        run.pop_size = int(setup.entry_pop_size.get())
        setup.entry_pop_size.config(bg=bg_right)
    except ValueError:
        flag = True
        setup.entry_pop_size.config(bg=bg_wrong)

    try:
        run.iterations = int(setup.entry_iter.get())
        setup.entry_iter.config(bg=bg_right)
    except ValueError:
        flag = True
        setup.entry_iter.config(bg=bg_wrong)

    run.output_dir = setup.entry_output.get()
    if run.output_dir == "":
        flag = True
        setup.entry_output.config(bg=bg_wrong)
    else:
        setup.entry_output.config(bg=bg_right)

    if flag:
        return

    objective = {}
    data_watcher = DataWatcher()
    culture = Culture()
    culture.register_data_watcher(data_watcher)

    if len(setup.widgets) < 2:
        flag = True
        setup.add_bacteria_button.config(bg=bg_wrong)
    else:
        setup.add_bacteria_button.config(bg=bg_colour)

    for widget in setup.widgets:
        try:
            objective[widget.species.entry_name.get()] = float(widget.entry_objective.get())
            widget.entry_objective.config(bg=bg_right)
        except ValueError:
            flag = True
            widget.entry_objective.config(bg=bg_wrong)

        if flag:
            return
        print("Loading Model of Species: %s" % widget.species.entry_name.get())
        species = Species(widget.species.entry_name.get(), widget.species.entry_model.get(), float(widget.species.entry_radius.get()), float(widget.species.entry_dryweight.get()))
        culture.innoculate_species(species, int(widget.species.entry_innoculation.get()))

    run.objective = objective
    run.culture = culture

    if flag:
        return

    app.show_frame(RunPage)

    run.graph_page = app.frames[RunPage]

    run.start_process()


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
        self.logo_image = tk.PhotoImage(file="U:/Bilder/logo.png")
        label = tk.Label(self, image=self.logo_image, bg=bg_colour).grid(row=0, column=0)
        button = tk.Button(self, text="New Run", bg=bg_colour, font="none 18 bold", command=lambda :controller.show_frame(SetupPage)).grid(row=1, column=0)
        button = tk.Button(self, text="Exit", font="none 18 bold", bg=bg_colour, command=_quit).grid(row=2, column=0)

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
        label = tk.Label(self, text="Number of CPUs:", bg=bg_colour).grid(row=990, column=0)
        label = tk.Label(self, text="Medium volume:", bg=bg_colour).grid(row=991, column=0)
        label = tk.Label(self, text="Simulation time:", bg=bg_colour).grid(row=992, column=0)
        label = tk.Label(self, text="Timestep:", bg=bg_colour).grid(row=993, column=0)
        label = tk.Label(self, text="Population size:", bg=bg_colour).grid(row=994, column=0)
        label = tk.Label(self, text="Iterations:", bg=bg_colour).grid(row=995, column=0)
        label = tk.Label(self, text="Output directory:", bg=bg_colour).grid(row=996, column=0)
        start_button = tk.Button(self, text="Start Run", image=self.start_image, bg=bg_colour, command=lambda :start(self), compound="left").grid(row=1000, column=0)
        exit_button = tk.Button(self, text="Exit", command=_quit, bg=bg_colour).grid(row=1000, column=1)
        button = tk.Button(self, text="Test", command=lambda :controller.show_frame(RunPage), bg=bg_colour).grid(row=1000, column=2)

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
        button = tk.Button(self, text="Back", bg=bg_colour, command=lambda :controller.show_frame(SetupPage)).grid(row=100, column=0)

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
        self.plot_fitness = self.fig1.add_subplot(111, xlabel="Iteration", ylabel="Fitness")
        self.fig1.align_labels(self.plot_fitness)
        self.fig2 = Figure(figsize=(4,4), dpi=100)
        self.plot_founder = self.fig2.add_subplot(111, xlabel="Time", ylabel="Abundance")
        self.fig2.align_labels(self.plot_founder)

        self.queue_fitness = Queue(maxsize=2)
        self.queue_founder = Queue(maxsize=2)
        self.fitness = []

        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self)
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas1.get_tk_widget().grid(row=1, column=0, padx=10)
        self.canvas2.get_tk_widget().grid(row=4, column=0, padx=10)

        label = tk.Label(self, text="Fitness", font="none 14 bold", bg=bg_colour).grid(row=0, column=0)
        label = tk.Label(self, text="Current Best:", font="none 14 bold", bg=bg_colour).grid(row=3, column=0)
        button = tk.Button(self, text="Back", bg=bg_colour, command=quit_and_back).grid(row=0, column=1)

        self.anim_fitness = animation.FuncAnimation(self.fig1, self._draw_fitness, interval=1000)
        self.anim_founder = animation.FuncAnimation(self.fig2, self._draw_founder, interval=2000)

        self.text = tk.Text(self, state=tk.DISABLED)
        self.text.grid(row=1, column=2)

    def _draw_fitness(self, i):
        self.canvas1.draw()

    def _draw_founder(self, i):
        self.canvas2.draw()

    def __getstate__(self):
        return (self.plot_fitness, self.plot_founder, self.fig1, self.fig2, self.canvas1, self.canvas2, self.fitness)

    def __setstate__(self, state):
        self.plot_fitness, self.plot_founder, self.fig1, self.fig2, self.canvas1, self.canvas2, self.fitness = state

    def update_fitness_plot(self):
        fit = None
        try:
            fit = self.queue_fitness.get(timeout=0.1)
        except queue.Empty:
            pass
        if fit is not None:
            self.fitness.append(fit)
            self.plot_fitness.clear()
            self.fig1.align_labels(self.plot_fitness)
            self.plot_fitness.plot(range(len(self.fitness)), self.fitness)

    def update_founder_plot(self):
        founder = None
        try:
            founder = self.queue_founder.get(timeout=0.1)
        except queue.Empty:
            pass
        if founder is not None:
            self.plot_founder.clear()
            self.fig2.align_labels(self.plot_founder)
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

        self.flag = False

    def start_process(self):
        self.graph_page.fitness = []
        self.graph_page.plot_fitness.clear()
        self.graph_page.plot_founder.clear()
        self.process = Thread(target=run_GA, args=(self.culture, self.objective, self.medium_volume, self.output_dir, self.graph_page.queue_fitness, self.graph_page.queue_founder, self, self.num_cpus, self.sim_time, self.timestep, self.pop_size, self.iterations, self.run_name))
        self.process.start()

    def terminate_process(self):
        if self.process is not None:
            self.flag = True
            self.process.join()
            print("Tasks terminated")
    '''
    def __getstate__(self):
        return (self.run_name, self.num_cpus, self.medium_volume, self.sim_time, self.timestep, self.pop_size, self.iterations, self.output_dir, self.objective, self.culture)

    def __setstate__(self, state):
        self.run_name, self.num_cpus, self.medium_volume, self.sim_time, self.timestep, self.pop_size, self.iterations, self.output_dir, self.objective, self.culture = state
    '''
    def update_graphs(self):
        self.graph_page.update_fitness_plot()
        self.graph_page.update_founder_plot()

if __name__ == '__main__':
    #bg_colour = "#8f9eb7"
    bg_colour = "#DDDDDD"
    app = Application()
    run = RunObject()
    app.mainloop()