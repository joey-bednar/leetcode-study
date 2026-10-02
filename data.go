package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"

	"gopkg.in/yaml.v3"
)

type Problem struct {
	ID           int      `yaml:"id"`
	Title        string   `yaml:"title"`
	Difficulty   string   `yaml:"difficulty"`
	Tags         []string `yaml:"tags"`
	Description  string   `yaml:"description"`
	EasyTime     string   `yaml:"easy_time"`
	EasySpace    string   `yaml:"easy_space"`
	EasyApproach string   `yaml:"easy_approach"`
	EasySolution string   `yaml:"easy_solution"`
	Time         string   `yaml:"time"`
	Space        string   `yaml:"space"`
	Approach     string   `yaml:"approach"`
	Solution     string   `yaml:"solution"`
	Verified     bool     `yaml:"verified"`
}

// UserData holds the study list and per-problem confidence levels.
type UserData struct {
	Study map[int]bool
	Conf  map[int]int
}

type rawUserData struct {
	StudyIDs   []int          `json:"study_ids"`
	Confidence map[string]int `json:"confidence"`
}

func baseDir() string {
	exe, err := os.Executable()
	if err != nil {
		return "."
	}
	if resolved, err := filepath.EvalSymlinks(exe); err == nil {
		exe = resolved
	}
	return filepath.Dir(exe)
}

func problemsFile() string { return filepath.Join(baseDir(), "problems.yaml") }
func userDataFile() string { return filepath.Join(baseDir(), "user_data.json") }

func loadProblems() ([]Problem, error) {
	b, err := os.ReadFile(problemsFile())
	if err != nil {
		return nil, err
	}
	var problems []Problem
	if err := yaml.Unmarshal(b, &problems); err != nil {
		return nil, err
	}
	return problems, nil
}

func loadData() (*UserData, error) {
	d := &UserData{Study: map[int]bool{}, Conf: map[int]int{}}
	b, err := os.ReadFile(userDataFile())
	if os.IsNotExist(err) {
		return d, nil
	}
	if err != nil {
		return nil, err
	}
	var raw rawUserData
	if err := json.Unmarshal(b, &raw); err != nil {
		return nil, err
	}
	for _, id := range raw.StudyIDs {
		d.Study[id] = true
	}
	for k, v := range raw.Confidence {
		id, err := strconv.Atoi(k)
		if err != nil {
			return nil, fmt.Errorf("bad confidence id %q", k)
		}
		d.Conf[id] = v
	}
	return d, nil
}

// save writes JSON formatted like Python's json.dump (", " and ": " separators).
func (d *UserData) save() error {
	ids := make([]int, 0, len(d.Study))
	for id := range d.Study {
		ids = append(ids, id)
	}
	sort.Ints(ids)
	cids := make([]int, 0, len(d.Conf))
	for id := range d.Conf {
		cids = append(cids, id)
	}
	sort.Ints(cids)

	var sb strings.Builder
	sb.WriteString(`{"study_ids": [`)
	for i, id := range ids {
		if i > 0 {
			sb.WriteString(", ")
		}
		sb.WriteString(strconv.Itoa(id))
	}
	sb.WriteString(`], "confidence": {`)
	for i, id := range cids {
		if i > 0 {
			sb.WriteString(", ")
		}
		fmt.Fprintf(&sb, `"%d": %d`, id, d.Conf[id])
	}
	sb.WriteString("}}")
	return os.WriteFile(userDataFile(), []byte(sb.String()), 0o644)
}
