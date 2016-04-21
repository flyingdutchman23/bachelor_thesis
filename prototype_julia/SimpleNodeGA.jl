module SimpleNodeGA

import Base.isless

using GeneticAlgorithms

rows = 2
columns = 3
max_generation_num = 100

type NodePlacementSolution <: Entity
  grid::BitMatrix
  fitness::Float64

  NodePlacementSolution() = new(BitMatrix(rows,columns), 0.0)
  NodePlacementSolution(grid) = new(grid, 0.0)
end

function create_entity(num)
  # for simplicity sake, let's limit the values for abcde to be
  # integers in [-42, 42]

  NodePlacementSolution(bitrand(rows, columns))
end

function fitness(ent)
  #TODO calculate fitness based on SPNE and data from file

  return 1.0
end

#=function fitness()=#

  #=spne = sum(received_packets)=#
  
  #=nodes = sum(ent.grid)=#
  #=spne /= rows * columns * nodes=#

  #=return spne=#
  
#=end=#


function mutate(ent)
  # let's go crazy and mutate 20% of the time
  rand(Float64) < 0.9 && return

  row = rand(1:rows)
  column = rand(1:columns)
  ent.grid[row, column] = !ent.grid[row, column]
end

function crossover(group)

  println("crossover")
  #assert same lengths for grids, otherwise something must be wrong
  @assert length(group[1].grid) == length(group[2].grid)
  #assert that each group consists of 2 parents
  @assert length(group) == 2
  # grab each element from a random parent

  father = group[1]
  mother = group[2]
  child = NodePlacementSolution(BitMatrix(rows, columns))

  placeOneCrossOver = rand(1:length(child.grid))
  for i = 1:placeOneCrossOver
    child.grid[i] = father.grid[i] 
  end

  for i = placeOneCrossOver:length(child.grid)
    child.grid[i] = mother.grid[i]
  end

  return child
end

function group_entities(pop)

  #stop criteria
  if generation_num() > max_generation_num
    println("Finished!!!!")
    return
  end

  # simple naive groupings that pair the best entitiy with every
  # other
  for i = 1:length(pop)
    produce([1, i])
  end
end

function isless(lhs, rhs)
  println(lhs)
  println(rhs)
end

end
