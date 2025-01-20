"""
TODO:
[x] Function to check files are there or not
[x] Xspec function for model-1 (log parabola)
[x] Xspec function for model-2 (powerlaw)
[x] Xspec function for model-3 (broken powerlaw)
[] Read the log file and make a json/yaml file for fit statistics
[] Make plot from the spectrum and ratio data
[] make the code for both single obs analysis and a list of obs
[] generalise the code such that you can use it on any source. (make nH, z etc user inputs - no source specific data hardcoded)
[] For Xspec models, many lines are repeating/same. How to make it short? Class?
BUGS:
[] Ignoring bad channel only working in AllData
[] Only spectrum plot data is able to save. The ratio plot data is not able to save
"""

import os
import glob
import numpy as np
import argparse
from xspec import *
import matplotlib.pyplot as plt

def check_file(fpath, pattern):
	"""
	Checks if exactly one file matching the given pattern exists in the specified directory.
	Args:
		fpath (str): Directory path to search.
		pattern (str): File pattern (e.g., '*.rmf').
	Returns:
		str: Path to the matching file if exactly one is found.
	Raises:
		ValueError: If more than one file matches.
		FileNotFoundError: If no file matches.
	"""
	file_match = glob.glob(os.path.join(fpath, pattern))
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


if __name__ == "__main__":
	# Getting path of the spectrum files as user input
	parser = argparse.ArgumentParser(description="Provide the file path for the spectrum data.")
	parser.add_argument('file_path', type=str, help='Path to the data files')
	args = parser.parse_args()
	file_path = args.file_path

	# out_path = file_path
	out_path = "/home/student/GitHome/nicer-xspec/outp"

	# Checking files are present or not
	try: 
		src_file = check_file(file_path, "*src.pha")
		rmf_file = check_file(file_path, "*.rmf")
		bkg_file = check_file(file_path, "*bkg.xcm")

		# Xspec analysis
		model1 = model_logpar(src_file, rmf_file, bkg_file, out_path)
		print(f"model1: {model1}")
		model2 = model_powerlaw(src_file, rmf_file, bkg_file, out_path)
		print(f"model2: {model2}")
		model3 = model_bknpowerlaw(src_file, rmf_file, bkg_file, out_path)
		print(f"model3: {model3}")
	except (ValueError, FileNotFoundError) as e:
		print(f"Error: {e}")
		exit(1)