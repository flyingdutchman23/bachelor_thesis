using GeneticAlgorithms

println("Hello!")
import SimpleNodeGA
println("Hello!2")

model = runga(SimpleNodeGA; initial_pop_size = 10)

println(population(model))  # the the latest population when the GA exited
