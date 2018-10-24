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
        del(self.components[id])


class Medium:

    def __init__(self, stock_medium, volume_in_litre):
        self.stock = stock_medium
        self.volume = volume_in_litre

        self.components = {}

        for component in self.stock.components:
            self.components[component] = self.stock.components[component] * self.volume

    def add_component(self, id, amount, volume_in_litre):
        self.components[id] = amount

    def remove_component(self, id):
        del(self.components[id])

    def update_medium(self, fluxes_dict):

        for key in fluxes_dict:
            if key in self.components:
                self.components[key] = max(self.components[key] + fluxes_dict[key], 0)
            #else:
                #self.components[key] = max(fluxes_dict[key], 0)

    def get_component(self, id):
        return self.components[id]

