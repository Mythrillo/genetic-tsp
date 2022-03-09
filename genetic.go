package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"os"
	"strconv"
	"strings"

	"gopkg.in/yaml.v3"
)

func load_distances(path string) ([][]int, error) {
	f, err := os.Open(path)

	if err != nil {
		return nil, err
	}

	defer f.Close()

	scanner := bufio.NewScanner(f)
	i := 0
	var distances [][]int
	for scanner.Scan() {
		trimmed := strings.TrimSpace(scanner.Text())
		string_list := strings.Split(trimmed, " ")
		var int_list []int
		for _, j := range string_list {
			j, err := strconv.Atoi(j)
			if err != nil {
				return nil, err
			}
			int_list = append(int_list, j)
		}
		if i != 0 {
			distances = append(distances, int_list)
		}
		i++
	}
	return distances, scanner.Err()
}

func get_random_path(number_of_cities int) []int {
	var path []int
	for i := 0; i < number_of_cities; i++ {
		path = append(path, i)
	}
	shuffle(path, number_of_cities)
	return path
}

func shuffle(path []int, number_of_cities int) {
	// Fisher–Yates shuffle
	for i := 0; i < number_of_cities; i++ {
		r := i + rand.Intn(number_of_cities-i)
		path[r], path[i] = path[i], path[r]
	}
}

func calculate_distance(distances [][]int, path []int, number_of_cities int) int {
	var distance int = 0
	for i := 1; i < number_of_cities; i++ {
		if path[i] > path[i-1] {
			distance += distances[path[i]][path[i-1]]
		} else {
			distance += distances[path[i-1]][path[i]]
		}
	}
	if path[0] > path[number_of_cities-1] {
		distance += distances[path[0]][path[number_of_cities-1]]
	} else {
		distance += distances[path[number_of_cities-1]][path[0]]
	}
	return distance
}

func generate_population(number_of_individuals int, number_of_cities int) [][]int {
	var result [][]int
	for i := 0; i < number_of_individuals; i++ {
		result = append(result, get_random_path(number_of_cities))
	}
	return result
}

func tournament_selection(population [][]int, population_scores []int, population_size int, tournament_size int) ([][]int, []int) {
	var population_after_selection [][]int
	var population_scores_after_selection []int
	for i := 0; i < population_size; i++ {
		chosen_index := rand.Intn(population_size)
		best_individual := population[chosen_index]
		best_score := population_scores[chosen_index]
		for j := 0; j < tournament_size; j++ {
			chosen_index = rand.Intn(population_size)
			if population_scores[chosen_index] < best_score {
				best_score = population_scores[chosen_index]
				best_individual = population[chosen_index]
			}
		}
		population_after_selection = append(population_after_selection, best_individual)
		population_scores_after_selection = append(population_scores_after_selection, best_score)
	}
	return population_after_selection, population_scores_after_selection
}

func main() {

	config_file, err := ioutil.ReadFile("config.yaml")

	if err != nil {
		log.Fatal(err)
	}

	data := make(map[interface{}]interface{})

	err2 := yaml.Unmarshal(config_file, &data)

	if err2 != nil {
		log.Fatal(err)
	}

	distances, err := load_distances(data["filename"].(string))

	if err != nil {
		log.Fatalf("load_distances: %s", err)
	}

	number_of_cities := len(distances)
	population := generate_population(data["population_size"].(int), number_of_cities)
	var population_scores []int
	for _, individual := range population {
		population_scores = append(population_scores, calculate_distance(distances, individual, number_of_cities))
	}
	fmt.Println(population_scores)
	_, new_p_scores := tournament_selection(population, population_scores, data["population_size"].(int), data["tournament_size"].(int))
	var sum_1 int = 0
	var sum_2 int = 0
	for i, sc := range new_p_scores {
		sum_1 += population_scores[i]
		sum_2 += sc
		fmt.Println(sc)
	}
	fmt.Println(sum_1, sum_2)
	// /fmt.Println(new_p_scores)
	//path := get_random_path(number_of_cities)
	//fmt.Println(path)
	//distance := calculate_distance(distances, path, number_of_cities)
	//fmt.Println(distance)
}
