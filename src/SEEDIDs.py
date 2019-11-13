

def init():
    global SEED_to_Names
    SEED_to_Names = {}
    with open("data/seed_metabolites_edited.tsv") as file:
        file.readline()
        for line in file:
            line = line.split('\t')
            SEED_to_Names[line[0]] = line[2]