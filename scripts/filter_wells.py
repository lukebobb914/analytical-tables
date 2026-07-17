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
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils import column_index_from_string
from openpyxl.styles import Font, Alignment
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import os

data_path = Path.cwd().parent / 'data'
output_path = Path.cwd().parent / 'output'     
output_path.mkdir(parents=True, exist_ok=True)


#%%
def main(excel: str, start_col: int, header_row: int, keep: list, param_start_row: int, safe: bool=False) -> None:
    """
    Main function to filter wells and delete unwanted data
    """
    # steps: 
    # 1) Delete/highlight unwanted wells 
    # 2) Remove no data params 
    # 3) Apply Core6 font 
    wb = load_workbook(excel)
    ws = wb['Chemistry Table']

    if safe == True: 
        highlight_unwanted_wells(ws, start_col, header_row, keep)
    else: 
        delete_unwanted_wells(ws, start_col, header_row, keep)
    
    delete_nodata_params(ws, start_col, param_start_row)
    apply_core6_fonts(ws)

    # save workbook 
    name = os.path.splitext(file_name)[0]
    wb.save(output_path / f'{name}_filtered_wells.xlsx')


def highlight_unwanted_wells(ws, start_col, header_row, keep) -> None:
    """ 
    highlights cols that don't want to keep in yellow
    """
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
    


# ========================================
# Delete unwanted wells 
# =======================================
# • delete starting from right to left 
# • start_col minus 1 (cuz need to include starting col too)
def delete_unwanted_wells(ws, start_col, header_row, keep) -> None:
    """
    Deletes columns that don't want to keep
    """
    for col in range(ws.max_column, start_col - 1, -1):
        header = str(ws.cell(row=header_row, column=col).value or '').strip()

        # loops thru every value in keep and checks if any of them are in current header (case insensitive)
        if not any(k.lower() in header.lower() for k in keep):
            ws.delete_cols(col)

    print('deleted all unwanted columns (wells)')

# ========================================
# Delete params that have nodata 
# =======================================
# • Loop thru all rows starting from bottom to start_row
# • Each row create list of all values from start_col to end 
# • Check if all values == '-' 
# • If yes, delete row 

def delete_nodata_params(ws, start_col, param_start_row) -> None:
    """
    Deletes rows where all values are '-' (ie. NODATA)
    """
    for row in range(ws.max_row, param_start_row - 1, -1):
        values = [ws.cell(row, col).value for col in range(start_col, ws.max_column + 1)]
        if all(v == '-' for v in values):       # generator expression to apply function check to see if all values evaluate to True
            ws.delete_rows(row)
    
    print('Deleted parameter rows where all wells had no data')

# ========================================
# Fonts/Colors
# =======================================
def apply_core6_fonts(ws) -> None: 
    font = Font(name='Avenir', size=10)
    alignment = Alignment(horizontal='center', vertical='center')

    for row in ws.iter_rows():
        for cell in row:
            cell.font = font
            cell.alignment = alignment

    print('Applied Core6 fonts')

# %%
# #! Inputs 
header_row = 4                                  # row number shown in excel 
start_col = column_index_from_string('BN')      # col where IDs start
param_start_row = 11                            # row of first param heading 
excel = '/Users/michaelchan/Documents/python/analytical-tables/data/GW.xlsx'

keep = ['13MW1S', '22-01', '22-08', '23-13',    
        '23-15',  
        'AE15-BH15', 'AE15-BH16', 'AE15-BH17', 
        'AE15-MW10', 'AE15-MW11']


# %%
main(excel, start_col, header_row, keep, param_start_row)

# %%
