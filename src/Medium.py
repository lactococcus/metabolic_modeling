from copy import deepcopy
import matplotlib.pyplot as plt


class StockMedium:
    """ Class for creating a stock solution of a given medium used to create a working medium """

    def __init__(self, medium_as_dict={}, volume_in_litre=1.0):
        self.components = medium_as_dict
        self.volume = volume_in_litre

        if self.volume != 1.0:
            for component in self.components:
                self.components[component] = self.components[component] * self.volume

    def add_component(self, id, amount, volume_in_litre):
        self.components[id] = amount / volume_in_litre

    def remove_component(self, id):
        if id in self.components:
            del (self.components[id])

    def create_medium(self, volume_in_litre):
        return Medium(self, volume_in_litre)


class Medium:
    """ Class for creating a working medium """

    def __init__(self, stock_medium, volume_in_litre):
        self.stock = stock_medium
        self.volume = volume_in_litre

        self.components = {}
        self.components_over_time = {}
        self.time = 0

        if self.stock != None:
            for component in self.stock.components:
                self.components[component] = self.stock.components[component] * self.volume
                self.components_over_time[component] = [self.stock.components[component] * self.volume]

    def copy(self):
        medium = Medium(None, 0.0)
        medium.stock = self.stock
        medium.volume = self.volume
        medium.components = deepcopy(self.components)
        medium.components_over_time = deepcopy(self.components_over_time)
        medium.time = deepcopy(self.time)
        return medium

    def from_dict(components_as_dict, volume_in_litre):
        """creates a medium from a dictionary containing component names as keys and amounts as values"""
        medium = Medium(None, volume_in_litre)
        medium.components = components_as_dict
        for comp in medium.components:
            medium.components_over_time[comp] = [medium.components[comp]]
        return medium

    def update_medium(self, fluxes_pandas):
        """updates the medium components after doing fba"""
        self.time += 1
        for i in range(len(fluxes_pandas.index)):
            # print(fluxes_pandas.index[i])
            key = fluxes_pandas.index[i]

            if key[:3] == "EX_":
                if key in self.components:
                    self.components[key] = max(self.components[key] + fluxes_pandas.iloc[i], 0)
                    self.components_over_time[key].append(self.components[key])
                elif fluxes_pandas.iloc[i] > 0.0:
                    self.components[key] = fluxes_pandas.iloc[i]
                    self.components_over_time[key] = []
                    for i in range(self.time):
                        self.components_over_time[key].append(0)
                    self.components_over_time[key].append(self.components[key])

    def remove_component(self, component):
        if component in self.components:
            del (self.components[component])
            del (self.components_over_time[component])
            return True
        else:
            return False

    def get_component(self, id):
        if id in self.components:
            return self.components[id]
        else:
            return 0.0

    def get_components(self):
        return self.components

    def plot_nutrients_over_time(self):
        for key in self.components_over_time:
            plt.plot(self.components_over_time[key], label=key)
        plt.legend()
        plt.show()

    def print_content(self):
        for component in self.components:
            print("%s: %f mmol" % (component, self.components[component]))
        print()

    def export_medium(medium, file_path):
        file = open(file_path, 'w')
        file.write("volume;%f\n" % medium.volume)
        for c in medium.components:
            file.write("%s;%f\n" % (c, medium.components[c]))
        file.close()

    def import_medium(file_path):
        file = open(file_path, 'r')
        volume = file.readline()
        volume = volume.split(';')[1]
        components = {}
        for line in file:
            tmp = line.split(";")
            components[tmp[0]] = float(tmp[1])
        file.close()
        return Medium.from_dict(components, volume)

    def __contains__(self, item):
        return item in self.components

    def __len__(self):
        return len(self.components)


m9_anoxic = {"EX_nh4_e": 18.7,
             "EX_cl_e": 10.0,
             "EX_na1_e": 10.0,
             "EX_mn2_e": 0.005,
             "EX_zn2_e": 0.0125,
             "EX_cobalt2_e": 0.0025,
             "EX_cu2_e": 0.0025,
             "EX_ca2_e": 0.01,
             "EX_mg2_e": 1.0,
             "EX_so4_e": 1.0,
             "EX_fe3_e": 0.005,
             "EX_fe2_e": 0.005,
             "EX_h_e": 100.0,
             "EX_k_e": 100.0,
             "EX_mobd_e": 0.0025,
             "EX_ni2_e": 0.0,
             "EX_pi_e": 10.0,
             "EX_glc__D_e": 16.65,
             "EX_h2o_e": 1000.0}

m9_oxic = {"EX_nh4_e": 18.7,
           "EX_cl_e": 10.0,
           "EX_na1_e": 10.0,
           "EX_mn2_e": 0.005,
           "EX_zn2_e": 0.0125,
           "EX_cobalt2_e": 0.0025,
           "EX_cu2_e": 0.0025,
           "EX_ca2_e": 0.01,
           "EX_mg2_e": 1.0,
           "EX_so4_e": 1.0,
           "EX_fe3_e": 0.005,
           "EX_fe2_e": 0.005,
           "EX_h_e": 100.0,
           "EX_k_e": 100.0,
           "EX_mobd_e": 0.0025,
           "EX_ni2_e": 0.0,
           "EX_pi_e": 10.0,
           "EX_glc__D_e": 16.65,
           "EX_h2o_e": 1000.0,
           "EX_o2_e": 1000.0}

M9_anoxic = StockMedium(m9_anoxic)
M9_oxic = StockMedium(m9_oxic)
