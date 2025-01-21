## nicer-xspec

This repository contains Python scripts for analyzing NICER spectral data using XSPEC with multiple models. It automates the handling of PHA, RMF, and background files, performs spectral fitting, generates plots, and extracts model parameters along with test statistics.

---

### Prerequisites

#### Software
- HEASoft

#### Python Dependencies
- NumPy, Pandas, PyXspec

---

### Usage

1. Initialize Environment:  
   Before running the Python script, ensure HEASoft and CALDB are initialized.

2. Run the Script:
   Use the following command to analyze an observation:  
   ```bash
   python nicer_xspec.py observation_path
   ```
   - `observation_path`:  
     Can be either:
     - A directory containing the required files (`PHA`, `RMF`, and `BKG`) with appropriate naming.  
     - A text file listing multiple observation paths (one per line).

---

## Outputs

For each XSPEC model, the following files will be generated:

- Logs: `model_xspec.log` (e.g., `logpar_xspec.log`) – logs of the analysis.
- Plots: `model_plot.ps` – spectral and ratio plots.
- Model Files: `model.xcm` – XSPEC model files.
- Data:
	- `model_spec.csv` – spectrum plot data.
	- `model_ratio.csv` – ratio plot data.
 
- `model_pm.csv`: Extracted model parameters.
- `model_ts.csv`: Test statistics of the models.

---

### Example Directory Structure

Ensure the following files exist in the directory for a single observation:
```
observation_path/
├── *src.pha   # Source spectrum file
├── *.rmf     # Response matrix file
├── *bkg.xcm  # Background model file
```

--- 

### Error Logging

If the analysis fails for any observation, the path and error details will be logged in a `failed_obs.txt` file for review.

