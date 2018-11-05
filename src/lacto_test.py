import cobra
from cobra.exceptions import OptimizationError
import Medium

model = cobra.io.read_sbml_model("U:\Masterarbeit\iNF517.xml")
model2 = cobra.io.read_sbml_model("U:\Masterarbeit\Genomes\Lactococcus.GFF___FASTA\Lactococcus.xml")

# objective = model.reactions.get_by_id("BIOMASS_LLA_noATPnoH")

# model.objective = objective

model.solver = 'cplex'

LB_medium = {"EX_glc__D_e": 1000.0,
             "EX_h2o_e": 1000.0,
             "EX_h_e": 1000.0,
             "EX_leu__L_e": 1000.0,
             "EX_ala__L_e": 1000.0,
             "EX_cl_e": 1000.0,
             "EX_pi_e": 1000.0,
             "EX_adn_e": 1000.0,
             "EX_nh4_e": 1000.0,
             "EX_gly_e": 1000.0,
             "EX_ser__L_e": 1000.0,
             "EX_arg__L_e": 1000.0,
             "EX_fe3_e": 1000.0,
             "EX_lys__L_e": 1000.0,
             "EX_asp__L_e": 1000.0,
             "EX_phe__L_e": 1000.0,
             "EX_k_e": 1000.0,
             "EX_pro__L_e": 1000.0,
             "EX_ca2_e": 1000.0,
             "EX_mg2_e": 1000.0,
             "EX_mn2_e": 1000.0,
             "EX_cobalt2_e": 1000.0,
             "EX_zn2_e": 1000.0,
             "EX_cu2_e": 1000.0,
             "EX_o2_e": 1000.0,
             "EX_glu__L_e": 1000.0,
             "EX_fol_e": 1000.0,
             "EX_gsn_e": 1000.0,
             "EX_h2s_e": 1000.0,
             "EX_his__L_e": 1000.0,
             "EX_hxan_e": 1000.0,
             "EX_ile__L_e": 1000.0,
             "EX_met__L_e": 1000.0,
             "EX_pnto__R_e": 1000.0,
             "EX_so4_e": 1000.0,
             "EX_trp__L_e": 1000.0,
             "EX_tyr__L_e": 1000.0,
             "EX_val__L_e": 1000.0,
             "EX_thm_e": 1000.0}

biomass = 1.0
dry_weight_g = 0.0000001
growth_curve = [biomass]

stock = Medium.StockMedium(LB_medium, 1.0)
medium = stock.create_medium(0.01)

# flux = None

for t in range(1):

    for reaction in model.reactions:
        # print(reaction.id, reaction.bounds)

        if reaction.id == "O2t":
            reaction.upper_bound = 1000.0
            reaction.lower_bound = -1000.0

        if reaction.id[:3] == "EX_":
            reaction.upper_bound = 1000.0
            reaction.lower_bound = -1000.0

            if reaction.id in medium:
                reaction.lower_bound = max(-1 * medium.get_component(reaction.id), -1000.0)
            else:
                reaction.lower_bound = 0.0

            if reaction.id == "EX_o2_e":
                reaction.upper_bound = -1.0

    try:
        solution = model.optimize(objective_sense='maximize', raise_error=True)
    except OptimizationError:
        print("Model infeasible")
        break

    '''
    for reaction in model.reactions:
        if reaction.id[:3] == "EX_":
            print(reaction.id, reaction.bounds)
    '''

    # flux = solution.fluxes

    print(model.summary())

    if solution.status == "optimal":

        biomass = solution.objective_value * biomass + biomass
        growth_curve.append(biomass)
        medium.update_medium(solution.fluxes)
        medium.print_content()

    else:
        break

'''
file = open("U:/Masterarbeit/fluxes_lacto.csv", 'w')

for i, name in enumerate(flux):
    file.write(flux.index[i] + ";" + str(flux.iloc[i]) + "\n")

file.close()
'''
'''
file = open("U:/Masterarbeit/growth_lacto.csv", 'w')

for i, g in enumerate(growth_curve):
    file.write(str(i) + ";" + str(round(g, 2)) + "\n")
file.close()

'''
