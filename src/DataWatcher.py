from copy import deepcopy

class DataWatcher:
    def __init__(self):
        self.data = {"species": {}, "individual": None, "medium": {}}

    def init_data_watcher(self, individual):
        self.init_species(individual.culture.species_list)
        self.init_medium()
        self.init_individual()

    def init_medium(self):
        pass

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

    def create_new_watcher(data_watcher):
        new_watcher = DataWatcher()
        new_watcher.init_individual()
        new_watcher.init_medium()
        new_watcher.data["species"] = deepcopy(data_watcher.data["species"])
        for key in new_watcher.data["species"]:
            new_watcher.data["species"][key][1] = [new_watcher.data["species"][key][0]]
        return new_watcher
