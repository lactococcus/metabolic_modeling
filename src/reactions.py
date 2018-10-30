import cobra

model = cobra.io.read_sbml_model("U:\Masterarbeit\Genomes\Lactococcus.GFF___FASTA\Lactococcus.xml")

file = open("U:\Masterarbeit\Lactococcus\lacto_reactions.csv", 'w')

for reaction in model.reactions:
    file.write(str(reaction.id))
    file.write(";")
    file.write(str(reaction.name))
    file.write(";")
    file.write(str(reaction))
    file.write(";")
    file.write(str(reaction.bounds))
    file.write("\n")

file.close()
