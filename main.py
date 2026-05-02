#!/usr/bin/env python3
import json, os, random, sys, yaml

from render import (
    print_problem,
    prompt_solution,
    print_solution,
    list_problems,
    study_list_problems,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_FILE = os.path.join(SCRIPT_DIR, "problems.yaml")
STUDY_FILE = os.path.join(SCRIPT_DIR, "study_list.json")
CONFIDENCE_FILE = os.path.join(SCRIPT_DIR, "confidence.json")


def load_study_list() -> set:
    if not os.path.exists(STUDY_FILE):
        return set()
    with open(STUDY_FILE) as f:
        return set(json.load(f)["ids"])


def save_study_list(ids: set) -> None:
    with open(STUDY_FILE, "w") as f:
        json.dump({"ids": sorted(ids)}, f)


def load_confidence() -> dict:
    if not os.path.exists(CONFIDENCE_FILE):
        return {}
    with open(CONFIDENCE_FILE) as f:
        return {int(k): v for k, v in json.load(f).items()}


def save_confidence(conf: dict) -> None:
    with open(CONFIDENCE_FILE, "w") as f:
        json.dump({str(k): v for k, v in conf.items()}, f)


def mark_problem(problems, args):
    if len(args) != 2:
        print("Usage: lc mark <id> <0-3>")
        return
    id_token, level_token = args
    if not id_token.isdigit():
        print(f"Not a valid ID: {id_token}")
        return
    if not level_token.isdigit() or int(level_token) not in (0, 1, 2, 3):
        print("Invalid level: must be 0, 1, 2, or 3")
        return
    pid = int(id_token)
    level = int(level_token)
    valid_ids = {p["id"] for p in problems}
    if pid not in valid_ids:
        print(f"Not found in problem set: {pid}")
        return
    conf = load_confidence()
    if level == 0:
        conf.pop(pid, None)
        print(f"Cleared confidence for problem {pid}")
    else:
        conf[pid] = level
        print(f"Marked problem {pid} as level {level}")
    save_confidence(conf)


def add_problems(problems, args):
    valid_ids = {p["id"] for p in problems}
    study_ids = load_study_list()
    added, invalid, unknown = [], [], []
    for token in args:
        if not token.isdigit():
            invalid.append(token)
            continue
        pid = int(token)
        if pid not in valid_ids:
            unknown.append(pid)
        else:
            study_ids.add(pid)
            added.append(pid)
    if not args:
        print("No IDs provided.")
        return
    if added:
        save_study_list(study_ids)
        print(f"Added: {', '.join(str(i) for i in added)}")
    if unknown:
        print(f"Not found in problem set: {', '.join(str(i) for i in unknown)}")
    if invalid:
        print(f"Not valid IDs: {', '.join(invalid)}")


def remove_problems(problems, args):
    study_ids = load_study_list()
    removed, not_found, invalid = [], [], []
    for token in args:
        if not token.isdigit():
            invalid.append(token)
            continue
        pid = int(token)
        if pid in study_ids:
            study_ids.discard(pid)
            removed.append(pid)
        else:
            not_found.append(pid)
    if not args:
        print("No IDs provided.")
        return
    if removed:
        save_study_list(study_ids)
        print(f"Removed: {', '.join(str(i) for i in removed)}")
    if not_found:
        print(f"Not in study list: {', '.join(str(i) for i in not_found)}")
    if invalid:
        print(f"Not valid IDs: {', '.join(invalid)}")


def random_problem(problems, all_problems=False):
    study_ids = load_study_list()
    if all_problems:
        pool = problems
    elif not study_ids:
        print("Study list is empty. Use 'lc add <id>' or 'lc random --all'.")
        sys.exit(1)
    else:
        pool = [p for p in problems if p["id"] in study_ids]
    p = random.choice(pool)
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
    print(
        "Usage: lc [random [--all] | pick <num> | list [--all] | add <id>... | remove <id>... | mark <id> 0-3]"
    )


def main():
    with open(PROBLEMS_FILE) as f:
        problems = yaml.safe_load(f)

    args = sys.argv[1:]

    conf = load_confidence()

    if len(args) == 0:
        print_help()
    elif args[0] == "random" and len(args) == 1:
        random_problem(problems)
    elif args[0] == "random" and len(args) == 2 and args[1] == "--all":
        random_problem(problems, all_problems=True)
    elif args[0] == "pick" and len(args) == 2:
        pick_problem(problems, int(args[1]))
    elif args[0] == "list" and len(args) == 1:
        study_ids = load_study_list()
        study_list_problems(problems, study_ids, conf)
    elif args[0] == "list" and len(args) == 2 and args[1] == "--all":
        list_problems(problems, load_study_list(), conf)
    elif args[0] == "add":
        add_problems(problems, args[1:])
    elif args[0] == "remove":
        remove_problems(problems, args[1:])
    elif args[0] == "mark":
        mark_problem(problems, args[1:])
    else:
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
