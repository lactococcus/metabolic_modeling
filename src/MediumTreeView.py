from Medium import Medium
from tkinter.ttk import Treeview, Button, Label, Radiobutton
from CustomEntryWidgets import FloatEntry
from tkinter import Frame, IntVar
from Individual import Individual

class MediumTreeView(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.tree = Treeview(self)
        self.tree['selectmode'] = "browse"
        self.tree['columns'] = ('Metabolite', 'Gram', 'Include')
        self.tree['height'] = 30
        self.tree['show'] = "headings"
        self.tree.heading('Metabolite', text="Metabolite")
        self.tree.heading('Gram', text="Quantity [mmol]")
        self.tree.heading('Include', text="Include")
        self.tree.column('Metabolite', minwidth=100, width=100)
        self.tree.column('Gram', minwidth=0, width=80)
        self.tree.column('Include', minwidth=50, width=50)
        self.tree.bind('<ButtonRelease-1>', self.select_item)
        self.tree.grid(row=0, column=0, columnspan=3)
        self.run_object = kwargs.pop('run_object', None)

        self.medium = None

        Label(self, text="Quantity:").grid(row=1, column=0)
        self.edit_entry = FloatEntry(self, initial_value='')
        self.edit_entry.grid(row=1, column=1, sticky='w')
        Button(self, text="Save Changes", command=self.save_changes).grid(row=1, column=2, rowspan=2)

        self.rad_var = IntVar()
        self.rad_button_exclude = Radiobutton(self, text="No", variable=self.rad_var, value=0)
        self.rad_button_include = Radiobutton(self, text="Yes", variable=self.rad_var, value=1)
        self.rad_button_include.grid(row=2, column=1, sticky='w')
        self.rad_button_exclude.grid(row=2, column=1, sticky='e')
        Label(self, text="Include:").grid(row=2, column=0)

        Button(self, text="Test Medium", command=self.plot_medium).grid(row=3, column=0)
        Button(self, text="Save Medium", command=self.save_medium).grid(row=3, column=1)

    def plot_medium(self):
        if self.medium is not None:
            components = {}
            children = self.tree.get_children('')
            for child in children:
                child = self.tree.item(child)
                name = child['values'][0]
                quant = float(child['values'][1])
                flag = bool(child['values'][2])
                if flag:
                    components[name] = quant
            medium = Medium.from_dict(components, self.run_object.medium_volume)
            individual = Individual(self.run_object.culture, None, self.run_object.objective, self.run_object.medium_volume, self.run_object.sim_time, self.run_object.timestep, self.run_object.culture.data_watcher)
            individual.plot(medium=medium, sub_plot=self.run_object.graph_page.plot_test_medium)
            self.run_object.graph_page._draw_medium(0)


    def add_medium(self, medium):
        if medium is not None:
            self.medium = medium
            self.update_treeviev()

    def update_treeviev(self):
        if self.medium is not None:
            for i, comp in enumerate(self.medium.get_components()):
                self.tree.insert('', i, comp, values=[comp, self.medium.get_components()[comp], 1])

    def select_item(self, a):
        try:
            currItem = self.tree.focus()
            string_qu = self.tree.item(currItem)['values'][1]
            include = bool(self.tree.item(currItem)['values'][2])
            self.edit_entry.set(string_qu)
            self.rad_var.set(0 if not include else 1)
        except:
            pass

    def save_changes(self):
        currItem = self.tree.focus()
        name = self.tree.item(currItem)['values'][0]
        exclude = 1 if self.rad_var.get() == 1 else 0
        self.tree.item(currItem, values=[name, self.edit_entry.get(), exclude])

    def load_medium(self, file):
        medium = Medium.import_medium(file)
        self.add_medium(medium)

    def save_medium(self):
        if self.medium is not None:
            components = {}
            children = self.tree.get_children('')
            for child in children:
                child = self.tree.item(child)
                name = child['values'][0]
                quant = float(child['values'][1])
                flag = bool(child['values'][2])
                if flag:
                    components[name] = quant
            medium = Medium.from_dict(components, self.run_object.medium_volume)
            Medium.export_medium(medium, "U:/Masterarbeit/GA_Results/final_medium.txt")