import cobra

model = cobra.io.read_sbml_model("U:\Masterarbeit\Lactococcus\Lactococcus.xml")
model.solver = 'cplex'



file = open("U:\Masterarbeit\Lactococcus\lacto_metabolites.txt", 'w')

met = []

for metabolite in model.metabolites:
    met.append((metabolite.id, metabolite.name))

met.sort(key=lambda tup: tup[0])

for metabolite in met:
    file.write(metabolite[0] + " = " + metabolite[1] + "\n")

file.close()

