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
        self.is_fresh = True

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
        self.is_fresh = False
        self.time += 1
        for i in range(len(fluxes_pandas.index)):
            # print(fluxes_pandas.index[i])
            key = fluxes_pandas.index[i]
            # print(key)
            if key[:3] == "EX_" and not (
                    key == "EX_cpd11416_e0" or key == "EX_cpd11416_c0"):  # EX_cpd11416_c0 is biomass exchange reaction
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

    def get_produced_nutrients(self):
        if self.is_fresh:
            print("Medium was not used yet. Run simulation and try again")
            return
        else:
            products = {}
            for key in self.components_over_time:
                if self.components_over_time[key][-1] > self.components_over_time[key][0]:
                    products[key] = self.components_over_time[key][-1]
            return products

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
        return Medium.from_dict(components, float(volume))

    def __contains__(self, item):
        return item in self.components

    def __len__(self):
        return len(self.components)

    def __getitem__(self, item):
        return self.components[item]


m9_noO2 = {"EX_nh4_e": 18.7,
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
           "EX_h2o_e": 100.0}

m9_O2 = {"EX_nh4_e": 18.7,
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
         "EX_o2_e": 100.0}

m9_O2 = {"EX_cpd00013_e0": 10,
         "EX_cpd00099_e0": 1,
         "EX_cpd00971_e0": 1,
         "EX_cpd00030_e0": 1,
         "EX_cpd00034_e0": 1,
         "EX_cpd00149_e0": 1,
         "EX_cpd00058_e0": 1,
         "EX_cpd00063_e0": 1,
         "EX_cpd00254_e0": 1,
         "EX_cpd00048_e0": 10,
         "EX_cpd10516_e0": 1,
         "EX_cpd10515_e0": 1,
         "EX_cpd00067_e0": 1,
         "EX_cpd00205_e0": 1,
         "EX_cpd11574_e0": 1,
         "EX_cpd00244_e0": 1,
         "EX_cpd00009_e0": 10,
         "EX_cpd00001_e0": 1,
         "EX_cpd00007_e0": 1000,
         "EX_cpd00027_e0": 25
         }

m9_noO2 = {"EX_cpd00013_e0": 10,
           "EX_cpd00099_e0": 10,
           "EX_cpd00971_e0": 10,
           "EX_cpd00030_e0": 10,
           "EX_cpd00034_e0": 10,
           "EX_cpd00149_e0": 10,
           "EX_cpd00058_e0": 10,
           "EX_cpd00063_e0": 10,
           "EX_cpd00254_e0": 10,
           "EX_cpd00048_e0": 10,
           "EX_cpd10516_e0": 10,
           "EX_cpd10515_e0": 10,
           "EX_cpd00067_e0": 10,
           "EX_cpd00205_e0": 10,
           "EX_cpd11574_e0": 10,
           "EX_cpd00244_e0": 10,
           "EX_cpd00009_e0": 10,
           "EX_cpd00001_e0": 10,
           "EX_cpd00027_e0": 10
           }

m9plus = {
    # M9 18
    "EX_cpd00013_e0": 1000,
    "EX_cpd00099_e0": 1000,
    "EX_cpd00971_e0": 1000,
    "EX_cpd00030_e0": 1000,
    "EX_cpd00034_e0": 1000,
    "EX_cpd00149_e0": 1000,
    "EX_cpd00058_e0": 1000,
    "EX_cpd00063_e0": 1000,
    "EX_cpd00254_e0": 1000,
    "EX_cpd00048_e0": 1000,
    "EX_cpd10516_e0": 1000,
    "EX_cpd10515_e0": 1000,
    "EX_cpd00067_e0": 1000,
    "EX_cpd00205_e0": 1000,
    "EX_cpd11574_e0": 1000,
    "EX_cpd00009_e0": 1000,
    "EX_cpd00001_e0": 1000,
    "EX_cpd00007_e0": 1000,
    # Vitamins 9
    "EX_cpd00104_e0": 1000,
    "EX_cpd00016_e0": 1000,
    "EX_cpd00305_e0": 1000,
    "EX_cpd00408_e0": 1000,
    "EX_cpd00133_e0": 1000,
    "EX_cpd00393_e0": 1000,
    "EX_cpd00220_e0": 1000,
    "EX_cpd03424_e0": 1000,
    "EX_cpd00423_e0": 1000,
    # Amino Acids 19
    "EX_cpd00132_e0": 1000,
    "EX_cpd00023_e0": 1000,
    "EX_cpd00053_e0": 1000,
    "EX_cpd00119_e0": 1000,
    "EX_cpd00322_e0": 1000,
    "EX_cpd00107_e0": 1000,
    "EX_cpd00060_e0": 1000,
    "EX_cpd00156_e0": 1000,
    "EX_cpd00054_e0": 1000,
    "EX_cpd00069_e0": 1000,
    'EX_cpd00066_e0': 1000,
    'EX_cpd00051_e0': 1000,
    'EX_cpd00084_e0': 1000,
    'EX_cpd00065_e0': 1000,
    'EX_cpd00161_e0': 1000,
    'EX_cpd00039_e0': 1000,
    'EX_cpd00129_e0': 1000,
    'EX_cpd00035_e0': 1000,
    'EX_cpd00041_e0': 1000
}

lb = {"EX_cpd00001_e0": 1000,
      "EX_cpd00007_e0": 1000,
      "EX_cpd00009_e0": 10,
      "EX_cpd00018_e0": 1,
      "EX_cpd00023_e0": 1,
      "EX_cpd00027_e0": 1,
      "EX_cpd00028_e0": 1,
      "EX_cpd00030_e0": 1,
      "EX_cpd00033_e0": 1,
      "EX_cpd00034_e0": 1,
      "EX_cpd00035_e0": 1,
      "EX_cpd00039_e0": 1,
      "EX_cpd00041_e0": 1,
      "EX_cpd00046_e0": 1,
      "EX_cpd00048_e0": 1,
      "EX_cpd00051_e0": 1,
      "EX_cpd00054_e0": 1,
      "EX_cpd00058_e0": 1,
      "EX_cpd00060_e0": 1,
      "EX_cpd00063_e0": 1,
      "EX_cpd00065_e0": 1,
      "EX_cpd00066_e0": 1,
      "EX_cpd00067_e0": 1,
      "EX_cpd00069_e0": 1,
      "EX_cpd00084_e0": 1,
      "EX_cpd00091_e0": 1,
      "EX_cpd00092_e0": 1,
      "EX_cpd00099_e0": 1,
      "EX_cpd00107_e0": 1,
      "EX_cpd00119_e0": 1,
      "EX_cpd00126_e0": 1,
      "EX_cpd00129_e0": 1,
      "EX_cpd00149_e0": 1,
      "EX_cpd00156_e0": 1,
      "EX_cpd00161_e0": 1,
      "EX_cpd00182_e0": 1,
      "EX_cpd00184_e0": 1,
      "EX_cpd00205_e0": 1,
      "EX_cpd00215_e0": 1,
      "EX_cpd00218_e0": 1,
      "EX_cpd00219_e0": 1,
      "EX_cpd00220_e0": 1,
      "EX_cpd00226_e0": 1,
      "EX_cpd00239_e0": 1,
      "EX_cpd00246_e0": 1,
      "EX_cpd00249_e0": 1,
      "EX_cpd00254_e0": 1,
      "EX_cpd00311_e0": 1,
      "EX_cpd00322_e0": 1,
      "EX_cpd00381_e0": 1,
      "EX_cpd00383_e0": 1,
      "EX_cpd00393_e0": 1,
      "EX_cpd00438_e0": 1,
      "EX_cpd00531_e0": 1,
      "EX_cpd00541_e0": 1,
      "EX_cpd00644_e0": 1,
      "EX_cpd00654_e0": 1,
      "EX_cpd00793_e0": 1,
      "EX_cpd00971_e0": 1,
      "EX_cpd01012_e0": 1,
      "EX_cpd01048_e0": 1,
      "EX_cpd03424_e0": 1,
      "EX_cpd10515_e0": 1,
      "EX_cpd10516_e0": 1,
      "EX_cpd11595_e0": 1,
      "EX_cpd00013_e0": 1
      }

m9_01 = {
    # M9
    "EX_cpd00013_e0": 1000,
    "EX_cpd00099_e0": 1000,
    "EX_cpd00971_e0": 1000,
    "EX_cpd00030_e0": 1000,
    "EX_cpd00034_e0": 1000,
    "EX_cpd00149_e0": 1000,
    "EX_cpd00058_e0": 1000,
    "EX_cpd00063_e0": 1000,
    "EX_cpd00254_e0": 1000,
    "EX_cpd00048_e0": 1000,
    "EX_cpd10516_e0": 1000,
    "EX_cpd10515_e0": 1000,
    "EX_cpd00067_e0": 1000,
    "EX_cpd00205_e0": 1000,
    "EX_cpd11574_e0": 1000,
    "EX_cpd00009_e0": 1000,
    "EX_cpd00001_e0": 1000,
    "EX_cpd00007_e0": 1000,
    # Vitamins
    "EX_cpd00104_e0": 1000,
    "EX_cpd00305_e0": 1000,
    "EX_cpd00644_e0": 1000,
    "EX_cpd00133_e0": 1000,
    "EX_cpd00393_e0": 1000,
    "EX_cpd00220_e0": 1000,
    "EX_cpd00423_e0": 1000,
    # Amino Acids
    "EX_cpd00132_e0": 1000,
    "EX_cpd00107_e0": 1000,
    "EX_cpd00060_e0": 1000,
    "EX_cpd00069_e0": 1000,
    'EX_cpd00066_e0': 1000,
    'EX_cpd00084_e0': 1000,
    'EX_cpd00027_e0': 1000
}

m9_02 = {
    "EX_cpd00013_e0": 10,
    "EX_cpd00099_e0": 1,
    "EX_cpd00971_e0": 1,
    "EX_cpd00030_e0": 1,
    "EX_cpd00034_e0": 1,
    "EX_cpd00149_e0": 1,
    "EX_cpd00058_e0": 1,
    "EX_cpd00063_e0": 1,
    "EX_cpd00254_e0": 1,
    "EX_cpd00048_e0": 10,
    "EX_cpd10516_e0": 1,
    "EX_cpd10515_e0": 1,
    "EX_cpd00067_e0": 1,
    "EX_cpd00205_e0": 1,
    "EX_cpd11574_e0": 1,
    "EX_cpd00009_e0": 10,
    "EX_cpd00001_e0": 1000,
    "EX_cpd00007_e0": 1000,
    # Vitamins
    "EX_cpd00220_e0": 1,
    # Aminoacids
    "EX_cpd00035_e0": 4,
    "EX_cpd00051_e0": 2,
    "EX_cpd00132_e0": 15,
    # Sugars
    "EX_cpd00185_e0": 216
}

m9_03 = {
    "EX_cpd00013_e0": 5,
    "EX_cpd00007_e0": 1000,
    "EX_cpd00048_e0": 5,
    "EX_cpd00205_e0": 1,
    "EX_cpd00034_e0": 1,
    "EX_cpd00099_e0": 1,
    "EX_cpd00063_e0": 1,
    "EX_cpd00058_e0": 1,
    "EX_cpd00149_e0": 1,
    "EX_cpd00305_e0": 1,
    "EX_cpd00254_e0": 1,
    "EX_cpd10516_e0": 1,
    "EX_cpd10515_e0": 1,
    "EX_cpd00009_e0": 3,
    "EX_cpd00030_e0": 1,
    #Aminoacids
    "EX_cpd00084_e0": 3.5,
    "EX_cpd00035_e0": 5,
    "EX_cpd00041_e0": 1,
    #Sugars
    "EX_cpd00076_e0": 10
}

M9_anoxic = StockMedium(m9_noO2)
M9_oxic = StockMedium(m9_O2)
M9_plus = StockMedium(m9plus)
M9_01 = StockMedium(m9_01)
LB = StockMedium(lb)
M9_02 = StockMedium(m9_02)
M9_03 = StockMedium(m9_03)
