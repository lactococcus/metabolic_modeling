from copy import deepcopy

class DataWatcher:
    def __init__(self):
        self.data = {"species": {}, "individual": None, "settings": [None, None, None, 0.0]}

    def init_data_watcher(self, individual):
        self.init_species(individual.culture.species_list)
        self.init_individual()

    def init_species(self, specs):
        for spec in specs:
            self.data["species"][spec.name] = [None, []] # [init_abundance, abundance]

    def init_individual(self):
        self.data["individual"] = None #fitness

    def get_fitness(self):
        return self.data["individual"]

    def set_fitness(self, fitness):
        self.data["individual"] = fitness

    def get_species(self):
        return self.data["species"]

    def get_abundance(self, spec_name):
        return self.data["species"][spec_name][1][-1]

    def set_abundance(self, spec_name, abundance):
        self.data["species"][spec_name][1].append(abundance)

    def get_growth_curve(self, spec_name):
        return self.data["species"][spec_name][1]

    def get_init_abundance(self, spec_name):
        return self.data["species"][spec_name][0]

    def set_init_abundance(self, spec_name, abundance):
        self.data["species"][spec_name][0] = abundance

    def get_oxigen(self):
        return self.data["settings"][1]

    def set_oxigen(self, boolean):
        self.data["settings"][1] = boolean

    def get_enforce_growth(self):
        return self.data["settings"][0]

    def set_enforce_growth(self, boolean):
        self.data["settings"][0] = boolean

    def get_pfba(self):
        return self.data["settings"][2]

    def set_pfba(self, boolean):
        self.data["settings"][2] = boolean

    def get_death_rate(self):
        return self.data["settings"][3]

    def set_death_rate(self, boolean):
        self.data["settings"][3] = boolean

    def create_new_watcher(data_watcher):
        new_watcher = DataWatcher()
        #new_watcher.init_individual()
        new_watcher.data["species"] = deepcopy(data_watcher.data["species"])
        new_watcher.data["settings"] = deepcopy(data_watcher.data["settings"])
        for key in new_watcher.data["species"]:
            new_watcher.data["species"][key][1] = [new_watcher.data["species"][key][0]]
        return new_watcher

    def __del__(self):
        del self.data
        #print("Destroyed DataWatcher")
