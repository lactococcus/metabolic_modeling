from copy import deepcopy

class DataWatcher:
    def __init__(self):
        """The datawatcher stores information like settings, biomasses and fitness scores of an individual"""
        self.data = {"species": {}, "individual": None, "settings": [None, None, None, 0.0], "crossfeeding": {}}

    def init_data_watcher(self, individual):
        self.init_species(individual.culture.species_list)
        self.init_individual()

    def init_species(self, specs):
        for spec in specs:
            self.data["species"][spec.name] = [None, []] # [init_biomass, biomass]
            self.data["crossfeeding"][spec.name] = [set(), set()] #influxes, outfluxes

    def init_individual(self):
        self.data["individual"] = None #fitness

    def get_crossfeeding(self):
        return self.data["crossfeeding"]

    def add_crossfeed_interaction(self, species_name, nutrient, input):
        direction = 0 if input else 1
        self.data["crossfeeding"][species_name][direction].add(nutrient)

    def get_fitness(self):
        return self.data["individual"]

    def set_fitness(self, fitness):
        self.data["individual"] = fitness

    def get_species(self):
        return self.data["species"]

    def get_biomass(self, spec_name):
        """Biomass in datawatcher is saved in pico gram"""
        return self.data["species"][spec_name][1][-1]

    def set_biomass(self, spec_name, biomass):
        self.data["species"][spec_name][1].append(biomass)

    def get_growth_curve(self, spec_name):
        return self.data["species"][spec_name][1]

    def get_init_biomass(self, spec_name):
        return self.data["species"][spec_name][0]

    def set_init_biomass(self, spec_name, biomass):
        self.data["species"][spec_name][0] = biomass

    def get_oxygen(self):
        return self.data["settings"][1]

    def set_oxygen(self, boolean):
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
            new_watcher.data["crossfeeding"][key] = [set(), set()]
        return new_watcher

    def __del__(self):
        del self.data
        #print("Destroyed DataWatcher")
