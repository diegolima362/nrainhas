import time
from functools import partial

# pip install tabulate
from tabulate import tabulate

import genetic

queens = int(input('Digite o numero n de rainhas: '))

if queens >= 4 and queens <= 25:
    target_value = (queens * (queens - 1)) / 2

    population_size = 50
    generation_limit = 100
    single_answer = True
    survivals_per_gen = 2

    iterations = 1

    plot_data = []

    for i in range(iterations):
        fitness = partial(genetic.fitness)

        start = time.process_time()

        population, generations, data = genetic.run_evolution(
            population_size=population_size,
            queens_total=queens,
            generation_limit=generation_limit,
            survivals=survivals_per_gen,
            single=single_answer
        )
        end = time.time()

        plot_data = data

        print(f'Iteração: {i} | Gerações: {generations} |', end=' ')
        print(f'Tempo: {time.process_time() - start}s')
        print(f'Melhor gene: {population[0]}')
        print(f'Precisão: {(fitness(population[0]) / target_value * 100):.3f} %')
        genetic.show_board(population[0])
        print('- - - - - - - - - - - - - - - - -\n')

    labels = ['Geração', 'Encontrou Solução', 'Melhor Gene', 'Pontos', 'Precisão']
    print(tabulate(plot_data, headers=labels, tablefmt='fancy_grid'))

else:
  print('\nOpcao Invalida.')
