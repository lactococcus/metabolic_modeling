from cobra.flux_analysis import flux_variability_analysis
import cobra

model = cobra.io.read_sbml_model("U:\Masterarbeit\iNF517.xml")
model.solver = 'cplex'


for reaction in model.reactions:
    # print(reaction.id, reaction.bounds)
    if reaction.id[:3] == "EX_":
        reaction.upper_bound = 1000.0
        reaction.lower_bound = -1000.0


fva = flux_variability_analysis(model, model.reactions, loopless=True)

file = open("U:\Masterarbeit\lacto_fva_o2.csv", 'w')

file.write("Name;minimum;maximum\n")

for i in range(len(fva.index)):
    file.write(fva.iloc[i].name + ";" + str(fva.iloc[i]['minimum']) + ";" + str(fva.iloc[i]['maximum']))
    file.write("\n")

file.close()
