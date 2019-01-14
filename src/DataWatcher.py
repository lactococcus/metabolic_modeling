
class DataWatcher:
    def __init__(self):
        self.data = {"species": {}, "individual": [], "medium": {}}

    def init_data_watcher(self, individual):
        individual.culture.register_data_watcher(self)
        self.init_species(individual.culture.species_list)
        self.init_medium()
        self.init_individual()

    def init_medium(self):
        pass

    def init_species(self, specs):
        for spec in specs:
            self.data["species"][spec.name] = [None, None] # [init_abundance, biomass]

    def init_individual(self):
        self.data["individual"] = [None, None] # [fitness, medium_fitness]