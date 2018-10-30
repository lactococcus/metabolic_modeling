import cobra
from cobra.medium import minimal_medium

model = cobra.io.read_sbml_model("U:\Masterarbeit\iNF517.xml")
model.solver = 'cplex'


'''
#file = open("U:\Masterarbeit\min_medium.txt", 'w')

for reaction in model.reactions:
    # print(reaction.id, reaction.bounds)
    if reaction.id[:3] == "EX_":
        reaction.upper_bound = 1000.0
        reaction.lower_bound = -1000.0


print(optlang.statuses)

med = minimal_medium(model, 0.01, minimize_components=True)

print(med)

#file.close()

max_medium = {"EX_2aeppn_e": 0.0,
              "EX_2h3mb_e": 0.0,
              "EX_2h3mp_e": 0.0,
              "EX_2hxic__L_e": 0.0,
              "EX_2mba_e": 0.0,
              "EX_2mbald_e": 0.0,
              "EX_2mpa_e": 0.0,
              "EX_3mba_e": 0.0,
              "EX_3mbal_e": 0.0,
              "EX_4abut_e": 0.0,
              "EX_4abz_e": 0.0,
              "EX_ac_e": 0.0,
              "EX_acald_e": 0.0,
              "EX_acgala_e": 0.0,
              "EX_acgam_e": 0.0,
              "EX_acmana_e": 0.0,
              "EX_actn__R_e": 0.0,
              "EX_ade_e": 0.0,
              "EX_akg_e": 0.0,
              "EX_ala__D_e": 0.0,
              "EX_ala__L_e": 10.0,
              "EX_arg__L_e": 10.0,
              "EX_asn__L_e": 0.0,
              "EX_asp__L_e": 10.0,
              "EX_btd_RR_e": 0.0,
              "EX_bzal_e": 0.0,
              "EX_cellb_e": 0.0,
              "EX_ch4s_e": 0.0,
              "EX_chol_e": 0.0,
              "EX_cit_e": 0.0,
              "EX_co2_e": 0.0,
              "EX_cys__L_e": 10.0,
              "EX_dha_e": 0.0,
              "EX_diact_e": 0.0,
              "EX_drib_e": 0.0,
              "EX_etoh_e": 0.0,
              "EX_fe2_e": 10.0,
              "EX_fe3_e": 10.0,
              "EX_fol_e": 10.0,
              "EX_for_e": 0.0,
              "EX_fru_e": 0.0,
              "EX_gal_e": 0.0,
              "EX_galt_e": 0.0,
              "EX_gcald_e": 0.0,
              "EX_glc__D_e": 100000.0,
              "EX_glcn__D_e": 0.0,
              "EX_gln__L_e": 0.0,
              "EX_glu__L_e": 10.0,
              "EX_gly_e": 0.0,
              "EX_glyb_e": 0.0,
              "EX_glyc3p_e": 0.0,
              "EX_glyc_e": 0.0,
              "EX_gua_e": 0.0,
              "EX_h2o_e": 100000.0,
              "EX_h2s_e": 0.0,
              "EX_h_e": 10000.0,
              "EX_his__L_e": 10.0,
              "EX_hxan_e": 0.0,
              "EX_ile__L_e": 10.0,
              "EX_ins_e": 0.0,
              "EX_lac__L_e": 0.0,
              "EX_lcts_e": 0.0,
              "EX_leu__L_e": 10.0,
              "EX_lys__L_e": 10.0,
              "EX_mal__L_e": 0.0,
              "EX_malt_e": 0.0,
              "EX_man_e": 0.0,
              "EX_met__D_e": 0.0,
              "EX_met__L_e": 10.0,
              "EX_mn2_e": 10.0,
              "EX_mnl_e": 0.0,
              "EX_nac_e": 10.0,
              "EX_nh4_e": 10.0,
              "EX_nmn_e": 0.0,
              "EX_o2_e": 10.0,
              "EX_orn__L_e": 0.0,
              "EX_orot_e": 0.0,
              "EX_pacald_e": 0.0,
              "EX_pea_e": 0.0,
              "EX_phe__L_e": 10.0,
              "EX_pi_e": 10.0,
              "EX_pnto__R_e": 10.0,
              "EX_ppi_e": 0.0,
              "EX_pro__L_e": 0.0,
              "EX_ptrc_e": 0.0,
              "EX_pyr_e": 0.0,
              "EX_rib__D_e": 0.0,
              "EX_ribflv_e": 10.0,
              "EX_sbt__D_e": 0.0,
              "EX_ser__D_e": 0.0,
              "EX_ser__L_e": 10.0,
              "EX_so4_e": 10.0,
              "EX_spmd_e": 0.0,
              "EX_succ_e": 0.0,
              "EX_sucr_e": 0.0,
              "EX_thm_e": 10.0,
              "EX_thr__L_e": 10.0,
              "EX_thymd_e": 0.0,
              "EX_tre_e": 0.0,
              "EX_trp__L_e": 10.0,
              "EX_tyr__L_e": 10.0,
              "EX_ura_e": 10.0,
              "EX_val__L_e": 10.0,
              "EX_xan_e": 0.0,
              "EX_zn2_e": 10.0}
              
'''
