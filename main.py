#!/usr/bin/env python3
import json, os, random, sys, yaml

from render import list_problems, print_problem, print_solution, prompt_solution, study_list_problems

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_FILE = os.path.join(SCRIPT_DIR, "problems.yaml")
USER_DATA_FILE = os.path.join(SCRIPT_DIR, "user_data.json")


def load_data() -> tuple[set, dict]:
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE) as f:
            raw = json.load(f)
    return set(raw["study_ids"]), {int(k): v for k, v in raw["confidence"].items()}


def save_data(study: set, conf: dict) -> None:
    with open(USER_DATA_FILE, "w") as f:
        json.dump({"study_ids": sorted(study), "confidence": {str(k): v for k, v in conf.items()}}, f)

def cmd_add(problems, study: set, tokens: list) -> bool:
    if not tokens:
        print("No IDs provided.")
        return False
    valid_ids = {p["id"] for p in problems}
    added, unknown, invalid = [], [], []
    for token in tokens:
        if not token.isdigit():
            invalid.append(token)
        elif (pid := int(token)) not in valid_ids:
            unknown.append(pid)
        else:
            study.add(pid)
            added.append(pid)
    if added:
        print(f"Added: {', '.join(str(i) for i in added)}")
    if unknown:
        print(f"Not found in problem set: {', '.join(str(i) for i in unknown)}")
    if invalid:
        print(f"Not valid IDs: {', '.join(invalid)}")
    return bool(added)


def cmd_remove(study: set, tokens: list) -> bool:
    if not tokens:
        print("No IDs provided.")
        return False
    removed, not_found, invalid = [], [], []
    for token in tokens:
        if not token.isdigit():
            invalid.append(token)
        elif (pid := int(token)) in study:
            study.discard(pid)
            removed.append(pid)
        else:
            not_found.append(pid)
    if removed:
        print(f"Removed: {', '.join(str(i) for i in removed)}")
    if not_found:
        print(f"Not in study list: {', '.join(str(i) for i in not_found)}")
    if invalid:
        print(f"Not valid IDs: {', '.join(invalid)}")
    return bool(removed)


def cmd_mark(problems, conf: dict, tokens: list) -> bool:
    if len(tokens) < 2:
        print("Usage: lc mark <id>... <0-3>")
        return False
    *id_tokens, level_token = tokens
    if not level_token.isdigit() or int(level_token) not in range(4):
        print("Invalid level: must be 0, 1, 2, or 3")
        return False
    level = int(level_token)
    valid_ids = {p["id"] for p in problems}
    marked, cleared, unknown, invalid = [], [], [], []
    for token in id_tokens:
        if not token.isdigit():
            invalid.append(token)
        elif (pid := int(token)) not in valid_ids:
            unknown.append(pid)
        elif level == 0:
            conf.pop(pid, None)
            cleared.append(pid)
        else:
            conf[pid] = level
            marked.append(pid)
    if marked:
        print(f"Marked {', '.join(str(i) for i in marked)} as level {level}")
    if cleared:
        print(f"Cleared confidence for: {', '.join(str(i) for i in cleared)}")
    if unknown:
        print(f"Not found in problem set: {', '.join(str(i) for i in unknown)}")
    if invalid:
        print(f"Not valid IDs: {', '.join(invalid)}")
    return bool(marked or cleared)


def cmd_random(problems, study: set, conf: dict, conf_filter=None, all_problems=False):
    pool = problems if all_problems else [p for p in problems if p["id"] in study]
    if not pool:
        sys.exit("Study list is empty. Use 'lc add <id>' or 'lc random --all'.")
    if conf_filter is not None:
        pool = [p for p in pool if conf.get(p["id"], 0) == conf_filter]
    if not pool:
        sys.exit(f"No problems matching --conf {conf_filter}.")
    p = random.choice(pool)
    print_problem(p)
    prompt_solution()
    print_solution(p)


def cmd_pick(problems, id_str: str):
    matches = [p for p in problems if p["id"] == int(id_str)]
    if not matches:
        sys.exit(f"No problem found with id {id_str}")
    p = matches[0]
    print_problem(p)
    prompt_solution()
    print_solution(p)


def cmd_list(problems, study: set, conf: dict, conf_filter=None, all_problems=False):
    if all_problems:
        visible = [p for p in problems if conf_filter is None or conf.get(p["id"], 0) == conf_filter]
        list_problems(visible, study, conf)
    else:
        visible_study = {pid for pid in study if conf_filter is None or conf.get(pid, 0) == conf_filter}
        study_list_problems(problems, visible_study, conf)


def print_help():
    print("Usage: lc [random [--all] [--conf <0-3>] | pick <num> | list [--all] [--conf <0-3>] | add <id>... | remove <id>... | mark <id>... 0-3]")


def main():
    with open(PROBLEMS_FILE) as f:
        problems = yaml.safe_load(f)

    args = sys.argv[1:]
    study, conf = load_data()

    conf_filter = None
    if "--conf" in args:
        idx = args.index("--conf")
        if idx + 1 >= len(args) or not args[idx + 1].isdigit() or int(args[idx + 1]) not in range(4):
            sys.exit("Usage: --conf requires a level 0-3")
        conf_filter = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    match args:
        case ["random"]:
            cmd_random(problems, study, conf, conf_filter)
        case ["random", "--all"]:
            cmd_random(problems, study, conf, conf_filter, all_problems=True)
        case ["pick", id_str] if id_str.isdigit():
            cmd_pick(problems, id_str)
        case ["list"]:
            cmd_list(problems, study, conf, conf_filter)
        case ["list", "--all"]:
            cmd_list(problems, study, conf, conf_filter, all_problems=True)
        case ["add", *tokens]:
            if cmd_add(problems, study, tokens):
                save_data(study, conf)
        case ["remove", *tokens]:
            if cmd_remove(study, tokens):
                save_data(study, conf)
        case ["mark", *tokens]:
            if cmd_mark(problems, conf, tokens):
                save_data(study, conf)
        case _:
            print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
