# =============================================================================
# Current Author   : Michael Chan
# Contact Info     : mchan@core6.ca
#
# This script:
# Combines duplicate sample results together that have been generated due
# to results of the same sample being reported in separate lab reports.
# Lab report IDs will be retained by appending removed row to the existing report ID col
# ============================================================================
# %%
import pandas as pd
from pathlib import Path
import numpy as np
from enum import Enum

class Matrix(Enum): 
    SOIL = 'soil'
    GW = 'gw'
    SW = 'sw'
    PW = 'pw'
    SED = 'sed'

def process_split_data(df: pd.DataFrame, groupby_fields: list, non_analyte_cols: list) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_conflicts = []
    merged_rows = []
    for _, group in df.groupby(groupby_fields, sort=False):
        group = group.sort_values('missing_count', ascending=True)                 # sort by least missing values
        base_row = group.iloc[0].copy()                                            # define base_row
        data_cols = [col for col in group.columns if col not in non_analyte_cols]     # define analytes cols 

        # Populate 'Lab Report Number with list of unique lab reports 
        lab_reports = group['Lab Report Number'].dropna().unique().tolist()     
        base_row['Lab Report Number'] = ', '.join(str(x) for x in lab_reports)

        # merge rows together
        base_row, conflicts = merge_group(group, data_cols, base_row)
        merged_rows.append(base_row)
        all_conflicts.extend(conflicts)

    # =========================
    # Create df 
    # =========================
    merged_df = pd.DataFrame(merged_rows).reset_index(drop=True)
    conflicts_df = pd.DataFrame(all_conflicts)

    # =========================
    # Check any rows missed 
    # =========================
    dropped_df = df[df[groupby_fields].isna().any(axis=1)]

    return merged_df, conflicts_df, dropped_df

def merge_group(df: pd.DataFrame, data_cols: list, base_row: pd.Series) -> tuple[pd.Series, list[dict]]:
    """ 
    merges rows together given a df and returns a 
    series of a single merged row and a series of all conflicts
    """
    # Steps: 
    # 1) iterate thru each row in df but skip 1st row (base_row)
    # 2) Create a conflict mask to flag params that have conflicting values b/w rows
    # 3) Store row/param info that are in conflict 
    # 4) Copy over current row data to base_row only if base_row doesn't have data already
    # 5) strip whitespace that is generated during step 4
    
    conflicts = []
    for _, row in df.iloc[1:].iterrows():
        # True (flag) only if all three conditions are met 
        # 1. Base row has a value
        # 2. current row has a value 
        # 3. values b/w two are different
        conflict_mask = (
            base_row[data_cols].notna() &
            row[data_cols].notna() &
            ~base_row[data_cols].eq(row[data_cols])
        )

        # Store info of param/row that are in conflict
        if conflict_mask.any():
            # append to conflicts list this dictionary
            conflicts.append({
                'base_sample_code': base_row['Sample Code'],                            # get base_row's sample code 
                'sample_code': row['Sample Code'],                                      # get current role's sample code 
                'conflicting_columns': conflict_mask[conflict_mask].index.tolist(),     # col names with conflicting values 
                'base_values': base_row[data_cols][conflict_mask].to_dict(),            # gets series of all conflicts (base) => converts to dict
                'row_values': row[data_cols][conflict_mask].to_dict()                   # gets series of all conflicts (current role) => converts to dict
            })

        # Copy over current row to base_row only if no value exists in base_row
        mask = base_row.isna() & row.notna()
        base_row.loc[mask] = row.loc[mask]
    return base_row, conflicts

parent_dir = Path(__file__).resolve().parent.parent
data_path = parent_dir / 'data'
output_path = parent_dir / 'output'
output_path.mkdir(parents=True, exist_ok=True)

# %%
# =========================
# Inputs
# =========================
excel_name = 'kitimat_historical_soil.xlsx'
header_row = 47                     # row # with headers  
last_row = 466                      # last row # with data 
matrix_type = Matrix.SW             # one of SOIL, SW, GW, PW, SED

# =========================
# Constants
# =========================
# cols that are not analyte cols (ie. do not need to check if there is conflict)
non_analyte_cols = ['Sample Code', 'missing_count', 'Lab Report Number', 'Parent Sample']

# Fields used to group rows from the same samples together
groupby_fields_dict = {
    'soil': ['Location Code', 'Date', 'Sample Type', 'Depth'], 
    'sw': ['Location Code', 'Date', 'Sample Type'],
    'gw': ['Location Code', 'Date', 'Sample Type'],
    'pw': ['Location Code', 'Date', 'Sample Type'],
    'sed': ['Location Code', 'Date', 'Sample Type', 'Depth'],
}

# =========================
# Calculated Params 
# =========================
num_rows = last_row - header_row 
groupby_fields = groupby_fields_dict[matrix_type.value]

#%%
# =========================
# Set up
# =========================
df = pd.read_excel(data_path / excel_name, sheet_name='Chemistry Table', skiprows=header_row, nrows=num_rows)
df['missing_count'] = (df == '-').sum(axis=1)
df = df.replace('-', np.nan)
df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

#%% 
# =========================
# Combine rows
# =========================
# process split data 
merged_df, conflicts_df, dropped_df = process_split_data(df, groupby_fields, non_analyte_cols)  

# export 
merged_df.to_csv(output_path / 'merged.csv')
conflicts_df.to_csv(output_path / 'conflicts.csv')
dropped_df.to_csv(output_path / 'dropped.csv')


# #%%
# for _, group in df.groupby(groupby_fields, sort=False):
#     group = group.sort_values('missing_count', ascending=True)                 # sort by least missing values
#     base_row = group.iloc[0].copy()                                            # define base_row
#     data_cols = [col for col in group.columns if col not in non_analyte_cols]     # define analytes cols 

#     # Populate 'Lab Report Number with list of unique lab reports to 
#     lab_reports = group['Lab Report Number'].dropna().unique().tolist()     
#     base_row['Lab Report Number'] = ', '.join(str(x) for x in lab_reports)

#     # merge rows together
#     base_row, conflicts = merge_group(group, data_cols, base_row)
#     merged_rows.append(base_row)
#     all_conflicts.extend(conflicts)

#     # =========================
#     # Check any rows missed 
#     # =========================
#     dropped_df = df[df[groupby_fields].isna().any(axis=1)]

#     # =========================
#     # Export
#     # =========================
#     merged_df = pd.DataFrame(merged_rows).reset_index(drop=True)
#     conflicts_df = pd.DataFrame(all_conflicts)

#     merged_df.to_csv(output_path / 'merged.csv')
#     conflicts_df.to_csv(output_path / 'conflicts.csv')
#     dropped_df.to_csv(output_path / 'dropped.csv')