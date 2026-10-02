# CLAUDE.md

## Running

```bash
go build -o lc . # build the executable (must live next to problems.yaml and user_data.json)
./lc # show help menu
./lc list # list problems
./lc random # pick a random problem
./lc pick <id> # pick a problem by id
```

## Architecture

This is a terminal flashcard CLI for practicing LeetCode problems, written in Go (the problem solutions themselves are Python, stored in `problems.yaml`). It has three source files:

- **`main.go`** -- entry point; arg parsing and the `random`/`pick`/`list`/`add`/`remove`/`mark` commands
- **`data.go`** -- `Problem` struct, loading `problems.yaml`, and loading/saving `user_data.json` (both resolved relative to the executable)
- **`render.go`** -- all terminal rendering: ANSI color constants, a regex-based Python syntax highlighter (`pythonHighlight`), a lightweight markdown renderer (`printMarkdown`), and `printProblem`/`printSolution`/list printing
- **`problems.yaml`** — problem data; each entry has `id`, `title`, `difficulty`, `tags`, `time`, `space`, `description`, `approach`, `solution`, and `verified` fields

## Adding problems

### Fetching problem data from neetcode.io

Before writing any problem entry, WebFetch the live data from neetcode.io:

    https://neetcode.io/solutions/<slug>

`<slug>` is the problem title lowercased, spaces replaced with hyphens, non-alphanumeric
characters (except hyphens) removed. Examples:
- "Two Sum" → `two-sum`
- "LRU Cache" → `lru-cache`
- "Valid Parentheses" → `valid-parentheses`

From the fetched page, extract:
- Problem title and LeetCode ID
- Difficulty (Easy / Medium / Hard)
- Tags / topic categories
- Full problem description (all examples and constraints)
- "Recommended Time & Space Complexity" for `time` and `space` fields
- The approach explanation (plain text, no code) for `approach`
- The optimal Python solution for `solution`

If the URL returns no useful content, ask the user for the exact neetcode.io URL before
proceeding.

### Schema

Each entry in `problems.yaml` follows this schema:

```yaml
- id: <int>
  title: "<string>"
  difficulty: Easy | Medium | Hard
  tags: [Tag1, Tag2]
  description: |
    <markdown — supports **bold**, `inline code`, Input:/Output:/Explanation: labels, and bullet lists>
  easy_time: "O(...)"
  easy_space: "O(...)"
  easy_approach: |
    <markdown>
  time: "O(...)"
  space: "O(...)"
  description: |
    <markdown — supports **bold**, `inline code`, Input:/Output:/Explanation: labels, and bullet lists>
  approach: |
    <markdown>
  solution: |
    <python code — rendered with syntax highlighting>
  verified: false
```

### Guidelines

Follow these guidelines exactly when adding new problems. If you are unsure, ask for clarification.

- The `id` field must match the title of the LeetCode problem.
- The `title` field must match the title of the LeetCode problem.
- The `difficulty` field must match the difficulty rating (Easy/Medium/Hard) of the LeetCode problem exactly.
- The `description` should be identical to the description of the LeetCode problem with minor tweaks as necessary to ensure the markdown renders properly.
- The `time` and `space` fields are the time complexity and space complexity (respectively) of the optimal solution. Use the "Recommended Time & Space Complexity" fetched live from neetcode.io (per the instructions above) to populate these fields.
- The `approach` is a summary of the approach to a solution. This should not contain code.
- The `solution` should be python code that implements the optimal solution.
- Do not add `easy_time`, `easy_space`, `easy_approach`, and `easy_solution` fields. Those will be manually added and populated later if applicable.
- Each entry in `problems.yaml` should be sorted by `id` with the lowest `id` at the top.
- No duplicate problems are allowed. If you are instructed to add a problem that is already in `problems.yaml`, ask if you can skip it.
- New problems must always have `verified: false`. Only the user sets this to `true` after manually verifying the entry.
