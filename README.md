
# Review of Background Soil Arsenic Concentrations in Lower Mainland

> This repository consists of scripts for automating analytical table creation  

## Project Structure

```
base_dev/
│
├── pyproject.toml          # Project dependencies
├── uv.lock                 # Locked dependency versions
├── README.md               # Instructions
├── scripts/
│   ├── analytical_tables.py     # manipulating lab tables 
│   ├── fetch_api.py        # fetching data from apis
│   ├── lnapl_monitoring.py # powell street lnapl data manipulation
│   ├── p4_stats.py         # COR P4 application stats
├── utils                   # store utility scripts 
└── .venv/                  # Virtual environment (created automatically)
```

---
## Analytical Table Preparation Flow
- Export table from ESDAT refer to ESDAT training
- Filter out wells using script 
- Format 
- RPDs 
- Flag RPDs that fail DQO 

## Excel Formulas 
### Conditional Formatting 

#### Highlights exceedances 
```
=AND($D6<>"-", VALUE(SUBSTITUTE(E6, "<", "")) > VALUE($D6))
```
- D: standard column 
- E: start of data column
- 6: row where data starts 

#### Highlights RDL exceedances 

```
=AND($D6<>"-", LEFT(E6, 1)="<", VALUE(SUBSTITUTE(E6, "<", "")) > VALUE($D6))
```
- D: standard column 
- E: start of data column
- 6: row where data starts 


#### Highlights RDL exceedances (Multiple standards)
```
=LET(
    standards,$D8:$J8,
    min_std,
        MIN(
            IF(
                standards="NS",
                1E99,
                IFERROR(
                    --TEXTBEFORE(standards,"-"),
                    --standards
                )
            )
        ),
    AND(
        LEFT(L8,1)="<",
        --MID(L8,2,99)>min_std
    )
)
```
- D8: start of standards 
- J8: last standard col 
- L8: start of values 

```
=AND(   E$2="RPD",   ISNUMBER(E6),   E6 > 0.45 )
```
- Highlights RPD below data quality objective
- E2: Col where data starts and row where RPD is
- E6: start of data 

### RPD Calculation
```
=IF(OR(E6="-", F6="-", E6="", F6=""),  "-",  IF(AND(ISNUMBER(E6), ISNUMBER(F6)),IF(AND(E6<=$C6*5, F6<=$C6*5),"NC", ABS(E6-F6)/AVERAGE(E6, F6)),"NC"))
```
- E6: Parent value
- F6: Dup value
- C6: RDL

### RPD DQO
| Medium | Parameter Category | Lab Duplicate DQO | Field Duplicate DQO |
|:------:|:-------------------|:-----------------:|:-------------------:|
| **Soil** | High variability metals (Ag, Al, Ba, Hg, K, Mo, Na, Pb, Sn, Sr, Ti) | 40% | 60% |
| **Soil** | Other metals and general inorganics | 30% | 45% |
| **Soil** | Polycyclic Aromatic Hydrocarbons (PAH) | 50% | 75% |
| **Soil** | Extractable Petroleum Hydrocarbons | 40% | 60% |
| **Soil** | Volatile organics and most other typical organic parameters | 40% | 60% |
| **Water** | Metals and general inorganics | 20% | 30% |
| **Water** | Polycyclic Aromatic Hydrocarbons (PAH) | 30% | 45% |
| **Water** | Extractable Petroleum Hydrocarbons | 30% | 45% |
| **Water** | Volatile organics and most other typical organic parameters | 30% | 45% |
| **Vapour** | All parameters | 40% | 60% |

