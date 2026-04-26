# Scoping Review Extra Material

This git repo contains, at the root level:
-  **`MasterSheet.xlsx`**: spreadsheet used during the review process.
- **`10_DOT_Scoping_Review_V2.pdf`** : final submission paper.

Moreover, the folliwing subfolders are present:

- **/Images**  
  Contains all images included in the paper.

- **/Automation**  
  Contains scripts used to automate parts of the review process.

- **/Latex**  
  Contains the source `.tex` file and the corresponding `.bib` reference file.

> **Note 1:** it is worth noticing that to write the Latex document Prism has been used (https://openai.com/prism/). Since prism is an onoine collaborative Latex editor, it does not generates the usual overhead files created by other Latex interpreters (e.g. TexMaker), therefore these files are not part of the submission. However, the source code should be enough to re-compile the paper. 

> **Note 2:** the`.bib` file is automatically generated with python. Fields that were not available in the RAW_DATA from Scopus (see below) are ignored in the generation process. 
---

## Master Sheet

The `.xlsx` file used during the review process is the core artifact of this work. It contains multiple sheets, each serving a specific role. A detailed description of each sheet is provided below.

> **Note:** All columns highlighted in bright yellow are computed via formulas.

---

### 1. RAW_DATA

- Contains the raw results obtained from the Scopus query.
- Includes additional auto-filled columns used for:
  - duplication detection  
  - consistency checks  

---

### 2. Papers

This is the **main working sheet** used throughout the review process. It contains all non-duplicate papers and includes the following key columns:

- **Reference**  
  - Unique internal identifier assigned to each paper  
  - Serves as:
    - the *join key* with the `Codes` sheet.  
    - the identifier for entries in the generated `.bib` file.  

- **Type**  
  - Classification of the paper: *practical*, *theoretical*, or *empirical*  
  - Set to `N/A` for papers not included in the final selection  

- **Title Screening**  
  - `Yes` → paper passed title screening  
  - `No` → paper excluded at title screening  

- **Abstract Screening**  
  - `Yes` → paper passed abstract screening  
  - `No` → paper excluded at abstract screening  

- **EID**  
  - Auto-filled based on title matching with `RAW_DATA` (and by matchin titles).
  - Used for:
    - duplication consistency checks  
    - joining with `RAW_DATA` to generate references automatically  

---

### 3. Codes

- Contains the extracted codes along with:
  - associated **layer**
  - **sub-layer** classifications  
- The **Reference** column links each code to its corresponding paper in the `Papers` sheet  

---

### 4. Statistics

- Contains aggregated statistics derived from the dataset  
- Values are computed through counts and filters applied to the other sheets  

---

## Automation

The `/Automation` folder contains two Python scripts:

- **main.py**  
  - Executes the automation pipeline  
  - Responsible for:
    - generating references.  
    - producing a LaTeX-compatible summary table (based on the `CODES` sheet)

- **function.py**  
  - Contains supporting utility functions used by `main.py`


> **Note 1:** A significant portion of the code—especially table generation—was produced with the assistance of ChatGPT.

> **Note 2:** Some variables (e.g., file paths and column names) are **hard-coded**. Therefore, to run the script correctly you must:
>  - do **not** modify sheet names in the Excel file  
>  - update the `MASTER_SHEET` variable in `main.py` to point to the local path of the Excel file.