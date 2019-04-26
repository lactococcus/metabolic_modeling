import cobra
from cobra import Reaction, Metabolite
from cobra.flux_analysis import flux_variability_analysis
from cobra.medium import minimal_medium


#model1 = cobra.io.read_sbml_model("U:\Masterarbeit\Lactococcus/reconstuction/Lactococcus_model2.xml")
#model2 = cobra.io.read_sbml_model("U:\Masterarbeit\Klebsiella/Klebsiella.xml")
#model3 = cobra.io.read_sbml_model("U:\Masterarbeit\Lactococcus\Lactococcus_lactis.xml")
model4 = cobra.io.read_sbml_model("U:\Masterarbeit\Lactococcus\Lactococcus_lactis_subsp_lactis_Il1403_IL1403.xml")
#model5 = cobra.io.read_sbml_model("U:/Masterarbeit/Klebsiella/reconstuction/Klebsiella_model.sbml")

model = model4


#for reaction in model.exchanges:
    #reaction.upper_bound = 1000.0
    #reaction.lower_bound = -1000.0

medium = minimal_medium(model, min_objective_value=10.0,minimize_components=True, exports=False, open_exchanges=True)
model.medium = medium
print(medium)
model.optimize()
print(model.summary())

'''
counter = 0
for reaction in model.reactions:
    balance = reaction.check_mass_balance()
    if len(balance) == 0:
        counter += 1
    print("ID: %s | %s" % (reaction.id, balance))
print("%d/%d | %2.1f%%" % (counter, len(model.reactions), counter/len(model.reactions)*100))
'''
'''
fva = flux_variability_analysis(model, model.reactions, loopless=True)

file = open("U:\Masterarbeit\Klebsiella\kleb_fva.csv", 'w')

file.write("Name;minimum;maximum\n")

for i in range(len(fva.index)):
    file.write(fva.iloc[i].name + ";" + str(fva.iloc[i]['minimum']) + ";" + str(fva.iloc[i]['maximum']))
    file.write("\n")

file.close()
'''