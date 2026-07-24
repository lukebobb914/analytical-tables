
# Analytical Tables Guide

> This repository consists of scripts for automating analytical table creation  

## Installation

### Clone Repo  

```bash  
git clone ...
```

### Create Virtual Environemnt  

```bash
uv sync
source .venv/bin/activate
```


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

### 1. Highlights Exceedances (Multiple Standards) 
```excel
=LET(standards,$D8:$D8,min_std,MIN(IF(standards="NS",1E99,IFERROR(--TEXTBEFORE(standards,"-"),--standards))),AND(E$2<>"RPD",ISNUMBER(E8),E8>min_std))
```
- $D8: start of standards
- $D8: end of standards
- E8: start of data 
- E2: row where RPD of current col (checks if is RPD col)

### 2. Highlights Detection Limit Exceedances (Multiple standards)
```excel
=LET(standards,$D8:$J8,min_std,MIN(IF(standards="NS",1E99,IFERROR(--TEXTBEFORE(standards,"-"),--standards))),AND(LEFT(L8,1)="<",--MID(L8,2,99)>min_std))
```
- D8: start of standards 
- J8: last standard col 
- L8: start of values 


### 3. Highlights RPD below DQO
```excel
=AND(E$2="RPD", ISNUMBER(E6), E6 > 0.45 )
```
- Highlights RPD below data quality objective
- RPD = NC when both sample and duplicate concentrations are <5X detection limit 
- E2: Col where data starts and row where RPD is
- E6: start of data 

### 4. Highlights UCC 
```excel
=LET(standards,$D6:$D6,min_std,MIN(IF(standards="NS",1E99,IFERROR(--TEXTBEFORE(standards,"-"),--standards))),AND(E$2<>"RPD", min_std<>1E99, ISNUMBER(F6),F6>(10*min_std)))
```
- Highlights values that exceed 10X the standard and will require comparison to upper cap concentrations listed in P11
- $D6: start of standards
- $D6: end of standards
- F6: start of data 
- E2: RPD's row of current col (checks if is RPD col)

#### RPD DQO Limits
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


### RPD Calculation (Single value standards)
```excel
=IF(OR(E6="-", F6="-", E6="", F6=""),  "-",  IF(AND(ISNUMBER(E6), ISNUMBER(F6)),IF(AND(E6<=$C6*5, F6<=$C6*5),"NC", ABS(E6-F6)/AVERAGE(E6, F6)),"NC"))
```
- W6: Parent value
- X6: Dup value
- C6: RDL

### RPD Calculation (Standard is a range)
```excel
=LET(std,IF(ISNUMBER($C6),$C6,VALUE(TEXTBEFORE($C6,"-"))),IF(OR(W6="-",X6="-",W6="",X6=""),"-",IF(AND(ISNUMBER(W6),ISNUMBER(X6)),IF(AND(W6<=std*5,X6<=std*5),"NC",ABS(W6-X6)/AVERAGE(W6,X6)),"NC")))
```
- W6: Parent value
- X6: Dup value
- C6: RDL


#### Equation Breakdown 
```excel
IF(OR(W6="-",X6="-",W6="",X6="")    
```
- Check if parent/daughter result is missing 

```excel
IF(AND(ISNUMBER(W6),ISNUMBER(X6))
```
- Checks if parent/daughter are number types
- If either value non numeric => NC

```excel
IF(ISNUMBER($C6),$C6,VALUE(TEXTBEFORE($C6,"-")))
``` 
- Take lowest standard range 
- if single number -> take name as is 

```excel
IF(AND(W6<=std*5,X6<=std*5),"NC",ABS(W6-X6)/AVERAGE(W6,X6)),"NC"))
```
- If parent <=5X standard -> NC otherwise calculate

