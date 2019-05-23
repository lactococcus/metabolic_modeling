import cobra
from cobra import Reaction, Metabolite, Model
from cobra.flux_analysis import flux_variability_analysis
from cobra.medium import minimal_medium

reactions_table = "U:\Masterarbeit\Media\seed_reactions_corrected.tsv"
metabolites_table = "U:\Masterarbeit\Media\seed_metabolites_edited.tsv"

universal_model = Model('Universal_Model')
universal_model_corrected = Model('Universal_Model_Corrected')

with open(metabolites_table, 'r') as file:
    file.readline()
    for line in file:
        line = line.split('\t')
        ID = line[0]
        name = line[2]
        formula = line[3]
        charge = line[7]
        if formula == 'null':
            formula = 'U'
        #print(ID, name, formula, charge)
        met_e = Metabolite(id=ID+'_e0', name=name, formula=formula, charge=int(charge), compartment='e0')
        met_c = Metabolite(id=ID+'_c0', name=name, formula=formula, charge=int(charge), compartment='c0')
        met_p = Metabolite(id=ID + '_p0', name=name, formula=formula, charge=int(charge), compartment='p0')
        universal_model.add_metabolites([met_e, met_c, met_p])
        universal_model_corrected.add_metabolites([met_e, met_c, met_p])

with open(reactions_table, 'r') as file:
    file.readline()
    to_add = set()
    for i, line in enumerate(file):
        line = line.split('\t')
        ID = line[0]
        name = line[2]
        rev = line[9]
        stoechiometry = line[4].split(';')
        status = line[22]
        lower_bound = -1000.0 if rev != '>' else 0.0
        upper_bound = 1000.0 if rev != '<' else 0.0
        #print(rev, stoechiometry, status, lower_bound, upper_bound)
        reaction = Reaction(id=ID, name=name, lower_bound=lower_bound, upper_bound=upper_bound)
        universal_model.add_reaction(reaction)
        if status == 'approved' or status == 'corrected':
            universal_model_corrected.add_reaction(reaction)
        formula = {}
        for met in stoechiometry:
            met = met.split(':')
            ID = met[1]
            amount = met[0]
            compartment = met[2]
            if compartment == '0':
                compartment = '_c0'
            elif compartment == '2':
                compartment = '_p0'
            else:
                compartment = '_e0'
            formula[ID + compartment] = float(amount)
        try:
            reaction.add_metabolites(formula)
        except KeyError as e:
            to_add.add(str(e))
        if  (i+1)%1000 == 0:
            print(f"{i + 1}/34722")

    for elem in to_add:
        print(elem)

'''
    for met in universal_model.metabolites:
        if met.compartment == 'e0':
            exchange = Reaction(id='EX_' + met.id, name=met.name + ' Exchange', lower_bound=-1000.0, upper_bound=1000.0)
            exchange.add_metabolites({met: -1})
            universal_model.add_reaction(exchange)
    universal_model.add_reaction(model.reactions.get_by_id('bio1'))
'''
#universal_model.objective = model.objective
#universal_model.objective = 'EX_cpd11416_e0'


cobra.io.write_sbml_model(universal_model, "U:\Masterarbeit\Media/universal_model_reactions.xml")
cobra.io.write_sbml_model(universal_model_corrected, "U:\Masterarbeit\Media/universal_model_reactions_corrected.xml")


