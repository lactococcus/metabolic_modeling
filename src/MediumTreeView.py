from Medium import Medium
from tkinter.ttk import Treeview, Button, Label, Radiobutton
from CustomEntryWidgets import FloatEntry, StringEntry
from tkinter import Frame, IntVar
from Individual import Individual
import SEEDIDs

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
        self.tree.grid(row=0, column=0, columnspan=3)
        self.run_object = kwargs.pop('run_object', None)

        self.medium = None
        self.medium_volume = None

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
            individual.plot(medium=medium, sub_plot=sub_plot)

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
                self.tree.insert('', i, comp, values=[comp, name, self.medium.get_components()[comp], 1])

    def select_item(self, a):
        try:
            currItem = self.tree.focus()
            string_qu = self.tree.item(currItem)['values'][2]
            include = bool(self.tree.item(currItem)['values'][3])
            self.edit_entry.set(string_qu)
            self.rad_var.set(0 if not include else 1)
        except:
            pass

    def save_changes(self):
        currItem = self.tree.focus()
        ID = self.tree.item(currItem)['values'][0]
        name = self.tree.item(currItem)['values'][1]
        exclude = 1 if self.rad_var.get() == 1 else 0
        self.tree.item(currItem, values=[ID, name, self.edit_entry.get(), exclude])

    def load_medium(self, file):
        medium = Medium.import_medium(file)
        self.add_medium(medium)

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