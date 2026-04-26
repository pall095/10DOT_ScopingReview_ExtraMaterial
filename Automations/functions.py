
import pandas as pd
from typing import List, Optional, Dict, Union

import pandas as pd

# === SAFE FIELD CLEANING ===
def clean_field(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value if value else None

# === FUNCTION TO FORMAT AUTHORS ===
def format_authors(authors):
    authors = clean_field(authors)
    if not authors:
        return None
    
    # Scopus format: "Lastname, Firstname; Lastname, Firstname"
    formatted = []
    for a in authors.split(";"):
        a = a.strip()
        if a:
            formatted.append(a)
    
    return " and ".join(formatted) if formatted else None

# === FUNCTION TO CREATE BIB ENTRY ===
def make_bibtex(row):
    key = clean_field(row.get("Reference"))
    if not key:
        return None

    fields = {
        "author":  format_authors(row.get("Authors")),
        "title":   clean_field(row.get("Title")),
        "journal": clean_field(row.get("Source title")),
        "year":    clean_field(row.get("Year")),
        "volume":  clean_field(row.get("Volume")),
        "number":  clean_field(row.get("Issue")),
        "doi":     clean_field(row.get("DOI")),
    }

    # Handle pages separately
    start = clean_field(row.get("Page start"))
    end   = clean_field(row.get("Page end"))
    if start or end:
        fields["pages"] = f"{start or ''}-{end or ''}".strip("-")

    # Build BibTeX only with non-null fields
    field_lines = [
        f"  {k} = {{{v}}}"
        for k, v in fields.items()
        if v is not None
    ]

    bib = f"@article{{{key},\n" + ",\n".join(field_lines) + "\n}"
    return bib

# === MAIN FUNCTION ===
def create_bib_text(reference_data_frame: pd.DataFrame,
                    raw_data_frame: pd.DataFrame,
                    output_name: str = "output.bib"):

    refs_df = reference_data_frame[["Reference", "EID"]]
    merged = pd.merge(refs_df, raw_data_frame, on="EID", how="left")

    bib_entries = []

    for _, row in merged.iterrows():
        entry = make_bibtex(row)
        if entry:
            bib_entries.append(entry)

    with open(output_name, "w", encoding="utf-8") as f:
        f.write("\n\n".join(bib_entries))

    print(f"✅ BibTeX file generated: {output_name}")

def df_to_latex_table(
    df: pd.DataFrame,
    columns: List[str],
    column_names: Optional[Dict[str, str]] = None,
    caption: Optional[str] = None,
    label: Optional[str] = None,
    max_rows: Optional[int] = None,
    citation_hook: Optional[Union[str, List[str]]] = None,
    output_file: Optional[str] = None,
    append: bool = False,

    # layout
    use_longtable: bool = True,
    full_width: bool = True,
    own_page: bool = True,
    use_tabularx: bool = True,
    longtable_width: str = "8cm"   # ⭐ width for last column
) -> str:

    # --- Normalize citation hook ---
    if isinstance(citation_hook, str):
        citation_hook = [citation_hook]

    # --- Select columns ---
    df = df[columns].copy()

    if max_rows:
        df = df.head(max_rows)

    # --- Rename columns ---
    if column_names:
        df = df.rename(columns=column_names)

    # --- Escape LaTeX ---
    def escape_latex(text: str) -> str:
        replacements = {
            "&": "\\&",
            "%": "\\%",
            "$": "\\$",
            "#": "\\#",
            "_": "\\_",
            "{": "\\{",
            "}": "\\}",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    # --- Process cells ---
    def process_cell(col, val):
        val = "" if pd.isna(val) else str(val)

        # remove line breaks
        val = val.replace("\n", " ").replace("\r", " ")

        if citation_hook and col in citation_hook:
            return f"\\cite{{{val.strip()}}}"

        return escape_latex(val).strip()

    df = pd.DataFrame({
        col: [process_cell(col, v) for v in df[col]]
        for col in df.columns
    })

    # --- ALIGNMENT (CORRECT FOR EACH MODE) ---
    n_cols = len(df.columns)

    if use_longtable:
        # ❗ longtable does NOT support X → use p{width}
        align = " ".join(["l"] * (n_cols - 1) + [f"p{{{longtable_width}}}"])
    elif use_tabularx:
        align = " ".join(["l"] * (n_cols - 1) + ["X"])
    else:
        align = " ".join(["l"] * n_cols)

    # --- Header ---
    header = " & ".join(df.columns) + " \\\\"

    lines = []

    # =========================================================
    # LONGTABLE (multi-page, correct)
    # =========================================================
    if use_longtable:

        lines.append("\\onecolumn")
        lines.append(f"\\begin{{longtable}}{{{align}}}")

        lines.append("\\toprule")
        lines.append(header)
        lines.append("\\midrule")
        lines.append("\\endfirsthead")

        lines.append("\\toprule")
        lines.append(header)
        lines.append("\\midrule")
        lines.append("\\endhead")

        for row in df.values:
            lines.append(" & ".join(row) + " \\\\")

        lines.append("\\bottomrule")

        if caption:
            lines.append(f"\\caption{{{caption}}}\\\\")
        if label:
            lines.append(f"\\label{{{label}}}\\\\")  # label after caption

        lines.append("\\end{longtable}")
        lines.append("\\twocolumn")

    # =========================================================
    # STANDARD FLOAT (table / table*)
    # =========================================================
    else:

        table_env = "table*" if full_width else "table"
        placement = "[p]" if own_page else "[h]"

        if own_page:
            lines.append("\\clearpage")

        lines.append(f"\\begin{{{table_env}}}{placement}")
        lines.append("\\centering")

        if use_tabularx:
            lines.append(f"\\begin{{tabularx}}{{\\textwidth}}{{{align}}}")
        else:
            lines.append(f"\\begin{{tabular}}{{{align}}}")

        lines.append("\\toprule")
        lines.append(header)
        lines.append("\\midrule")

        for row in df.values:
            lines.append(" & ".join(row) + " \\\\")

        lines.append("\\bottomrule")

        if use_tabularx:
            lines.append("\\end{tabularx}")
        else:
            lines.append("\\end{tabular}")

        if caption:
            lines.append(f"\\caption{{{caption}}}")
        if label:
            lines.append(f"\\label{{{label}}}")

        lines.append(f"\\end{{{table_env}}}")

        if own_page:
            lines.append("\\clearpage")

    latex_str = "\n".join(lines)

    # --- Write file ---
    if output_file:
        mode = "a" if append else "w"
        with open(output_file, mode, encoding="utf-8") as f:
            f.write(latex_str + "\n")

    return latex_str


def extract_metrics( codes_frame : pd.DataFrame ) :

    LAYER_COL = "Layer"
    SUBDIVISION_COL = "Subdivision"

    master_dict = dict( )


    for row , row_content in codes_frame.iterrows( ) :

        layer = row_content[ LAYER_COL ]
        subdivision = row_content[ SUBDIVISION_COL ]

        if not( layer in master_dict.keys( ) ) :
            master_dict[ layer ] = dict( )
            master_dict[ layer ][ subdivision ] = 1 
            
        else :
            if subdivision in master_dict[ layer ].keys( ) :
                master_dict[ layer ][ subdivision ] += 1 
            else :
                master_dict[ layer ][ subdivision ] = 1 

    return master_dict         

    