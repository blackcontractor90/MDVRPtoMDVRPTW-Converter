# MDVRP → MDVRPTW Converter

A lightweight Python script that converts **Cordeau-format MDVRP (type 2)** instance files into **MDVRPTW (type 6)** format, following the conventional benchmark standards used in Cordeau et al. (2001).

No external dependencies — runs on standard Python 3.

---

## Background

The **Multi-Depot Vehicle Routing Problem with Time Windows (MDVRPTW)** extends the MDVRP by adding:
- A **time window** `[e, l]` per customer — the earliest and latest time service may begin
- A **service duration** `d` per customer — time spent at each stop

This script synthesises those fields from your existing MDVRP geometry using the conventions established in Cordeau's benchmark instances:
- Travel time = Euclidean distance (vehicle speed = 1)
- Time windows centred on the nearest-depot travel time ± a configurable half-width
- Planning horizon `T_max` auto-computed or set manually

---

## File Format

Both input and output follow the **Cordeau unified format**, described at [neo.lcc.uma.es](https://neo.lcc.uma.es/vrp/vrp-instances/description-for-files-of-cordeaus-instances/).

### Header line
```
type  m  n  t
```
| Field | Meaning |
|---|---|
| `type` | Problem type — `2` = MDVRP, `6` = MDVRPTW |
| `m` | Number of vehicles |
| `n` | Number of customers |
| `t` | Number of depots |

### Depot capacity lines (`t` lines)
```
D  Q
```
| Field | Meaning |
|---|---|
| `D` | Maximum route duration |
| `Q` | Maximum vehicle load |

### Node lines (customers, then depots)
```
i  x  y  d  q  f  a  list  e  l
```
| Field | Meaning |
|---|---|
| `i` | Node ID |
| `x`, `y` | Coordinates |
| `d` | Service duration |
| `q` | Demand |
| `f` | Visit frequency |
| `a` | Number of visit combinations |
| `list` | Visit combination code |
| `e` | Earliest service time (time window open) |
| `l` | Latest service time (time window close) |

---

## Installation

No installation required. Clone the repo and run the script directly with Python 3.

```bash
git clone https://github.com/your-username/mdvrp-to-mdvrptw.git
cd mdvrp-to-mdvrptw
```

If you are using Anaconda, any standard environment works:

```bash
conda activate your-env
python mdvrp_to_mdvrptw.py p02
```

---

## Usage

```bash
python mdvrp_to_mdvrptw.py <input_file> [options]
```

The input file can be an absolute or relative path — it does not need to be in the same directory as the script.

### Options

| Flag | Default | Description |
|---|---|---|
| `-o`, `--output` | `<input>_mdvrptw.txt` | Output file path |
| `--service-time` | `10` | Service duration assigned to every customer node |
| `--tmax` | auto | Planning horizon. Auto = `ceil(max_nearest_tt × 3)` |
| `--style` | `wide` | Time window style: `wide`, `narrow`, or `custom` |
| `--half-width` | — | Window half-width when `--style custom` |

### Time window styles

| Style | Half-width | Based on |
|---|---|---|
| `wide` | `T_max / 2` | Cordeau large-window instances (pr06–pr10) |
| `narrow` | `max(30, T_max × 0.15)` | Cordeau tight-window instances (pr01–pr05) |
| `custom` | User-defined via `--half-width` | Manual control |

---

## Examples

```bash
# Minimal — output saved as p02_mdvrptw.txt alongside the input
python mdvrp_to_mdvrptw.py p02

# Narrow time windows (pr01–pr05 benchmark style)
python mdvrp_to_mdvrptw.py p02 --style narrow

# Custom half-width with a fixed planning horizon
python mdvrp_to_mdvrptw.py p02 --style custom --half-width 45 --tmax 480

# Custom service time and explicit output path
python mdvrp_to_mdvrptw.py p02 --service-time 15 -o converted/p02_mdvrptw.txt

# Input from a different directory
python mdvrp_to_mdvrptw.py ../instances/p02 -o ./output/p02_mdvrptw.txt
```

---

## Output summary

Every run prints a summary to the terminal:

```
====================================================
  MDVRP → MDVRPTW Conversion Summary
====================================================
  Input file     : p02
  Output file    : p02_mdvrptw.txt
  Customers      : 23
  Depots         : 4
  Problem type   : 2 (MDVRP) → 6 (MDVRPTW)
  T_max          : 218
  Service time   : 10
  Window style   : wide
  Half-width     : 109.0
  Travel time    : Euclidean distance (speed = 1)
====================================================
```

---

## References

Cordeau, J-F., Laporte, G., & Mercier, A. (2001). A unified tabu search heuristic for vehicle routing problems with time windows. *Journal of the Operational Research Society*, 52(8), 928–936.

---

## Author

**blackcontractor90** — [@blackcontractor90](https://github.com/blackcontractor90)

---

## License

MIT
