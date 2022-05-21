import yaml
import random
import copy



def load_config(path: str) -> dict:
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config

def load_distances(path: str) -> list[list[int]]:
    distances = []
    i = 0
    with open(path) as f:
        for line in f.readlines():
            if i == 0:
                i += 1
                continue
            distances.append([int(x) for x in line.strip().split(" ")])
    for i, row in enumerate(distances):
        for other_row in distances[i+1:]:
            row.append(other_row[i])
    return distances

def get_random_path(size: int) -> list[int]:
    path = [i for i in range(size)]
    random.shuffle(path)
    return path

def calculate_distance(distances: list[list[int]], path: list[int]) -> int:
    distance = 0
    path_length = len(path)
    for i, city in enumerate(path):
        tmp = distances[city][path[(i + 1) % path_length]]
        distance += tmp
    return distance

def generate_population(population_size: int, path_size: int) -> list[list[int]]:
    return [get_random_path(path_size) for _ in range(population_size)]

def tournament_selection(population: list[list[int]], tournament_size: int, distances: list[list[int]]) -> list[list[int]]:
    new_population = []
    while len(new_population) < len(population):
        selected_population = random.choices(population, k=tournament_size)
        new_population.append(get_best_from_population(selected_population, distances))
    return new_population

def get_best_from_population(population: list[list[int]], distances: list[list[int]]) -> list[int]:
    best = None
    best_distance = None
    for path in population:
        if best == None:
            best = path
            best_distance = calculate_distance(distances, path)
        elif calculate_distance(distances, path) < best_distance:
            best = path
            best_distance = calculate_distance(distances, path)
    return best

def pmx_crossover(probability: float, population: list[list[int]]) -> list[list[int]]:
    new_population = []
    for i in range(0, len(population), 2):
        try:
            parent1 = population[i]
            parent2 = population[i + 1]
        except:
            new_population.append(parent1)
            continue
        if random.random() > probability:
            new_population.append(parent1)
            new_population.append(parent2)
            continue
        crossover_point1 = random.randint(0, len(population) - 2)
        crossover_point2 = random.randint(crossover_point1 + 1, len(population) - 1)

        child1 = parent1.copy()
        child2 = parent2.copy()

        for j in range(crossover_point1, crossover_point2):
            child1[j], child2[j] = parent2[j], parent1[j]
        new_population.append(child1)
        new_population.append(child2)
    return new_population

def simple_mutation(probability: float, population: list[list[int]]) -> list[list[int]]:
    for path in population:
        for j in range(len(path)):
            if random.random() < probability:
                other_index = random.choice([i for i in range(len(path)) if i != j])
                path[j], path[other_index] = path[other_index], path[j]
    return population

def swap_mutation(probability: float, population: list[list[int]]) -> list[list[int]]:
    for path in population:
        if random.random() < probability:
            x1 = random.randint(0, len(path) - 2)
            x2 = random.randint(x1, len(path) - 1)
            path[x1:x2] = path[x1:x2][::-1]
    return population

def get_n_best(population: list[list[int]], n: int, distances: list[list[int]]) -> list[list[int]]:
    scores = []
    for path in population:
        scores.append((path, calculate_distance(distances, path)))
    scores.sort(key=lambda x: x[1])
    new_population = []
    for i in range(n):
        new_population.append(scores[i][0])
    return new_population


def partial_replacement_succession(old_population: list[list[int]], new_population: list[list[int]], ratio: float, distances: list[list[int]]) -> list[list[int]]:
    from_new = int(len(new_population) * ratio)
    from_old = len(new_population) - from_new
    return get_n_best(new_population, from_new, distances) + get_n_best(old_population, from_old, distances)

if __name__ == "__main__":
    stagnation_iteration = 0
    try:
        config = load_config("config.yaml")
        distances = load_distances(config["dataset_path"])
        path_size = len(distances)
        population = generate_population(11, path_size)
        crossover_probability = config["crossover_probability"]
        mutation_probability = config["mutation_probability"]
        previous_best_distance = None
        for iteration in range(config["iterations"]):
            if stagnation_iteration >= 1000:
                mutation_probability = random.uniform(0.7, 0.99)
                crossover_probability = random.uniform(0.2, 0.4)
                stagnation_iteration = 0
            old_pop = copy.deepcopy(population)
            population = tournament_selection(population, config["tournament_size"], distances)
            population = pmx_crossover(crossover_probability, population)
            population = swap_mutation(mutation_probability, population)
            population = partial_replacement_succession(old_pop, population, 0.75, distances)
            best_path = get_best_from_population(population, distances)
            best_distance = calculate_distance(distances, best_path)
            if best_distance == previous_best_distance:
                stagnation_iteration += 1
            else:
                previous_best_distance = best_distance
                crossover_probability = config["crossover_probability"]
                mutation_probability = config["mutation_probability"]
                stagnation_iteration = 0
            print(f"Iteration: {iteration}, best distance: {best_distance}")
    except KeyboardInterrupt:
        print(f"Best path found: {best_path}")
        print(f"The distance was: {best_distance}")
        print(len(best_path))
