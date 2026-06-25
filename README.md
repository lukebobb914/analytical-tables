
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

## Excel Formulas 
### Conditional Formatting 
```
=AND($D6<>"-", VALUE(SUBSTITUTE(E6, "<", "")) > VALUE($D6))
```
- Highlights exceedances 
- D: standard column 
- E: start of data column
- 6: row where data starts 

```
=AND($D6<>"-", LEFT(E6, 1)="<", VALUE(SUBSTITUTE(E6, "<", "")) > VALUE($D6))
```
- Highlights RDL exceedances 
- D: standard column 
- E: start of data column
- 6: row where data starts 

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
