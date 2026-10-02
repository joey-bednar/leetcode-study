package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
)

func die(msg string) {
	fmt.Fprintln(os.Stderr, msg)
	os.Exit(1)
}

func isDigits(s string) bool {
	if s == "" {
		return false
	}
	for _, c := range s {
		if c < '0' || c > '9' {
			return false
		}
	}
	return true
}

func joinInts(ids []int) string {
	s := make([]string, len(ids))
	for i, id := range ids {
		s[i] = strconv.Itoa(id)
	}
	return strings.Join(s, ", ")
}

func validIDs(problems []Problem) map[int]bool {
	m := make(map[int]bool, len(problems))
	for _, p := range problems {
		m[p.ID] = true
	}
	return m
}

func cmdAdd(problems []Problem, d *UserData, tokens []string) bool {
	if len(tokens) == 0 {
		fmt.Println("No IDs provided.")
		return false
	}
	valid := validIDs(problems)
	var added, unknown []int
	var invalid []string
	for _, t := range tokens {
		if !isDigits(t) {
			invalid = append(invalid, t)
			continue
		}
		id, _ := strconv.Atoi(t)
		if !valid[id] {
			unknown = append(unknown, id)
		} else {
			d.Study[id] = true
			added = append(added, id)
		}
	}
	if len(added) > 0 {
		fmt.Printf("Added: %s\n", joinInts(added))
	}
	if len(unknown) > 0 {
		fmt.Printf("Not found in problem set: %s\n", joinInts(unknown))
	}
	if len(invalid) > 0 {
		fmt.Printf("Not valid IDs: %s\n", strings.Join(invalid, ", "))
	}
	return len(added) > 0
}

func cmdRemove(d *UserData, tokens []string) bool {
	if len(tokens) == 0 {
		fmt.Println("No IDs provided.")
		return false
	}
	var removed, notFound []int
	var invalid []string
	for _, t := range tokens {
		if !isDigits(t) {
			invalid = append(invalid, t)
			continue
		}
		id, _ := strconv.Atoi(t)
		if d.Study[id] {
			delete(d.Study, id)
			removed = append(removed, id)
		} else {
			notFound = append(notFound, id)
		}
	}
	if len(removed) > 0 {
		fmt.Printf("Removed: %s\n", joinInts(removed))
	}
	if len(notFound) > 0 {
		fmt.Printf("Not in study list: %s\n", joinInts(notFound))
	}
	if len(invalid) > 0 {
		fmt.Printf("Not valid IDs: %s\n", strings.Join(invalid, ", "))
	}
	return len(removed) > 0
}

func cmdMark(problems []Problem, d *UserData, tokens []string) bool {
	if len(tokens) < 2 {
		fmt.Println("Usage: lc mark <id>... <0-3>")
		return false
	}
	idTokens, levelToken := tokens[:len(tokens)-1], tokens[len(tokens)-1]
	if !isDigits(levelToken) || len(levelToken) != 1 || levelToken[0] > '3' {
		fmt.Println("Invalid level: must be 0, 1, 2, or 3")
		return false
	}
	level, _ := strconv.Atoi(levelToken)
	valid := validIDs(problems)
	var marked, cleared, unknown []int
	var invalid []string
	for _, t := range idTokens {
		if !isDigits(t) {
			invalid = append(invalid, t)
			continue
		}
		id, _ := strconv.Atoi(t)
		switch {
		case !valid[id]:
			unknown = append(unknown, id)
		case level == 0:
			delete(d.Conf, id)
			cleared = append(cleared, id)
		default:
			d.Conf[id] = level
			marked = append(marked, id)
		}
	}
	if len(marked) > 0 {
		fmt.Printf("Marked %s as level %d\n", joinInts(marked), level)
	}
	if len(cleared) > 0 {
		fmt.Printf("Cleared confidence for: %s\n", joinInts(cleared))
	}
	if len(unknown) > 0 {
		fmt.Printf("Not found in problem set: %s\n", joinInts(unknown))
	}
	if len(invalid) > 0 {
		fmt.Printf("Not valid IDs: %s\n", strings.Join(invalid, ", "))
	}
	return len(marked) > 0 || len(cleared) > 0
}

func promptSolution() {
	fmt.Printf("\n%s[enter to reveal]%s", Dim, Reset)
	if _, err := bufio.NewReader(os.Stdin).ReadString('\n'); err != nil {
		fmt.Println()
		os.Exit(0)
	}
}

func showProblem(p Problem) {
	printProblem(p)
	promptSolution()
	printSolution(p)
}

func cmdRandom(problems []Problem, d *UserData, conf *int, all bool) {
	var pool []Problem
	for _, p := range problems {
		if all || d.Study[p.ID] {
			pool = append(pool, p)
		}
	}
	if len(pool) == 0 {
		die("Study list is empty. Use 'lc add <id>' or 'lc random --all'.")
	}
	if conf != nil {
		var filtered []Problem
		for _, p := range pool {
			if d.Conf[p.ID] == *conf {
				filtered = append(filtered, p)
			}
		}
		pool = filtered
	}
	if len(pool) == 0 {
		die(fmt.Sprintf("No problems matching --conf %d.", *conf))
	}
	showProblem(pool[rand.Intn(len(pool))])
}

func cmdPick(problems []Problem, idStr string) {
	id, err := strconv.Atoi(idStr)
	if err == nil {
		for _, p := range problems {
			if p.ID == id {
				showProblem(p)
				return
			}
		}
	}
	die(fmt.Sprintf("No problem found with id %s", idStr))
}

func cmdList(problems []Problem, d *UserData, conf *int, all bool) {
	matches := func(id int) bool { return conf == nil || d.Conf[id] == *conf }
	if all {
		var visible []Problem
		for _, p := range problems {
			if matches(p.ID) {
				visible = append(visible, p)
			}
		}
		listProblems(visible, d.Study, d.Conf)
		return
	}
	visible := map[int]bool{}
	for id := range d.Study {
		if matches(id) {
			visible[id] = true
		}
	}
	studyListProblems(problems, visible, d.Conf)
}

func printHelp() {
	fmt.Println("Usage: lc [random [--all] [--conf <0-3>] | pick <num> | list [--all] [--conf <0-3>] | add <id>... | remove <id>... | mark <id>... 0-3]")
}

func main() {
	problems, err := loadProblems()
	if err != nil {
		die(err.Error())
	}
	d, err := loadData()
	if err != nil {
		die(err.Error())
	}

	args := os.Args[1:]
	var conf *int
	for i, a := range args {
		if a != "--conf" {
			continue
		}
		if i+1 >= len(args) || len(args[i+1]) != 1 || args[i+1][0] < '0' || args[i+1][0] > '3' {
			die("Usage: --conf requires a level 0-3")
		}
		v := int(args[i+1][0] - '0')
		conf = &v
		args = append(append([]string{}, args[:i]...), args[i+2:]...)
		break
	}

	save := func(changed bool) {
		if changed {
			if err := d.save(); err != nil {
				die(err.Error())
			}
		}
	}

	switch {
	case len(args) == 1 && args[0] == "random":
		cmdRandom(problems, d, conf, false)
	case len(args) == 2 && args[0] == "random" && args[1] == "--all":
		cmdRandom(problems, d, conf, true)
	case len(args) == 2 && args[0] == "pick" && isDigits(args[1]):
		cmdPick(problems, args[1])
	case len(args) == 1 && args[0] == "list":
		cmdList(problems, d, conf, false)
	case len(args) == 2 && args[0] == "list" && args[1] == "--all":
		cmdList(problems, d, conf, true)
	case len(args) >= 1 && args[0] == "add":
		save(cmdAdd(problems, d, args[1:]))
	case len(args) >= 1 && args[0] == "remove":
		save(cmdRemove(d, args[1:]))
	case len(args) >= 1 && args[0] == "mark":
		save(cmdMark(problems, d, args[1:]))
	default:
		printHelp()
		os.Exit(1)
	}
}
