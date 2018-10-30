import cobra
from cobra import Reaction, Metabolite

model = cobra.io.read_sbml_model("U:\Masterarbeit\Genomes\Lactococcus.GFF___FASTA\Lactococcus.xml")
model2 = cobra.io.read_sbml_model("U:\Masterarbeit\iNF517.xml")

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
reac_lac_exchange.lower_bound = 0.1

reac_lac_exchange.add_metabolites({'lac__L_e': -1.0})

solution = model.optimize()
print(model.summary())