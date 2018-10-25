import cobra
import Medium
model = cobra.io.read_sbml_model("D:/Uni/Bioinformatik/Masterarbeit/iNF517.xml")

# objective = model.reactions.get_by_id("BIOMASS_LLA_noATPnoH")

# model.objective = objective

model.solver = 'glpk'

min_medium = {"EX_glc__D_e": 1000.0,
              "EX_arg__L_e": 1000.0,
              "EX_cys__L_e": 1000.0,
              "EX_ser__L_e": 1000.0,
              "EX_thr__L_e": 1000.0,
              "EX_leu__L_e": 1000.0,
              "EX_met__L_e": 1000.0,
              "EX_val__L_e": 1000.0,
              "EX_ile__L_e": 1000.0,
              "EX_glu__L_e": 1000.0,
              "EX_thymd_e": 1000.0,
              "EX_fol_e": 1000.0,
              "EX_nac_e": 1000.0,
              "EX_pi_e": 1000.0,
              "EX_pnto__R_e": 1000.0,
              "EX_ura_e": 1000.0,
              "EX_orot_e": 1000.0,
              "EX_o2_e": 1000.0,
              "EX_h2o_e": 1000.0}

min_medium2 = {"EX_2hxic__L_e": 10.0,
               #"EX_acgam_e": 1.0,
               "EX_glc__D_e": 100.0,
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

medium_availability_factor = 1000000
biomass = 1.0
bacterium_size = 1.0
growth_curve = [biomass]
growth_rate = [0.0]

stock = Medium.StockMedium(min_medium2, 1.0)
medium = stock.create_medium(0.04)
'''
file = open("D:/Uni/Bioinformatik/Masterarbeit/EX_lacto.txt", 'w')
for reac in model.reactions:
    if reac.id[:3] == "EX_":
        file.write('"' + reac.id + '" : 0.0,' + "\n")
file.close()
'''

for t in range(1):

    for reaction in model.reactions:
        # print(reaction.id, reaction.bounds)

        if reaction.id[:3] == "EX_":
            reaction.upper_bound = 1000.0
            reaction.lower_bound = -1000.0

            if medium.has_component(reaction.id):
                reaction.lower_bound = -1 * medium.get_component(reaction.id)
            else:
                reaction.lower_bound = 0
            #print(reaction.id, reaction.bounds)

    try:
        solution = model.optimize(objective_sense='maximize', raise_error=True)
    except Exception:
        print(solution.status)
        break

    '''
    for reaction in model.reactions:
        if reaction.id[:3] == "EX_":
            print(reaction.id, reaction.bounds)
    '''

    print(model.summary())

    if solution.status == "optimal":

        biomass = solution.objective_value * biomass + biomass
        growth_curve.append(biomass)
        growth_rate.append(solution.objective_value)
        bacterium_size = biomass % 1 + 1
        '''
        for component in min_medium2:
            if component in solution.fluxes:
                min_medium2[component] = max(min_medium2[component] + solution.fluxes[component] * biomass, 0)
        '''
        medium.update_medium(solution.fluxes)
        medium.print_content()

    else:
        break

file = open("D:/Uni/Bioinformatik/Masterarbeit/growth_lacto.csv", 'w')

for i, g in enumerate(growth_curve):
    file.write(str(i) + ";" + str(round(g, 2)) + ";" + str(growth_rate[i]) + "\n")
file.close()

