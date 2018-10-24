
class Culture:

    bacteria = []

    def __init__(self, duplication_cutoff=2.0):
        self.duplication_cutoff = duplication_cutoff

    def addBacterium(self, biomass):
        self.bacteria += biomass

    def duplicate(self):

        for bacterium in self.bacteria:
            if bacterium > self.duplication_cutoff:
                self.bacteria.remove(bacterium)
                self.bacteria.append(bacterium / 2)
                self.bacteria.append(bacterium / 2)

    def addBiomass(self, biomass):

        for bacterium in self.bacteria:
            bacterium += biomass

    def bacteriaCount(self):
        return len(self.bacteria)