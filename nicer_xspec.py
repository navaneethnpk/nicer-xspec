"""
TODO:
[x] Function to check files are there or not
[x] Xspec function for model-1 (log parabola)
[x] Xspec function for model-2 (powerlaw)
[x] Xspec function for model-3 (broken powerlaw)
[x] Read the log file and make a json/yaml file for fit statistics
[] make the code for both single obs analysis and a list of obs
[] Make plot from the spectrum and ratio data
[] generalise the code such that you can use it on any source. (make nH, z etc user inputs - no source specific data hardcoded)
[] For Xspec models, many lines are repeating/same. How to make it short? Class?
BUGS:
[] Ignoring bad channel only working in AllData
[x] Only spectrum plot data is able to save. The ratio plot data is not able to save
[] the xspec three models are running continuously. So, the spectrum is getting added to next session. How to exit xspec after doing on model.
"""

import re
import os
import glob
import yaml
import numpy as np
import argparse
from xspec import *
import matplotlib.pyplot as plt

def check_file(filepath, pattern):
	"""
	Checks if exactly one file matching the given pattern exists in the specified directory.
	Args:
		filepath (str): Directory path to search.
		pattern (str): File pattern (e.g., '*.rmf').
	Returns:
		str: Path to the matching file if exactly one is found.
	Raises:
		ValueError: If more than one file matches.
		FileNotFoundError: If no file matches.
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
		# s1.ignore("bad")
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
		Xset.closeLog()

		return True
	except Exception as e:
		print(f"Error: An error in Xspec analysis: {e}")
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
		# s1.ignore("bad")
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
		Xset.closeLog()

		return True
	except Exception as e:
		print(f"Error: An error in Xspec analysis: {e}")
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
		# s1.ignore("bad")
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
		Xset.closeLog()

		return True
	except Exception as e:
		print(f"Error: An error in Xspec analysis: {e}")
		return False

def read_xspec_log(loglist):
	"""
	"""
	model_data = {}
	num_pattern = r"\b\d+\.\d+(?:[eE][+-]?\d{2})?\b"
	for lfile in loglist:
		with open(lfile, 'r') as file:
			lcontent = file.read()

		sections = re.split(r"={10,}", lcontent)
		mcontent = sections[-1]

		if "logpar" in mcontent:
			lpm_lines = mcontent.strip().split('\n')
			lpm_par1_line = [line for line in lpm_lines if "alpha" in line]
			lpm_par1_vals = re.findall(num_pattern, lpm_par1_line[0])
			lpm_par2_line = [line for line in lpm_lines if "beta" in line]
			lpm_par2_vals = re.findall(num_pattern, lpm_par2_line[0])
			lpm_par3_line = [line for line in lpm_lines if "pivotE" in line]
			lpm_par3_vals = re.findall(num_pattern, lpm_par3_line[0])
			lpm_par4_line = [line for line in lpm_lines if "norm" in line]
			lpm_par4_vals = re.findall(num_pattern, lpm_par4_line[0])

			model_data["logpar"] = {
				"alpha": {"value": lpm_par1_vals[0], "error": lpm_par1_vals[1] if len(lpm_par1_vals) > 1 else None},
				"beta": {"value": lpm_par2_vals[0], "error": lpm_par2_vals[1] if len(lpm_par2_vals) > 1 else None},
				"pivotE": {"value": lpm_par3_vals[0], "error": lpm_par3_vals[1] if len(lpm_par3_vals) > 1 else None},
				"norm": {"value": lpm_par4_vals[0], "error": lpm_par4_vals[1] if len(lpm_par4_vals) > 1 else None}}
		elif "powerlaw" in mcontent:
			pl_lines = mcontent.strip().split('\n')
			pl_par1_line = [line for line in pl_lines if "PhoIndex" in line]
			pl_par1_vals = re.findall(num_pattern, pl_par1_line[0])
			pl_par2_line = [line for line in pl_lines if "norm" in line]
			pl_par2_vals = re.findall(num_pattern, pl_par2_line[0])

			model_data["powerlaw"] = {
				"PhoIndex": {"value": pl_par1_vals[0], "error": pl_par1_vals[1] if len(pl_par1_vals) > 1 else None},
				"norm": {"value": pl_par2_vals[0], "error": pl_par2_vals[1] if len(pl_par2_vals) > 1 else None}}
		elif "bknpower" in mcontent:
			bkn_lines = mcontent.strip().split('\n')
			bkn_par1_line = [line for line in bkn_lines if "PhoIndx1" in line]
			bkn_par1_vals = re.findall(num_pattern, bkn_par1_line[0])
			bkn_par2_line = [line for line in bkn_lines if "BreakE" in line]
			bkn_par2_vals = re.findall(num_pattern, bkn_par2_line[0])
			bkn_par3_line = [line for line in bkn_lines if "PhoIndx2" in line]
			bkn_par3_vals = re.findall(num_pattern, bkn_par3_line[0])
			bkn_par4_line = [line for line in bkn_lines if "norm" in line]
			bkn_par4_vals = re.findall(num_pattern, bkn_par4_line[0])

			model_data["bknpower"] = {
				"PhoIndx1": {"value": bkn_par1_vals[0], "error": bkn_par1_vals[1] if len(bkn_par1_vals) > 1 else None},
				"BreakE": {"value": bkn_par2_vals[0], "error": bkn_par2_vals[1] if len(bkn_par2_vals) > 1 else None},
				"PhoIndx2": {"value": bkn_par3_vals[0], "error": bkn_par3_vals[1] if len(bkn_par3_vals) > 1 else None},
				"norm": {"value": bkn_par4_vals[0], "error": bkn_par4_vals[1] if len(bkn_par4_vals) > 1 else None}}		

	# Save the data to a YAML file
	with open("model_parameters.yaml", 'w') as file:
		yaml.dump(model_data, file)


	return

if __name__ == "__main__":
	# Getting path of the spectrum files as user input
	parser = argparse.ArgumentParser(description="Provide the file path or a text file containing paths for the spectrum data.")
	parser.add_argument('ip_path', type=str, help='Path to the spectrum data directory or a text file with paths')
	args = parser.parse_args()
	ip_path = args.ip_path

	out_path = ip_path

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
		print(f"Error: {e}")
		exit(1)

	# Running Xspec analysis
	for fpath in file_paths:
		"""
		try: 
			src_file = check_file(fpath, "*src.pha")
			rmf_file = check_file(fpath, "*.rmf")
			bkg_file = check_file(fpath, "*bkg.xcm")

			# Xspec analysis
			model1 = model_logpar(src_file, rmf_file, bkg_file, out_path)
			print(f"model1: {model1}")
			model2 = model_powerlaw(src_file, rmf_file, bkg_file, out_path)
			print(f"model2: {model2}")
			model3 = model_bknpowerlaw(src_file, rmf_file, bkg_file, out_path)
			print(f"model3: {model3}")
		except (ValueError, FileNotFoundError) as e:
			print(f"Error: {e}")
			continue
		"""
		# Reading Xspec log files
		try:
			log_files = glob.glob(os.path.join(fpath, "*xspec.log"))
			if len(log_files) == 3:
				read_xspec_log(log_files)
			else:
				raise ValueError(f"Expected 3 Xspec log files in the directory '{fpath}', but found {len(log_files)}.")
		except ValueError as e:
			print(f"Error: {e}")
			continue 
