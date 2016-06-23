
### helper module to print specific states and results via normal print on terminal

import config

def individual(individual):

    print("Individual, nodes: ",sum(individual))
    if config.PLACEMENT_TYPE == config.LIST:
        print(individual)
    else:
        for r in range(config.LENG[config.YAXIS]):
            row = []
            for c in range(config.LENG[config.XAXIS]):
                row.append(individual[r * config.LENG[0] + c])
            print(r,row)

def individual_plotorder(individual):

    print("Individual, nodes: ",sum(individual))
    for r in range(config.LENG[1]-1,-1,-1):
        row = list(individual[r*config.LENG[0]:(r+1)*config.LENG[0]])
        print(r,row)
