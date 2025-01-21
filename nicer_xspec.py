"""
ABOUT:
- 


TODO:
[x] Function to check files are there or not
[x] Xspec function for model-1 (log parabola)
[x] Xspec function for model-2 (powerlaw)
[x] Xspec function for model-3 (broken powerlaw)
[x] Read the log file and make a json/yaml file for fit statistics
[x] make the code for both single obs analysis and a list of obs
[x] Run it on and kopernik and debug it.
[] check_file:only check file and return bool then in the __main__ print which one/ones is not there. now if all three are not there only first one will show as missing.
[] also check fpath is there or not. now even path is not there.it will show file is not present.
[] error-log is appending. for each code, it has to fresh.

[] Make plot from the spectrum and ratio data - seperate code
[x] Code to read the YAML file - seperate code
[x] Print and save parameters as table.
[] generalise the code such that you can use it on any source. (make nH, z etc user inputs - no source specific data hardcoded)
[] For Xspec models, many lines are repeating/same. How to make it short? Class?
BUGS:
[x] Ignoring bad channel only working in AllData
[x] Only spectrum plot data is able to save. The ratio plot data is not able to save
[x] the xspec three models are running continuously. So, the spectrum is getting added to next session. How to exit xspec after doing on model.
"""

import re
import os
import glob
import yaml
import argparse
import numpy as np
import pandas as pd

try:
	from xspec import *
except ModuleNotFoundError:
	print("\n!!! Xspec is not initiated. Run the Python code after initializing HEASoft and CALDB. !!!\n")
	exit(1)	

def check_file(filepath, pattern):
	"""
	Checks if exactly one file matching the given pattern exists in the specified directory.
	Args:
		filepath (str): Directory path to search.
		pattern (str): File pattern (e.g., '*.rmf').
	Returns:
		str: Path to the matching file if exactly one is found.
	"""
	file_match = glob.glob(os.path.join(filepath, pattern))
	if len(file_match) == 1:
		return file_match[0]
	elif len(file_match) > 1:
		raise ValueError(f"More than one '{pattern}' file found. Please make sure that only one exists in the given path.")
	else:
		raise FileNotFoundError(f"The file matching '{pattern}' is not present in the given path.")

def model_logpar(pha, rmf, bkg, opath):
	"""
	Performs Xspec analysis using the 'logpar' model. Logs the fitting process, generates plots, and saves results.
	Args:
		pha (str): The path to the PHA file, which contains the spectrum data.
		rmf (str): The path to the RMF file used for spectral response calibration.
		bkg (str): The path to the BKG (Background File) used to model the background spectrum.
		opath (str): The directory where the output files will be saved.
	Returns:
		bool: True if the function completes successfully, False otherwise.
	"""
	try:
		# Xpsec output logging
		ch = Xset.chatter
		Xset.chatter = 0
		lch = Xset.logChatter
		Xset.logChatter = 20
		logFile = Xset.openLog(f"{opath}/logpar_xspec.log")
		logFile = Xset.log

		# Loading data
		s1 = Spectrum(pha)
		s1.response = rmf
		s1.background = bkg
		AllData.ignore("bad")
		s1.ignore("**-0.3,10.0-**")

		# Define model and its parameters
		m1 = Model("tbabs*logpar")
		m1.TBabs.nH = 0.0131
		m1.TBabs.nH.frozen = True
		m1.logpar.alpha = 1.0
		m1.logpar.beta = 1.0
		Fit.nIterations = 100
		Fit.statMethod = "chi"
		Fit.perform()
		Fit.show()

		# Plotting
		Plot.device = f"{opath}/logpar_plot.ps"
		Plot.xAxis = "keV"
		Plot.xLog = True
		Plot.yLog = True
		Plot("eeufspec","ratio")

		# Saving the spectrum and ratio plot data
		Plot.device = "/null"
		Plot("eeufspec")
		xVals = Plot.x()
		yVals = Plot.y()
		modVals = Plot.model()
		yErrs = Plot.yErr()
		dataM = np.column_stack((xVals, yVals, yErrs, modVals))
		np.savetxt(f"{opath}/logpar_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")
		Plot("ratio")
		xVals = Plot.x()
		yVals = Plot.y()
		yErrs = Plot.yErr()
		dataR = np.column_stack((xVals, yVals, yErrs))
		np.savetxt(f"{opath}/logpar_ratio.csv", dataR, delimiter=",", header="xVals,yVals,yErrs", comments="")

		Xset.save(f"{opath}/logpar_model.xcm", info='m')
		AllData.clear()
		Xset.closeLog()

		return True
	except Exception as e:
		print(f"> Error: An error in Xspec analysis: {e}")
		return False

def model_powerlaw(pha, rmf, bkg, opath):
	"""
	Performs Xspec analysis using the 'powerlaw' model. Logs the fitting process, generates plots, and saves results.
	"""
	try:
		ch = Xset.chatter
		Xset.chatter = 0
		lch = Xset.logChatter
		Xset.logChatter = 20
		logFile = Xset.openLog(f"{opath}/plaw_xspec.log")
		logFile = Xset.log

		s1 = Spectrum(pha)
		s1.response = rmf
		s1.background = bkg
		AllData.ignore("bad")
		s1.ignore("**-0.3,10.0-**")

		m1 = Model("tbabs*powerlaw")
		m1.TBabs.nH = 0.0131
		m1.TBabs.nH.frozen = True
		m1.powerlaw.PhoIndex = 1.0
		Fit.nIterations = 100
		Fit.statMethod = "chi"
		Fit.perform()
		Fit.show()

		Plot.device = f"{opath}/plaw_plot.ps"
		Plot.xAxis = "keV"
		Plot.xLog = True
		Plot.yLog = True
		Plot("eeufspec","ratio")

		Plot.device = "/null"
		Plot("eeufspec")
		xVals = Plot.x()
		yVals = Plot.y()
		modVals = Plot.model()
		yErrs = Plot.yErr()
		dataM = np.column_stack((xVals, yVals, yErrs, modVals))
		np.savetxt(f"{opath}/plaw_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")
		Plot("ratio")
		xVals = Plot.x()
		yVals = Plot.y()
		yErrs = Plot.yErr()
		dataR = np.column_stack((xVals, yVals, yErrs))
		np.savetxt(f"{opath}/plaw_ratio.csv", dataR, delimiter=",", header="xVals,yVals,yErrs", comments="")

		Xset.save(f"{opath}/plaw_model.xcm", info='m')
		AllData.clear()
		Xset.closeLog()

		return True
	except Exception as e:
		print(f"> Error: An error in Xspec analysis: {e}")
		return False

def model_bknpowerlaw(pha, rmf, bkg, opath):
	"""
	Performs Xspec analysis using the 'powerlaw' model. Logs the fitting process, generates plots, and saves results.
	"""
	try:
		ch = Xset.chatter
		Xset.chatter = 0
		lch = Xset.logChatter
		Xset.logChatter = 20
		logFile = Xset.openLog(f"{opath}/bknpl_xspec.log")
		logFile = Xset.log

		s1 = Spectrum(pha)
		s1.response = rmf
		s1.background = bkg
		AllData.ignore("bad")
		s1.ignore("**-0.3,10.0-**")

		m1 = Model("tbabs*bknpower")
		m1.TBabs.nH = 0.0131
		m1.TBabs.nH.frozen = True
		m1.bknpower.PhoIndx1 = 1.0
		m1.bknpower.PhoIndx2 = 1.0
		Fit.nIterations = 100
		Fit.statMethod = "chi"
		Fit.perform()
		Fit.show()

		Plot.device = f"{opath}/bknpl_plot.ps"
		Plot.xAxis = "keV"
		Plot.xLog = True
		Plot.yLog = True
		Plot("eeufspec","ratio")

		Plot.device = "/null"
		Plot("eeufspec")
		xVals = Plot.x()
		yVals = Plot.y()
		modVals = Plot.model()
		yErrs = Plot.yErr()
		dataM = np.column_stack((xVals, yVals, yErrs, modVals))
		np.savetxt(f"{opath}/bknpl_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")
		Plot("ratio")
		xVals = Plot.x()
		yVals = Plot.y()
		yErrs = Plot.yErr()
		dataR = np.column_stack((xVals, yVals, yErrs))
		np.savetxt(f"{opath}/bknpl_ratio.csv", dataR, delimiter=",", header="xVals,yVals,yErrs", comments="")

		Xset.save(f"{opath}/bknpl_model.xcm", info='m')
		AllData.clear()
		Xset.closeLog()

		return True
	except Exception as e:
		print(f"> Error: An error in Xspec analysis: {e}")
		return False

def get_mparameters(lines, pnames):
	"""
	Extracts parameter values and errors from the lines.
	Args:
		lines (list): Lines of text to search for parameters.
		pnames (list): List of parameter names to extract.
	Returns:
		OrderedDict: Extracted parameter data with value and error.
	"""
	num_pattern = r"\b\d+\.\d+(?:[eE][+-]?\d{2})?\b"
	para_data = {}

	for param in pnames:
		line = next((line for line in lines if param in line), None)
		if line:
			values = re.findall(num_pattern, line)
			para_data[param] = {"value": values[0], "error": values[1] if len(values) > 1 else None}
		else:
			print(f"> Warning: Parameter '{param}' not found in the lines.")

	return para_data

def get_test_statistics(lines):
	"""
	Extracts test statistics (Chi-Squared and DOF) from the lines.
	Args:
		lines (list): Lines of text to search for parameters.
	Returns:
		Dict: Extracted parameter data with value and error.
	"""
	ts_data = {}
	num_pattern = r"\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b"

	chi_val = re.findall(num_pattern, lines[-2])
	dof_val = re.findall(num_pattern, lines[-1])

	if chi_val and dof_val:
		ts_data["Chi-Squared"] = chi_val[0]
		ts_data["DOF"] = dof_val[1]
	else:
		print(f"> Warning: test statistics values not found in the lines.")

	return ts_data

def read_xspec_log(loglist, opath):
	"""
	Reads XSPEC log files, extracts model parameters, and writes them to a YAML file.
	Args:
		loglist (list): List of paths to XSPEC log files.
		opath (str): Path to save the output YAML file.
	Returns:
		Dict: model parameters and test statistics.
	"""
	model_data = {}
	models = {
		"logpar": ["alpha", "beta", "pivotE", "norm"],
		"powerlaw": ["PhoIndex", "norm"],
		"bknpower": ["PhoIndx1", "BreakE", "PhoIndx2", "norm"]}

	for lfile in loglist:
		with open(lfile, 'r') as file:
			lcontent = file.read()

		sections = re.split(r"={10,}", lcontent)
		mcontent = sections[-1]

		for model, param in models.items():
			if model in mcontent:
				lines = mcontent.strip().split('\n')
				model_data[model] = {"parameters": get_mparameters(lines, param), "test_statistics": get_test_statistics(lines)}
				break

	# with open(f"{opath}/model_pms.yaml", 'w') as file:
	# 	yaml.dump(model_data, file, sort_keys=False, default_flow_style=False)

	return model_data

def extract_pm(data):
	"""
	Extracts model parameters from the given data and returns a DataFrame.
	Args:
		data (dict): The loaded YAML data containing model parameters.
	Returns:
		pd.DataFrame: A DataFrame
	"""
	pm_data = []
	for mname, minfo in data.items():
		for param, values in minfo["parameters"].items():
			pm_data.append([mname, param, values["value"], values["error"]])
	pmdf = pd.DataFrame(pm_data, columns=["Model", "Parameter", "Value", "Error"])

	return pmdf

def extract_ts(data):
	"""
	Extracts test statistics from the data and returns a DataFrame.
	"""
	ts_data = []
	for mname, minfo in data.items():
		chi_val = float(minfo["test_statistics"]["Chi-Squared"])
		dof_val = float(minfo["test_statistics"]["DOF"])
		rcs_val = round(chi_val / dof_val, 4)
		ts_data.append([mname, chi_val, dof_val, rcs_val])
	tsdf = pd.DataFrame(ts_data, columns=["Model", "Chi2", "DOF", "RedChi2"])

	return tsdf

def process_df(df, morder):
	"""
	Processes and sorts a DataFrame by the model order.
	Args:
		df (pd.DataFrame): The DataFrame to be processed.
		morder (list): The desired order of the models.
	Returns:
		pd.DataFrame: The sorted DataFrame.
	"""
	df["Model"] = pd.Categorical(df["Model"], categories=morder, ordered=True)
	df = df.sort_values("Model")
	df = df.reset_index(drop=True)

	return df


if __name__ == "__main__":
	# Getting path of the spectrum files as user input
	parser = argparse.ArgumentParser(description="Provide the file path or a text file containing paths for the spectrum data.")
	parser.add_argument('ip_path', type=str, help='Path to the spectrum data directory or a text file with paths')
	args = parser.parse_args()
	ip_path = args.ip_path

	# Checking user input
	try:
		if os.path.isdir(ip_path):
			file_paths = [ip_path]
		elif os.path.isfile(ip_path):
			with open(ip_path, 'r') as file:
				file_paths = [line.strip() for line in file if line.strip()]
		else:
			raise ValueError(f"'{ip_path}' is neither a valid directory nor a file containing paths.")
	except ValueError as e:
		print(f"> Error: {e}")
		exit(1)

	# Running Xspec analysis
	for fpath in file_paths:
		print(f"\n>>> Running Xspec analysis for Obs: {fpath}")

		try:
			# Checking required files 
			src_file = check_file(fpath, "*src.pha")
			rmf_file = check_file(fpath, "*.rmf")
			bkg_file = check_file(fpath, "*bkg.xcm")

			# Xspec analysis
			model1 = model_logpar(src_file, rmf_file, bkg_file, fpath)
			model2 = model_powerlaw(src_file, rmf_file, bkg_file, fpath)
			model3 = model_bknpowerlaw(src_file, rmf_file, bkg_file, fpath)
			if model1 and model2 and model3:
				print("> Xspec analysis are successful. Output files from Xspec are created")
			else:
				print("> Error: XSPEC analysis failed.")

			# Reading Xspec log files
			log_files = glob.glob(os.path.join(fpath, "*xspec.log"))
			if len(log_files) == 3:
				mdata = read_xspec_log(log_files, fpath)
				print("> The Xspec log files checked for model parameters.")
			else:
				raise ValueError(f"Expected 3 Xspec log files in the directory '{fpath}', but found {len(log_files)}.")
		
			# Printing and saving model parameters
			if mdata:
				# Get model parameter and test statistics as tables
				mdf = extract_pm(mdata)
				tdf = extract_ts(mdata)
				# Define model order and process DataFrames (Not really needed)
				morder = ["logpar", "powerlaw", "bknpower"]
				mdf = process_df(mdf, morder)
				tdf = process_df(tdf, morder)
				# Print and save the tables
				print(f"\nThe model parameter table:\n{mdf}\n")
				print(f"The model test statistics table:\n{tdf}\n")
				pname, tname = "model_pm.csv", "model_ts.csv"
				mdf.to_csv(os.path.join(fpath, pname), index=False)
				tdf.to_csv(os.path.join(fpath, tname), index=False)
				print(f"The tables are saved: {pname}, {tname}")
			else:
				print(f"> Error: Model parameters were not collected successfully. Failed to make DataFrames.")
		except Exception as e:
			print(f"> Error: {e}")
			# Log the path of failed analysis
			with open('failed_obs.txt', 'a') as file:
				file.write(f"- {fpath}: {str(e)}\n")
			print(f"> Error logged for {fpath}. Moving to next path.")
			continue