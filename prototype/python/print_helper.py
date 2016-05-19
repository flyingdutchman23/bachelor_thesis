
### helper module to print specific states and results via normal print on terminal

from config import ROWS, COLS

def individual(individual):

    print("Individual, nodes: ",sum(individual))
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(individual[r * COLS + c])
        print(r,row)

def individual_plotorder(individual):

    print("Individual, nodes: ",sum(individual))
    for r in range(ROWS-1,-1,-1):
        row = list(individual[r*COLS:(r+1)*COLS])
        print(r,row)
