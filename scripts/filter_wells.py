# =============================================================================
# Current Author   : Michael Chan
# Contact Info     : mchan@core6.ca
#
# 
# This script filters ESDAT export by wells you want
#TODO: Add functionality 
# - remove rows where all values are '-' 
# ============================================================================
#%%
from openpyxl.utils import column_index_from_string
import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import os

data_path = Path.cwd().parent / 'data'
output_path = Path.cwd().parent / 'output'     
output_path.mkdir(parents=True, exist_ok=True)

# %%
# #! Inputs 
header_row = 4                                  # row number shown in excel 
start_col = column_index_from_string('BN')      # col where IDs start
file_name = 'Soil RLLD.xlsx'

keep = ['13MW1S', 'EXC', '22-01', '22-08', '23-13', 
        '23-15', '24-16', 'NE', '8-17', 'MWY', '8-16', 
        'AE15-BH15', 'AE15-BH16', 'AE15-BH17', 
        'AE15-BH18', 'AE15-MW7', 'AE15-MW10', 'AE15-MW11']

#%%
wb = load_workbook(data_path / file_name)
ws = wb['Chemistry Table']

#%%
yellow_fill = PatternFill(
    fill_type='solid',
    start_color='FFFF00',
    end_color='FFFF00'
)

for col in range(start_col, ws.max_column + 1):
    header = str(ws.cell(row=header_row, column=col).value or '').strip()

    # Keep if the header contains any desired well name
    if not any(k.lower() in header.lower() for k in keep):
        # Highlight the entire column
        for row in range(1, ws.max_row + 1):
            ws.cell(row=row, column=col).fill = yellow_fill

# Save to a new file
wb.save(output_path / 'highlighted.xlsx')

#%%
# ========================================
# Delete unwanted cols starting from right to left 
# - start_col - 1 => because we need to include starting col too (range never includes the last index)
# =======================================
for col in range(ws.max_column, start_col - 1, -1):
    header = str(ws.cell(row=header_row, column=col).value or "").strip()

    # loops thru every value in keep and checks if any of them are in current header (case insensitive)
    if not any(k.lower() in header.lower() for k in keep):
        ws.delete_cols(col)

name = os.path.splitext(file_name)[0]
wb.save(output_path / f'{name}_filtered_wells.xlsx')

# %%
