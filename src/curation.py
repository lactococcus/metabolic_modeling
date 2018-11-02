import cobra
from cobra import Reaction, Metabolite
from cobra.flux_analysis import flux_variability_analysis
from cobra.medium import minimal_medium


model = cobra.io.read_sbml_model("U:\Masterarbeit\Genomes\Lactococcus.GFF___FASTA\Lactococcus.xml")

#for reaction in model.reactions:
    #print(reaction.check_mass_balance())

'''
model.reactions.L_LACD2.lower_bound = 0
model.reactions.L_LACD2.upper_bound = 0
model.reactions.L_LACD3.lower_bound = 0
model.reactions.L_LACD3.upper_bound = 0
'''

reac_lac_transport = Reaction('L_lac')
reac_lac_exchange = Reaction('EX_lac__L_e')
lac__L_e = Metabolite('lac__L_e', formula='C3H5O3', name='L-lactate', compartment='e')

model.add_reactions([reac_lac_exchange, reac_lac_transport])
model.add_metabolites([lac__L_e])

reac_lac_transport.name = 'L-lactate transport'
reac_lac_transport.upper_bound = 1000.0
reac_lac_transport.lower_bound = 0.0

reac_lac_transport.add_metabolites({'lac__L_c': -1.0, 'lac__L_e': 1.0})

reac_lac_exchange.name = 'L-lactate exchange'
reac_lac_exchange.upper_bound = 1000.0
reac_lac_exchange.lower_bound = -1000.0

reac_lac_exchange.add_metabolites({'lac__L_e': -1.0})

for reaction in model.reactions:
    # print(reaction.id, reaction.bounds)
    if reaction.id[:3] == "EX_":
        reaction.upper_bound = 1000.0
        reaction.lower_bound = -1000.0

print(minimal_medium(model,0.001, exports=False, open_exchanges=True))

'''
fva = flux_variability_analysis(model, model.reactions, loopless=True)

file = open("U:\Masterarbeit\Lactococcus\lacto_fva.csv", 'w')

file.write("Name;minimum;maximum\n")

for i in range(len(fva.index)):
    file.write(fva.iloc[i].name + ";" + str(fva.iloc[i]['minimum']) + ";" + str(fva.iloc[i]['maximum']))
    file.write("\n")

file.close()
'''