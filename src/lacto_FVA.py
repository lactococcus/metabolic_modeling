from cobra.flux_analysis import *
import cobra
import matplotlib.pyplot as plt

model1 = cobra.io.read_sbml_model("U:\Masterarbeit\Lactococcus\Lactococcus.xml")
model2 = cobra.io.read_sbml_model("U:\Masterarbeit\Klebsiella\Klebsiella.xml")
model3 = cobra.io.read_sbml_model("U:\Masterarbeit\iNF517.xml")

model = model1
model.solver = 'cplex'

def main():
    for reaction in model.exchanges:
        reaction.upper_bound = 1000.0
        reaction.lower_bound = -1000.0

    y_axis = []
    x_axis = []

    ess = find_essential_reactions(model, 0.001)

    for reaction in ess:
        if reaction.id[:3] == "EX_":
            print(reaction.id)

    '''
    for i in range(10):
        print(i)
        x = 1.0/(i+1)
        y = 0
        fva = flux_variability_analysis(model, model.exchanges, fraction_of_optimum=x, loopless=False)
        for i in range(len(fva.index)):
            if fva.iloc[i]['minimum'] + 0.000001 < 0 and fva.iloc[i]['minimum'] + 0.000001 < 0:
                y += 1
        y_axis.append(y)
        x_axis.append(x)
    
    print(len(model.exchanges))
    
    plt.plot(x_axis, y_axis, label='Number of essential reactions')
    plt.legend()
    plt.show()
    '''
    '''
    file = open("U:\Masterarbeit\lacto_fva_o2.csv", 'w')
    
    file.write("Name;minimum;maximum\n")
    
    for i in range(len(fva.index)):
        file.write(fva.iloc[i].name + ";" + str(fva.iloc[i]['minimum']) + ";" + str(fva.iloc[i]['maximum']))
        file.write("\n")
    
    file.close()
    '''

if __name__ == "__main__":
    main()