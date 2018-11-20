import copy
'''
Class for creating a stock solution of a given medium
used to create a working medium
'''
class StockMedium:

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

    def __init__(self, stock_medium, volume_in_litre):
        self.stock = stock_medium
        self.volume = volume_in_litre

        self.components = {}

        if self.stock != None:
            for component in self.stock.components:
                self.components[component] = self.stock.components[component] * self.volume

    def from_dict(components_as_dict, volume_in_litre=1.0):
        medium = Medium(None,volume_in_litre)
        medium.components = components_as_dict
        return medium

    def add_component(self, id, amount, volume_in_litre):
        self.components[id] = amount

    def remove_component(self, id):
        del(self.components[id])

    def update_medium(self, fluxes_pandas):

        for i in range(len(fluxes_pandas.index)):
            #print(fluxes_pandas.index[i])
            key = fluxes_pandas.index[i]

            if key[:3] == "EX_":
                if key in self.components:
                    self.components[key] = max(self.components[key] + fluxes_pandas.iloc[i], 0)
                elif fluxes_pandas.iloc[i] > 0.0:
                    self.components[key] = fluxes_pandas.iloc[i]

    def get_component(self, id):
        if id in self.components:
            return self.components[id]
        else:
            return 0.0

    def print_content(self):
        for component in self.components:
            print(component + ": " + str(round(self.components[component], 3)) + " mmol")
        print()

    def __contains__(self, item):
        return item in self.components



