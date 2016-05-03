
### helper module to print specific states and results via normal print on terminal

def individual(individual):

    print("Individual")
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(individual[r * COLS + c])
        print(r,row)

