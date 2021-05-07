# Codigo adaptado do Framework Genetic Algorithms
# https://github.com/kiecodes/genetic-algorithms

from collections import Counter
from random import randint, random, choices
from typing import List, Tuple, Callable

# Um genoma representa um cenario de posicionamento das rainhas em um tabuleiro NxN
# Cada valor na lista representa o deslocamento a partir do topo esquerdo [0, 0]
#
# Por exemplo, o cenário
#
#  * Q * *
#  * * * Q
#  * * Q *
#  Q * * *
#
#  seria representado por
#  [3, 0, 2, 1]
#
# Cada valor da lista pode tambem ser representado por um ponto
# P(x, y)
# Onde x é o seu indice na lista e y é o proprio valor
# [3, 0, 2, 1] => {(0, 3), (1, 0), (2, 2), (3, 1)}
Genome = List[int]

# Uma população é representada por uma lista de Genome
Population = List[Genome]

FitnessFunc = Callable[[Genome], int]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PopulateFunc = Callable[[], Population]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]


# Função que recebe um genoma e retorna sua pontuação baseado no total
# de conflitos que ele apresenta, sendo
#
# pontuação = conflitos possiveis - total de conflitos
#
# onde
#
# conflitos possiveis = (N * (N-1)) / 2 | N = numero de rainhas
#
# Para 8 rainhas temos
# (8 * (8 - 1)) / 2 => 28
#
# Assim, um genoma com 0 conflitos terá como pontuação maxima possivel (28 - 0) = 28
def fitness(genome: Genome) -> int:
    # No design utilizado para representar um cenário não é possivel ocorrer
    # conflitos em colunas, apenas em linhas e diagonais

    # Soma de conflitos horizontais
    #
    # Como um genoma representa as aparições de rainhas em cada coluna
    # Se existir um valor repetido, isso indica que existem conflitos horizontal
    #
    # [0, 2, 3, 0] => Q * * Q

    # estrutura para contar aparições dos valores presentes no genoma
    counter = dict(Counter(genome))
    # soma de valores que aparecem mais de uma vez no genoma (conflitos horizontais)
    rows = sum(list(map(lambda x: x - 1 if x > 1 else 0, counter.values())))

    # Soma de conflitos diagonais

    # Para saber se duas rainhas estão na mesma diagonal podemos considerar
    # os valores do genoma como pontos e assim calcular a distancia vertical e horizontal
    # e, se as distancias forem iguais, elas estao na mesma diagonal
    # dx = |x1−x2| dy = |y1−y2|

    size = len(genome)
    diagonals = 0
    for i in range(size - 1):
        for j in range(i + 1, size):
            if abs(i - j) == abs(genome[i] - genome[j]):
                diagonals += 1

    max_fit = int((size * (size - 1)) / 2)
    total = rows + diagonals
    points = max_fit - total
    return points


# Gera uma lista de tamanho [length] com inteiros [0...length-1]
# que representam a disposição de rainhas no tabuleiro
def generate_genome(length: int) -> Genome:
    # return sample(range(0, length), length)
    return [randint(0, length - 1) for _ in range(0, length)]


# Gera uma população com [population_size] individuos, onde cada
# individuo terá o comprimento definido pelo numero [queens] de rainhas
def generate_population(population_size: int, queens: int) -> Population:
    return [generate_genome(queens) for _ in range(population_size)]


# Recebe dois Genome [a] e [b] e faz um cruzamento dos valores
# retornando dois novos Genome filhos formados pela combinação.
# A partição é feita em um indice aleatorio.
def crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]


# Realiza ou não uma mutação em um genoma
#
# 1 - Gera um valor aleatorio
# 2 - Se valor gerado < probabilidade de mutação, altera um valor aleatorio do Genome
# 3 - Retorna genoma
def mutation(genome: Genome, probability: float = 0.5) -> Genome:
    if random() < probability:
        index = randint(0, len(genome) - 1)
        genome[index] = randint(0, len(genome) - 1)
    return genome


# Recebe uma população e uma função de adequação
# e retorna um par de individuos
def selection(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(gene) for gene in population],
        k=2
    )


# Ordena (decrescente) uma população de acordo com a pontuação de cada individuo
def sort_population(population: Population, fitness_func: FitnessFunc) -> Population:
    return sorted(population, key=fitness_func, reverse=True)


# Exibe um tabuleiro de acordo com os dados de um Genome
def show_board(genome: Genome):
    size = len(genome)
    for i in range(size):
        for j in range(size):
            if i == genome[j]:
                print(' Q ', end='')
            else:
                print(' * ', end='')
        print('')


# Algoritimo para posicionar [queens_total] rainhas em um tabuleiro sem
# gerar conflitos entre elas
#
# Executa o processo de evolução, gerando novas populações de tamanho [population_size]
# formadas pelos [survivals] da geração anterior mais novos individuos gerados a partir
# de mutações
#
# Se o limite de gerações [generation_limit] não for definida, o padrão será 100.
# Um valor negativo faz com que ocorram evoluções até encontrar uma população que atinja o objetivo
#
# A função retorna a ultima geração obtida, o numero da geração e dados das gerações passadas
def run_evolution(
        population_size: int,
        queens_total: int,
        generation_limit: int = 100,
        survivals: int = 2,
        single: bool = False,
) -> Tuple[Population, int, List]:
    population = generate_population(population_size, queens_total)
    max_fit = int((queens_total * (queens_total - 1)) / 2)

    plot_data = []

    i = 0
    while i != generation_limit:
        population = sorted(population, key=lambda genome: fitness(genome), reverse=True)

        best_fit = fitness(population[0])
        plot_data.append([i, best_fit == max_fit, population[0], best_fit, f'{(best_fit / max_fit) * 100:.3f}%'])

        if best_fit == max_fit and single:
            break

        next_generation = population[0:survivals]

        for j in range(int(len(population) / 2) - 1):
            parents = selection(population, fitness)
            offspring_a, offspring_b = crossover(parents[0], parents[1])
            offspring_a = mutation(offspring_a)
            offspring_b = mutation(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation
        i += 1

    return population, i, plot_data
