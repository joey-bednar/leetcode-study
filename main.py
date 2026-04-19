#!/usr/bin/env python3
import os, random, sys, yaml

from render import print_problem, prompt_solution, print_solution, list_problems

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_FILE = os.path.join(SCRIPT_DIR, "problems.yaml")


def random_problem(problems):
    p = random.choice(problems)

    print_problem(p)
    prompt_solution()
    print_solution(p)


def pick_problem(problems, problem_id):
    matches = [p for p in problems if p["id"] == problem_id]
    if not matches:
        print(f"No problem found with id {problem_id}")
        sys.exit(1)

    p = matches[0]

    print_problem(p)
    prompt_solution()
    print_solution(p)


def print_help():
    print("Usage: lc [random | pick <num> | list]")


def main():
    with open(PROBLEMS_FILE) as f:
        problems = yaml.safe_load(f)

    args = sys.argv[1:]

    if len(args) == 0:
        print_help()
    elif args[0] == "random" and len(args) == 1:
        random_problem(problems)
    elif args[0] == "pick" and len(args) == 2:
        pick_problem(problems, int(args[1]))
    elif args[0] == "list" and len(args) == 1:
        list_problems(problems)
    else:
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
