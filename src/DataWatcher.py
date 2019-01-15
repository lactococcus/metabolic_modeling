
class DataWatcher:
    def __init__(self):
        self.data = {"species": {}, "individual": [None, None], "medium": {}}

    def init_data_watcher(self, individual):
        self.init_species(individual.culture.species_list)
        self.init_medium()
        self.init_individual()

    def init_medium(self):
        pass

    def init_species(self, specs):
        for spec in specs:
            self.data["species"][spec.name] = [None, None] # [init_abundance, abundance]

    def init_individual(self):
        self.data["individual"] = [None, None] # [fitness, medium_fitness]

    def get_fitness(self):
        return self.data["individual"][0]

    def set_fitness(self, fitness):
        self.data["individual"][0] = fitness

    def create_new_watcher(data_watcher):
        new_watcher = DataWatcher()
        #new_watcher.init_individual()
        new_watcher.init_medium()
        new_watcher.data["species"] = data_watcher.data["species"]
        for key in new_watcher.data["species"]:
            new_watcher.data["species"][key][1] = new_watcher.data["species"][key][0]
        return new_watcher
