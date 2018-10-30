import cobra
from cobra.exceptions import OptimizationError
import Medium

model = cobra.io.read_sbml_model("U:\Masterarbeit\iNF517.xml")
model2 = cobra.io.read_sbml_model("U:\Masterarbeit\Genomes\Lactococcus.GFF___FASTA\Lactococcus.xml")


# objective = model.reactions.get_by_id("BIOMASS_LLA_noATPnoH")

# model.objective = objective

model.solver = 'cplex'

min_medium = {"EX_glc__D_e": 1000.0,
              "EX_asp__L_e": 1000.0,
              "EX_leu__L_e": 1000.0,
              "EX_met__L_e": 1000.0,
              "EX_val__L_e": 1000.0,
              "EX_ile__L_e": 1000.0,
              "EX_glu__L_e": 1000.0,
              "EX_ac_e": 1000.0,
              "EX_fe2_e": 1000.0,
              "EX_fol_e": 1000.0,
              "EX_nac_e": 1000.0,
              "EX_nmn_e": 1000.0,
              "EX_pi_e": 1000.0,
              "EX_ppi_e": 1000.0,
              "EX_pnto__R_e": 1000.0,
              "EX_ribflv_e": 1000.0,
              "EX_thm_e": 1000.0,
              "EX_ura_e": 1000.0,
              "EX_orot_e": 1000.0,
              "EX_o2_e": 1000.0,
              "EX_h2o_e": 1000.0}

min_medium2 = {"EX_2hxic__L_e": 10.0,
               # "EX_acgam_e": 1.0,
               "EX_glc__D_e": 50.0,
               "EX_cys__L_e": 10.0,
               "EX_glu__L_e": 20.0,
               "EX_met__L_e": 10.0,
               "EX_nmn_e": 10.0,
               "EX_orn__L_e": 10.0,
               "EX_orot_e": 10.0,
               "EX_pnto__R_e": 10.0,
               "EX_ppi_e": 10.0,
               "EX_pro__L_e": 10.0,
               "EX_thm_e": 10.0,
               "EX_thymd_e": 10.0,
               "EX_o2_e": 1000.0,
               "EX_h2o_e": 1000.0}

min_medium3 = {"EX_2mba_e": 1000.0,
               "EX_ade_e": 1000.0,
               "EX_arg__L_e": 1000.0,
               "EX_asn__L_e": 1000.0,
               "EX_asp__L_e": 1000.0,
               "EX_cys__L_e": 1000.0,
               "EX_drib_e": 1000.0,
               "EX_glyc3p_e": 1000.0,
               "EX_glc__D_e": 1000.0,
               "EX_gua_e": 1000.0,
               "EX_h2o_e": 1000.0,
               "EX_h_e": 1000.0,
               "EX_o2_e": 1000.0,
               "EX_his__L_e": 1000.0,
               "EX_lys__L_e": 1000.0,
               "EX_nmn_e": 1000.0,
               "EX_phe__L_e": 1000.0,
               "EX_pnto__R_e": 1000.0,
               "EX_ppi_e": 1000.0,
               "EX_rib__D_e": 1000.0,
               "EX_ser__L_e": 1000.0,
               "EX_thymd_e": 1000.0,
               "EX_trp__L_e": 1000.0,
               "EX_tyr__L_e": 1000.0,
               "EX_ura_e": 1000.0}

biomass = 1.0
dry_weight_g = 0.0000001
growth_curve = [biomass]

stock = Medium.StockMedium(min_medium2, 1.0)
medium = stock.create_medium(0.04)

#flux = None

for t in range(1):

    for reaction in model.reactions:
        # print(reaction.id, reaction.bounds)

        if reaction.id == "O2t":
            reaction.upper_bound = 1000.0
            reaction.lower_bound = -1000.0

        if reaction.id[:3] == "EX_":
            reaction.upper_bound = 1000.0
            reaction.lower_bound = -1000.0

            if medium.has_component(reaction.id):
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

    #flux = solution.fluxes

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
