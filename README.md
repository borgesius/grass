# 🌱 grass

Paint your GitHub contribution graph with ASCII art.

> **How it works:** GitHub's contribution graph is a 7-row × ~52-column grid. Each cell is one day. `plant.py` maps an ASCII art pattern onto that grid and generates backdated git commits — enough of them to completely dominate the graph regardless of your real activity.

---

## The Grid

```
         oldest week ←————————————————→ newest week
         col 0   col 1   col 2  ...  col 51

row 0    Sun     Sun     Sun    ...   Sun
row 1    Mon     Mon     Mon    ...   Mon
row 2    Tue     Tue     Tue    ...   Tue
row 3    Wed     Wed     Wed    ...   Wed
row 4    Thu     Thu     Thu    ...   Thu
row 5    Fri     Fri     Fri    ...   Fri
row 6    Sat     Sat     Sat    ...   Sat
```

Your pattern file must be **exactly 7 rows tall**. Each column is one week. The rightmost column maps to the current week; it works backward from there.

---

## Intensity Levels (4-shade system)

GitHub's contribution graph has exactly 4 green shades. We map to them precisely:

| Character | Commits/day | GitHub shade |
|-----------|-------------|--------------|
| `#`       | 100         | Darkest green |
| `O`       | 75          | Dark green |
| `o`       | 50          | Medium green |
| `.`       | 25          | Light green |
| ` ` (space) | 0         | Empty (white) |

Since we control the max commits on any day (100), the relative shading is deterministic. This lets you design with actual gradients — drop shadows, depth, 3D effects.

**On an active day you might push 50+ commits.** Use `--intensity 256` for all cells to guarantee the art wins no matter what.

---

## Setup

```bash
git clone https://github.com/borgesius/grass.git
cd grass
```

No dependencies beyond Python 3.9+ and git.

---

## Usage

### Preview (dry run)

```bash
python3 plant.py patterns/heart.txt --dry-run
```

### Plant a pattern

```bash
python3 plant.py patterns/heart.txt
git push
```

GitHub updates the graph within a few minutes.

### Crank the intensity

```bash
python3 plant.py patterns/heart.txt --intensity 256
git push
```

### Reruns are safe (idempotent)

`plant.py` checks existing grass commits per date and only adds the delta. Running it twice does nothing the second time.

### Clear and start over

```bash
python3 plant.py --clear
```

Resets the repo history and force-pushes, preserving your working files. Then replant:

```bash
python3 plant.py patterns/wave.txt --intensity 256
git push
```

### Use a specific repo path

```bash
python3 plant.py patterns/heart.txt --repo /path/to/grass
```

---

## Using This for Your Own Profile

**Don't fork** — you'd inherit all of borgesius's commits and have to clear immediately.

Instead, create a fresh repo and use `--setup` to wire this clone to it:

```bash
# 1. Create a new empty repo on GitHub: github.com/new
#    Name it anything (e.g. "grass"). Do NOT initialize with a README.

# 2. Clone this repo for the scripts
git clone https://github.com/borgesius/grass.git
cd grass

# 3. Point it at your new repo and push just the scripts (no grass commits)
python3 plant.py --setup https://github.com/yourusername/grass.git

# 4. Plant your art
python3 plant.py patterns/heart.txt --intensity 100
git push
```

`--setup` clears any existing grass commits, swaps the remote to your repo, and pushes the scripts. Your clone is now yours — borgesius's commits never touch your profile.

---

## Safety

`plant.py` refuses to run in any directory that doesn't contain a `.grass` marker file. This prevents accidentally running `--clear` in the wrong repo.

---

## Writing Your Own Pattern

Create a `.txt` file with exactly 7 lines using `#`, `O`, `o`, `.`, or spaces:

```
  ###  
 #####
#######
#######
 #####
  ###
   #
```

Regenerate all bundled patterns from source:

```bash
python3 generate_patterns.py
```

---

## Included Patterns

| File | Description |
|------|-------------|
| `patterns/heart.txt` | ❤️ Heart, centered in the year |
| `patterns/gradient.txt` | 🟩 Full-year gradient fade (lightest → darkest) |
| `patterns/wave.txt` | 🌊 Sine wave with shaded depth |
| `patterns/pacman.txt` | 🕹️ Pac-Man with ghost + fading pellets |
| `patterns/cloaked.txt` | 🌲 Cloaked figure crossing a river through a forest |

---

## Notes

- Commits use `--allow-empty` — no file changes needed
- All commits are tagged with `🌱 grass` for easy identification
- Only past dates are committed (future dates skipped automatically)
- The graph shows the last 52 weeks — older patterns won't appear
- `--clear` rewrites history and force-pushes; safe only on this repo (enforced by `.grass`)

---

## License

Do whatever you want with this.
