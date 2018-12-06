import copy
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
            del(self.components[id])

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

    def from_dict(components_as_dict, volume_in_litre):
        """creates a medium from a dictionary containing component names as keys and amounts as values"""
        medium = Medium(None,volume_in_litre)
        medium.components = components_as_dict
        for comp in medium.components:
            medium.components_over_time[comp] = [medium.components[comp]]
        return medium

    def update_medium(self, fluxes_pandas):
        """updates the medium components after doing fba"""
        self.time += 1
        for i in range(len(fluxes_pandas.index)):
            #print(fluxes_pandas.index[i])
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
            del(self.components[component])
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
            print(component + ": " + str(round(self.components[component], 3)) + " mmol")
        print()

    def export_medium(medium, file_path):
        file = open(file_path, 'w')

        for c in medium.components:
            file.write(c + ":" + str(medium.components[c]) + "\n")
        file.close()

    def import_medium(file_path, volume):
        file = open(file_path, 'r')

        components = {}
        for line in file:
            tmp = line.split(":")
            components[tmp[0]] = float(tmp[1])
        file.close()
        return Medium.from_dict(components, volume)

    def __contains__(self, item):
        return item in self.components

    def __len__(self):
        return len(self.components)



