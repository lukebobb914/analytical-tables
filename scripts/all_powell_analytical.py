# =============================================================================
# Current Author   : Michael Chan
# Contact Info     : mchan@core6.ca
#
# This script: 
# automates the process of sorting/filtering analytical data and outputs 
# excel sheet ready for styling 
# ============================================================================

#%%
import pandas as pd
from pathlib import Path
import csv
import numpy as np

data_path = Path.cwd().parent / 'data'
output_path = Path.cwd().parent / 'output'     
output_path.mkdir(parents=True, exist_ok=True)

#%%
def filter_cols(df: pd.DataFrame, well_ids: list, col_ind: int) -> pd.DataFrame:  
    """ 
    filters for well IDs (cols) of interest from given lab table and returns filtered df
    given col_ind which represents the col where samples start 

    Requires multi-index on df: 
        1. Well ID
        2. Sort by well then date
        3. Rows that actually have analytical results 
            -> remove rows where all samples == '-'
        4. Fix RDL col (take first number)
    """
    # split table
    base_cols = df.iloc[:, :col_ind]
    data_cols = df.iloc[:, col_ind:]

    # filter wells of interest 
    filtered_df = data_cols.loc[:, data_cols.columns.get_level_values(0).isin(well_ids)]

    # sort by well ID then by date (well ID = 0, date = 1)
    filtered_df = filtered_df.sort_index(axis=1, level=[0, 1])

    # remove all occurances of '#1' from entire df
    filtered_df = filtered_df.replace('#1', '', regex=True)

    # join 
    combined = pd.concat([base_cols, filtered_df], axis=1)

    # drop no data rows '-'
    mask = (filtered_df == '-').all(axis=1)
    idx = filtered_df.index[mask]
    final_df = combined.drop(index=idx)
    final_df = final_df[final_df.iloc[:, 1].isna()]

    # fix RDL col 
    final_df.iloc[:, 4] = final_df.iloc[:, 4].apply(lambda x: fix_rdl_values(x))
    return final_df     

def fix_rdl_values(s: str) -> str: 
    """ 
    given rdl value will take the first value if is a range otherwise will 
    return value back
    """
    if pd.isna(s): 
        return s
    
    s = str(s)                      # ensure string type 
    if '-' in s: 
        rdls = s.split('-') 
        return rdls[0].strip()
    else: 
        return s

def remap_well_index(df: pd.DataFrame, mapping_dict: dict) -> pd.DataFrame: 
    """returns a remapped df remapping well ID index of a multi-index df 

    Args:
        df (pd.DataFrame): multi-index df (well id, date)
        mapping_dict (dict): {lab_well_id: well_id_to_map_to}

    """
    well_ids = df.columns.get_level_values(0)       # extract well ids 
    dates = df.columns.get_level_values(1)   # extract dates 
    mapped_well_ids = well_ids.map(lambda x: mapping_dict.get(x, x))     # use pandas .map method to apply fn to each index
    df.columns = pd.MultiIndex.from_arrays([mapped_well_ids, dates])     # insert indexes
    return df

def group_params(df: pd.DataFrame, param_df: pd.DataFrame, order_dict: dict) -> pd.DataFrame: 
    """returns df grouped/sorted based on param groups + order specified by 
    parms_df and order_dict

    Args:
        df (pd.DataFrame): input df 
        params_df (pd.DataFrame): df consisting of headers -> Parameter,  Group
        order_dict (dict): dictionary with group name as key and rank (0-n)
    """
    # convert param_df to dict
    param_to_group = dict(zip(param_df['Parameter'], param_df['Group']))

    # sort index by groupo + group order then param alphabetically 
    # 1. create helper df with group order and param cols 
    # 2. sort based on group_order and param 
    # 3. apply index to df 
    # 4. populate col left of parameters col (shd be empty) with group 
    sort_df = pd.DataFrame({
        '_group_order': df.iloc[:, 2].map(param_to_group).map(order_dict),
        '_param': df.iloc[:, 2]
    })

    sorted_index = sort_df.sort_values(['_group_order', '_param'], kind='stable').index
    final_df = df.loc[sorted_index]
    
    final_df.iloc[:, 1] = final_df.iloc[:, 2].map(param_to_group)
    
    return final_df

def collapse_dup_rows(df: pd.DataFrame) -> pd.DataFrame:  
    """ 
    collapses duplicate rows of df 
    """
    # replace '-' values with nan
    df = df.replace('-', np.nan)

    # collapse -> use first value
    col_series = df.iloc[:, 2]
    collapse = (df.groupby(col_series, dropna=False)
                .first()
                .reset_index(drop=True))

    # replace nan with '-' values
    collapse = collapse.replace(np.nan, '-')

    # remove rows without any params
    collapse = collapse[collapse.iloc[:, 2] != '-'] 

    return collapse

def insert_empty_cols(df, n):
    """ 
    inserts empty cols in needed in vapour tables formatting 
    """
    new_cols = []
    
    # loop thru cols
    for i, col in enumerate(df.columns):
        # add current col to new_cols list 
        new_cols.append(df.iloc[:, i])
        
        # insert 2 cols if col index is >= n (start of samples) 
        if i >= n:
            new_cols.append(pd.Series(np.nan, index=df.index, name=(col[0], "")))
            new_cols.append(pd.Series(np.nan, index=df.index, name=(col[0], "")))
    
    # convert list of cols to df 
    return pd.concat(new_cols, axis=1)

#! Work in progress
def insert_empty_header_rows(df):
    """
    Insert a blank row  whenever
    the value in group column changes.
    """
    rows = []

    prev_grp = None

    for _, row in df.iterrows():
        current_grp = row.iloc[1]

        if current_grp != prev_grp:
            rows.append([np.nan] * len(df.columns))

        rows.append(row.tolist())
        prev_grp = current_grp

    return pd.DataFrame(rows, columns=df.columns)

# %%
# =================================================== Vapour Tables for All Powell St Wells ================================================
# This section creates 2 ready to format analytical tables 
# 1. Onsite wells 
# 2. Offsite wells  
# =========================================================================================================================================

# ========================================
# Load in Chemistry Table + Index
# ========================================
# lab raw data 
excel = data_path / 'all_powell_vp_combined.xlsx'
df = pd.read_excel(excel, sheet_name='Chemistry Table')

# wells of interest with lab ID and well ID 
wells_df = pd.read_excel(data_path / 'classification.xlsx')
wells_df = wells_df.dropna()

# drop param heading rows 
df = df[df.iloc[:, 1].isna()].reset_index(drop=True)

#%% 
# ========================================
# Foward fill merged NaN cells (Vapour export)
# ========================================
#! double check indices are correct now (index will change if you use initial df)
pindex_row = 4      # primary index (well ID)
sindex_row = 2      # secondary index (date)
end_row = 212       # end ind before comments 

data_start_col = 8  # col when data starts 
param_col = 2       # params col
units_col = 3       # units col 


df.iloc[:end_row, param_col] = df.iloc[:end_row, param_col].ffill()                   # downward fill params 

#%%
# forward fill to fix merged cells 
df.iloc[:end_row, param_col] = df.iloc[:end_row, param_col].ffill()                   # downward fill params 
df.loc[pindex_row] = df.loc[pindex_row].ffill()                                       # forward fill if Field ID row has NaN (fills with prev value)
df.loc[sindex_row] = df.loc[sindex_row].ffill()                                       # forward fill dates
df.columns = pd.MultiIndex.from_arrays([df.loc[pindex_row], df.loc[sindex_row]])      # create multi-index

#%%
# ========================================
# remap well id index 
# - map lab ids to correct well IDs 
# ========================================
group_field = 'Type'
grouped = wells_df.groupby(group_field)
mapping_dict = dict(zip(wells_df['Lab ID'], wells_df['Well ID']))
remapped_df = remap_well_index(df, mapping_dict)    

# get new remapped lab IDs
try: 
    alley = grouped.get_group('alley').loc[:, 'Well ID'].tolist()
    onsite = grouped.get_group('onsite').loc[:, 'Well ID'].tolist()
    sidewalk = grouped.get_group('sidewalk').loc[:, 'Well ID'].tolist()
    offsite = grouped.get_group('offsite').loc[:, 'Well ID'].tolist()

    # combine alley, onsite, sidewalk, unknown wells 
    onsite = onsite + alley + sidewalk 

except KeyError as e:
    print(f'Error -> Missing indoor wells: {e}')


#%%
# ========================================
# define param order 
# ========================================
group_order = {
    'Extractable Hydrocarbons': 1,
    'Volatile Hydrocarbons': 0,
    'Polycyclic Aromatic Hydrocarbons (PAHs)': 2,
    'Volatile Organic Compounds (VOCs)': 3,
}

param_df = pd.read_csv(data_path / 'vp_params.csv')

#%%
# ========================================
# 1. filter cols (filter cols)
# 2. remove other units (rows)
# 3. group/sort (group params in correct order)
# 4. insert empty cols 
# ========================================
filtered_df = filter_cols(remapped_df, onsite, data_start_col)
data_df = filtered_df.iloc[7:]  # skip first 6 rows 
collapse_df = data_df[~data_df.iloc[:, units_col].isin(['ppbv', 'ug/sample'])]
final_df = group_params(collapse_df, param_df, group_order)
inserted_df = insert_empty_cols(final_df, n=data_start_col)
inserted_df = insert_empty_header_rows(inserted_df)
inserted_df.to_excel(output_path / 'All Onsite VP Analytical.xlsx')

print(f'Unique Params Count Before Row Collapse {filtered_df.iloc[:, 2].replace('-', np.nan).nunique()}')
print(f'Unique Params Count After Collapse {collapse_df.iloc[:, 2].replace('-', np.nan).nunique()}')
print(f'Unique Params Count After Group/Sort {final_df.iloc[:, 2].replace('-', np.nan).nunique()}')



# %%
# Offsite Properties
# ========================================
# 1. filter cols (filter cols)
# 2. remove other units (rows)
# 3. group/sort (group params in correct order)
# 4. insert empty cols 
# ========================================
filtered_df = filter_cols(remapped_df, offsite, data_start_col)
data_df = filtered_df.iloc[7:]  # skip first 6 rows 
collapse_df = data_df[~data_df.iloc[:, units_col].isin(['ppbv', 'ug/sample'])]
final_df = group_params(collapse_df, param_df, group_order)
inserted_df = insert_empty_cols(final_df, n=data_start_col)
inserted_df.to_excel(output_path / 'All Offsite VP Analytical.xlsx')

print(f'Unique Params Count Before Row Collapse {filtered_df.iloc[:, 2].replace('-', np.nan).nunique()}')
print(f'Unique Params Count After Collapse {collapse_df.iloc[:, 2].replace('-', np.nan).nunique()}')
print(f'Unique Params Count After Group/Sort {final_df.iloc[:, 2].replace('-', np.nan).nunique()}')

# %%
