package main

import (
	"fmt"
	"regexp"
	"strings"
)

const (
	Reset  = "\033[0m"
	Bold   = "\033[1m"
	Dim    = "\033[2m"
	Italic = "\033[3m"

	Red     = "\033[31m"
	Green   = "\033[32m"
	Yellow  = "\033[33m"
	Blue    = "\033[34m"
	Magenta = "\033[35m"
	Cyan    = "\033[36m"
	White   = "\033[37m"

	BRed     = "\033[91m"
	BGreen   = "\033[92m"
	BYellow  = "\033[93m"
	BBlue    = "\033[94m"
	BMagenta = "\033[95m"
	BCyan    = "\033[96m"
	BWhite   = "\033[97m"

	BGCode = "\033[48;5;236m"
)

var difficultyColor = map[string]string{"Easy": BGreen, "Medium": BYellow, "Hard": BRed}

func diffColor(d string) string {
	if c, ok := difficultyColor[d]; ok {
		return c
	}
	return White
}

var builtins = []string{
	"print", "len", "range", "enumerate", "zip", "map", "filter", "sorted",
	"list", "dict", "set", "tuple", "int", "str", "float", "bool", "type",
	"None", "True", "False", "self", "cls", "append", "extend", "pop", "get",
	"items", "values", "keys", "heappush", "heappop",
}

var keywords = []string{
	"False", "None", "True", "and", "as", "assert", "async", "await", "break",
	"class", "continue", "def", "del", "elif", "else", "except", "finally",
	"for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
	"not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
}

// Go's RE2 has no lookbehind, so def/class names are matched as plain
// identifiers and classified by looking at the preceding text.
var tok = regexp.MustCompile(`(?s)` +
	`(?P<COMMENT>#[^\n]*)` +
	`|(?P<STRING3D>"""[\s\S]*?"""|'''[\s\S]*?''')` +
	`|(?P<STRING>"[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*')` +
	`|(?P<NUMBER>\b\d+(?:\.\d+)?\b)` +
	`|(?P<KEYWORD>\b(?:` + strings.Join(keywords, "|") + `)\b)` +
	`|(?P<BUILTIN>\b(?:` + strings.Join(builtins, "|") + `)\b)` +
	`|(?P<IDENT>\w+)` +
	`|(?P<OTHER>.)`)

var tokNames = tok.SubexpNames()

var (
	boldRe = regexp.MustCompile(`\*\*(.+?)\*\*`)
	codeRe = regexp.MustCompile("`([^`]+)`")
)

func printMarkdown(text string) {
	for _, line := range strings.Split(text, "\n") {
		stripped := strings.TrimSpace(line)

		line = boldRe.ReplaceAllString(line, Bold+"${1}"+Reset)
		line = codeRe.ReplaceAllString(line, BGCode+" "+Cyan+"${1}"+Reset+BGCode+" "+Reset)

		switch {
		case strings.HasPrefix(stripped, "Input:") || strings.HasPrefix(stripped, "Output:") || strings.HasPrefix(stripped, "Explanation:"):
			key, rest, _ := strings.Cut(stripped, ":")
			fmt.Printf("  %s%s%s:%s%s\n", Bold, BCyan, key, Reset, rest)
		case strings.HasPrefix(stripped, "- "):
			fmt.Printf("  %s•%s %s\n", Cyan, Reset, strings.TrimLeft(line, "- "))
		case strings.HasPrefix(stripped, "**") && strings.HasSuffix(stripped, "**"):
			fmt.Printf("  %s%s%s%s\n", Bold, BWhite, strings.Trim(stripped, "*"), Reset)
		default:
			fmt.Printf("  %s\n", line)
		}
	}
}

func pythonHighlight(code string) string {
	var out strings.Builder
	for _, m := range tok.FindAllStringSubmatchIndex(code, -1) {
		v := code[m[0]:m[1]]
		kind := ""
		for g := 1; g < len(tokNames); g++ {
			if m[2*g] >= 0 {
				kind = tokNames[g]
				break
			}
		}
		switch kind {
		case "COMMENT":
			out.WriteString(Dim + Green + v + Reset)
		case "STRING3D", "STRING":
			out.WriteString(Yellow + v + Reset)
		case "NUMBER":
			out.WriteString(BMagenta + v + Reset)
		case "KEYWORD":
			out.WriteString(Bold + BBlue + v + Reset)
		case "BUILTIN":
			out.WriteString(Cyan + v + Reset)
		case "IDENT":
			switch before := code[:m[0]]; {
			case strings.HasSuffix(before, "def "):
				out.WriteString(Bold + BGreen + v + Reset)
			case strings.HasSuffix(before, "class "):
				out.WriteString(Bold + BYellow + v + Reset)
			default:
				out.WriteString(v)
			}
		default:
			out.WriteString(v)
		}
	}
	return out.String()
}

func printCode(code string) {
	lines := strings.Split(strings.TrimRight(code, " \t\n\r\f\v"), "\n")
	w := len(fmt.Sprint(len(lines)))
	for i, line := range lines {
		fmt.Printf("%s%*d%s %s\n", Dim, w, i+1, Reset, pythonHighlight(line))
	}
}

func printProblem(p Problem) {
	fmt.Printf("\n%s%d. %s%s  [%s%s%s]\n", Bold, p.ID, p.Title, Reset, diffColor(p.Difficulty), p.Difficulty, Reset)
	fmt.Printf("%s%s%s\n\n", Dim, strings.Join(p.Tags, ", "), Reset)
	fmt.Printf("  %s%sDESCRIPTION%s\n\n", Bold, BMagenta, Reset)
	printMarkdown(p.Description)
}

func heading(s string) {
	fmt.Printf("  %s%s%s%s\n\n", Bold, BMagenta, s, Reset)
}

func printSolution(p Problem) {
	verified := ""
	if p.Verified {
		verified = fmt.Sprintf(" [%sVERIFIED%s]", BGreen, Reset)
	}

	if p.EasySolution != "" {
		fmt.Println()
		heading("SUBOPTIMAL APPROACH")
		printMarkdown(p.EasyApproach)

		heading("SUBOPTIMAL COMPLEXITY")
		fmt.Printf("  Time: %s\n", p.EasyTime)
		fmt.Printf("  Space: %s\n", p.EasySpace)

		fmt.Println()
		heading("SUBOPTIMAL_SOLUTION")
		printCode(p.EasySolution)
		fmt.Println()
	}

	fmt.Println()
	heading("APPROACH")
	printMarkdown(p.Approach)

	heading("COMPLEXITY")
	fmt.Printf("  Time: %s\n", p.Time)
	fmt.Printf("  Space: %s\n", p.Space)

	fmt.Println()
	fmt.Printf("  %s%sSOLUTION%s%s\n\n", Bold, BMagenta, Reset, verified)
	printCode(p.Solution)
	fmt.Println()
}

func confidenceMarker(id int, conf map[int]int) string {
	level := conf[id]
	if level == 0 {
		return "   "
	}
	color := Reset
	switch level {
	case 1:
		color = Dim + White
	case 2:
		color = BYellow
	case 3:
		color = BGreen
	}
	return fmt.Sprintf("%s[%d]%s", color, level, Reset)
}

// printRow prints one list row; study is nil for the study-list view.
func printRow(p Problem, width int, conf map[int]int, study map[int]bool) {
	color := diffColor(p.Difficulty)
	level := confidenceMarker(p.ID, conf)
	if study != nil {
		mark := " "
		if study[p.ID] {
			mark = BCyan + "*" + Reset
		}
		fmt.Printf("  %s %s  %s%s%*d%s. %s%s%s\n", mark, level, Bold, Cyan, width, p.ID, Reset, color, p.Title, Reset)
	} else {
		fmt.Printf("  %s  %s%s%*d%s. %s%s%s\n", level, Bold, Cyan, width, p.ID, Reset, color, p.Title, Reset)
	}
}

func maxIDWidth(problems []Problem) int {
	m := 0
	for _, p := range problems {
		if p.ID > m {
			m = p.ID
		}
	}
	return len(fmt.Sprint(m))
}

func listProblems(problems []Problem, study map[int]bool, conf map[int]int) {
	heading("PROBLEMS")
	width := maxIDWidth(problems)
	for _, p := range problems {
		printRow(p, width, conf, study)
	}
}

func studyListProblems(problems []Problem, studyIDs map[int]bool, conf map[int]int) {
	var filtered []Problem
	for _, p := range problems {
		if studyIDs[p.ID] {
			filtered = append(filtered, p)
		}
	}
	if len(filtered) == 0 {
		fmt.Println("  Study list is empty.")
		return
	}
	heading("STUDY LIST")
	width := maxIDWidth(filtered)
	for _, p := range filtered {
		printRow(p, width, conf, nil)
	}
}
