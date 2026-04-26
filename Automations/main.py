import pandas as pd
import re
from functions import create_bib_text , df_to_latex_table

MASTER_FILE = r"G:\My Drive\10DOT\Deliverable1\SubmissionPackage\MasterSheet.xlsx"  
PAPERS_SHEET = "Papers"
RAW_DATA_SHEET = "RAW_DATA"
CODES_SHEET = "Codes"

CODES_COL_TO_KEEP = [
    "Reference" ,
    "Factor" ,	
    "Layer"	 , 
    "Subdivision" ,
    "Interpretation" ,
]


# === LOAD SHEETS ===
refs_df = pd.read_excel( MASTER_FILE , sheet_name= PAPERS_SHEET )   # contains Reference, EID
raw_df  = pd.read_excel( MASTER_FILE , sheet_name= RAW_DATA_SHEET )   # contains full metadata
codes_df = pd.read_excel( MASTER_FILE , sheet_name = CODES_SHEET ) 

# === CLEAN COLUMN NAMES (avoid hidden issues) ===
refs_df.columns = refs_df.columns.str.strip()
raw_df.columns  = raw_df.columns.str.strip()
create_bib_text( refs_df , raw_df )

df_to_latex_table(
    df=codes_df,
    columns=[
        "Reference",
        "Factor",
        "Layer",
        "Subdivision",
        "Interpretation"
    ],
    citation_hook="Reference",

    caption="Trust framework mapping",
    label="tab:trust_framework",

    output_file="tables.tex",

    use_longtable=True,        # ⭐ multi-page
    longtable_width="4cm"      # adjust if needed
)
