from Medium import Medium
from tkinter.ttk import Treeview, Button, Label, Radiobutton
from CustomEntryWidgets import FloatEntry, StringEntry
from tkinter import Frame, IntVar
from Individual import Individual
import SEEDIDs
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#Widget that displays the contents of the medium and handles edits.
#Also displays a pie chart for medium components selected in the tree view
class MediumTreeView(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.tree = Treeview(self)
        self.tree['selectmode'] = "browse"
        self.tree['columns'] = ('ID', 'Name', 'Gram', 'Include')
        self.tree['height'] = 30
        self.tree['show'] = "headings"
        self.tree.heading('ID', text="ID")
        self.tree.heading('Name', text="Name")
        self.tree.heading('Gram', text="Quantity [mmol]")
        self.tree.heading('Include', text="Include")
        self.tree.column('ID', minwidth=0, width=20)
        self.tree.column('Name', minwidth=100, width=100)
        self.tree.column('Gram', minwidth=0, width=90)
        self.tree.column('Include', minwidth=50, width=50)
        self.tree.bind('<ButtonRelease-1>', self.select_item)
        self.tree.grid(row=0, column=0, columnspan=4)
        self.run_object = kwargs.pop('run_object', None)

        self.medium = None
        self.medium_volume = None
        self.uptake_quantities = {}
        self.species_names = []

        self.pie_figure, self.piechart = plt.subplots()
        self.pie_figure.figsize = (4,4)
        self.piechart.pie([0,0])
        self.canvas = FigureCanvasTkAgg(self.pie_figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=4, padx=10)

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
        Label(self, text="Medium Name:").grid(row=3, column=0)
        self.name_entry = StringEntry(self, initial_value="refined_medium")
        self.name_entry.grid(row=3, column=1, sticky='w')

        Button(self, text="Test Medium", command=parent.plot).grid(row=4, column=1)
        Button(self, text="Save Medium", command=lambda: self.save_medium(parent.save)).grid(row=3, column=2)

    def plot_medium(self, individual, sub_plot):
        #costruct medium from treeviev
        if self.medium is not None:
            components = {}
            children = self.tree.get_children('')
            for child in children:
                child = self.tree.item(child)
                ID = child['values'][0]
                quant = float(child['values'][2])
                flag = bool(child['values'][3])
                if flag:
                    components[ID] = quant
            medium = Medium.from_dict(components, self.medium_volume)

            #simulate medium to get the nutrition uptake for each member of the bacterial community
            individual.plot(True, medium=medium, sub_plot=sub_plot)
            uptakes = individual.get_uptakes()

            #calculate the relative uptake quantities
            self.uptake_quantities = {}
            for child in children:
                child_elements = self.tree.item(child)
                ID = child_elements['values'][0]
                name = child_elements['values'][1]
                quant = float(child_elements['values'][2])
                flag = child_elements['values'][3]

                uptake_per_species = []
                self.species_names = []

                for n, spec in enumerate(uptakes):
                    self.species_names.append(spec)
                    try:
                        uptake = uptakes[spec][ID]
                    except:
                        uptake = 0

                    try:
                        self.uptake_quantities[ID].append(uptake)
                    except:
                        self.uptake_quantities[ID] = [uptake]


            for ID in self.uptake_quantities:
                total = sum(self.uptake_quantities[ID])
                if total == 0:
                    self.uptake_quantities[ID] = [0 for i in self.species_names]
                    print(ID)
                    continue
                relative_quantities = []
                for i in self.uptake_quantities[ID]:
                    relative_quantities.append(i / total)
                self.uptake_quantities[ID] = relative_quantities



    def add_medium(self, medium, medium_volume):
        if medium is not None:
            self.medium = medium
            self.medium_volume = medium_volume
            self.update_treeviev()

    def update_treeviev(self):
        if self.medium is not None:
            for i, comp in enumerate(self.medium.get_components()):
                try:
                    name = SEEDIDs.SEED_to_Names[comp.split("_")[1]]
                except:
                    name = comp
                self.tree.insert('', i, comp, values=[comp, name, self.medium.get_components()[comp], 1, ""])

    def select_item(self, a):
        try:
            currItem = self.tree.focus()
            string_qu = self.tree.item(currItem)['values'][2]
            include = bool(self.tree.item(currItem)['values'][3])
            self.edit_entry.set(string_qu)
            self.rad_var.set(0 if not include else 1)

            self.piechart.clear()
            self.piechart.pie(self.uptake_quantities[self.tree.item(currItem)['values'][0]], labels=self.species_names, labeldistance=None)
            self.piechart.axis('equal')
            self.piechart.legend()
            self.canvas.draw()
        except:
            pass

    def save_changes(self):
        currItem = self.tree.focus()
        ID = self.tree.item(currItem)['values'][0]
        name = self.tree.item(currItem)['values'][1]
        exclude = 1 if self.rad_var.get() == 1 else 0
        uptake = self.tree.item(currItem)['values'][4]
        self.tree.item(currItem, values=[ID, name, self.edit_entry.get(), exclude, uptake])

    def load_medium(self, file):
        medium = Medium.import_medium(file)
        self.add_medium(medium)

    #saves medium to file
    def save_medium(self, path):
        if self.medium is not None:
            file_path = ""
            for x in path.split("/")[:-1]:
                file_path = file_path + x + "/"

            components = {}
            children = self.tree.get_children('')
            for child in children:
                child = self.tree.item(child)
                ID = child['values'][0]
                name = child['values'][1]
                quant = float(child['values'][2])
                flag = bool(child['values'][3])
                if flag:
                    if quant > 0:
                        components[name] = quant
            medium = Medium.from_dict(components, self.medium_volume)
            Medium.export_medium(medium, file_path + "/" + self.name_entry.get() + ".csv")