# =============================================================================
# Current Author   : Michael Chan
# Contact Info     : mchan@core6.ca
#
# This script helps reorder rows of esdat vertical export to predefined order

# Pre-requesites: 
# - Import Excel Spreadsheet: consists of 2 worksheets 
#       1. order  - extracted col order 
#       2. export - new esdat export 
#
# Example 'Order' worksheet 

# | Altered                        | Original                           |
# |--------------------------------|------------------------------------|
# | extractable hydrocarbons       | Extractable Petroleum Hydrocarbons |
# | EPH C10-C19                    | EPH   C10-C19                      |
# | EPH C19-C32                    | EPH   C19-C32                      |
# | LEPH                           | LEPH                               |
# | HEPH                           | HEPH                               |
# | Physical Parameters            | Physical Parameters                |
# | Total Suspended Solids         | Total   Suspended Solids           |
# | volatile hydrocarbons          | Volatile Petroleum Hydrocarbons    |
# | vh c6-c10                      | VH   (C6-C10)                       |
# | vph (c6-c10)                   | VPH   (VH C6-C10 - BTEX)           |
# | Benzene                        | Benzene                            |
# | Toluene                        | Toluene                            |
# | Ethylbenzene                   | Ethylbenzene                       |
# | methyl tert-butyl ether (mtbe) | Methyl   tert-butyl ether          |
# | Styrene                        | Styrene                            |
# | Xylene (m & p)                 | Xylene   (m & p)                   |
# | Xylene (o)                     | Xylene   (o)                       |

# * user needs to manually inspect unmatched rows
# * For params that are diff -> change param in 'order' so it matches 
# * keep the original col so u know what was original
# ============================================================================
#%%
import pandas as pd
from pathlib import Path
import csv
import numpy as np

parent_dir = Path(__file__).resolve().parent.parent
data_path = parent_dir / 'data'
output_path = parent_dir / 'output'
output_path.mkdir(parents=True, exist_ok=True)

#%%
# =============================
# Import data
# =============================
rows_to_skip = 8

order_df = pd.read_excel(data_path / 'bp_esdat_export.xlsx', sheet_name='order')
export_df = pd.read_excel(data_path / 'bp_esdat_export.xlsx', sheet_name='export1', skiprows=rows_to_skip)
export_df = export_df.iloc[:, 2:]       # drop first 2 cols

# convert param col to lowercase 
order_df.iloc[:, 0] = order_df.iloc[:, 0].astype('string').str.strip().str.lower()
export_df.iloc[:, 0] = export_df.iloc[:, 0].astype('string').str.strip().str.lower()
# %%
# See which parameters are missing or inconsistent 
order = order_df.iloc[:, [0]].rename(
    columns={order_df.columns[0]: 'Master Order'}
)

export = export_df.iloc[:, [0]].drop_duplicates().rename(
    columns={export_df.columns[0]: 'Export Order'}
)
merged_params_df = order.merge(export, left_on='Master Order', right_on='Export Order', how='outer', indicator=True)
merged_params_df.columns = ['order', 'export', 'status']
merged_params_df.to_csv('check_params.csv', index=False)

# Check dup params in export 
duplicates = export_df[
    export_df.iloc[:, 0].duplicated(keep=False)
].sort_values(export_df.columns[0])

print(duplicates)
print('**fix duplicates if applicable')

# %%
# Build actual df 
df = order_df.merge(export_df, left_on='Altered', right_on=export_df.iloc[:, 0], how='left')
df = df.fillna('ZZZ')
df.to_csv(output_path / 'reordered.csv', index=False)
# %%
