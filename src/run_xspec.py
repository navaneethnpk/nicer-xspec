import os
import re
import sys
import glob
import numpy as np
from xspec import *

def check_file(filepath, pattern):
	file_match = glob.glob(os.path.join(filepath, pattern))
	return file_match[0] if file_match else None

def log_error(errmsg):
	with open('failed_obs.txt', 'a') as file:
		file.write(errmsg)
	return

def run_xspec(pha, rmf, arf, bkg, path, mname):
	ch = Xset.chatter
	Xset.chatter = 0
	lch = Xset.logChatter
	Xset.logChatter = 20
	logFile = Xset.openLog(f"{path}/{mname}_xspec.log")
	logFile = Xset.log

	# Loading data
	s1 = Spectrum(pha)
	s1.response = rmf
	s1.response.arf = arf
	s1.background = bkg
	AllData.ignore("bad")
	s1.ignore("**-0.3,10.0-**")

	# Define model and its parameters
	nh_val = 0.0131
	if mname == "logpar":
		m1 = Model("tbabs*logpar")
		m1.TBabs.nH = nh_val
		m1.TBabs.nH.frozen = True
		m1.logpar.alpha = 1.0
		m1.logpar.beta = 1.0
	elif mname == "powerlaw":
		m1 = Model("tbabs*powerlaw")
		m1.TBabs.nH = nh_val
		m1.TBabs.nH.frozen = True
		m1.powerlaw.PhoIndex = 1.0
	elif mname == "bknpower":
		m1 = Model("tbabs*bknpower")
		m1.TBabs.nH = nh_val
		m1.TBabs.nH.frozen = True
		m1.bknpower.PhoIndx1 = 1.0
		m1.bknpower.PhoIndx2 = 1.0
	else:
		raise ValueError("Unknown model. Check.")

	Fit.nIterations = 100
	Fit.statMethod = "chi"
	Fit.perform()
	Fit.show()

	# Plotting
	Plot.device = f"{path}/{mname}_plot.ps"
	Plot.xAxis = "keV"
	Plot.xLog = True
	Plot.yLog = True
	Plot("eeufspec", "ratio")

	# Saving the spectrum and ratio plot data
	Plot.device = "/null"
	Plot("eeufspec")
	xVals = Plot.x()
	yVals = Plot.y()
	modVals = Plot.model()
	yErrs = Plot.yErr()
	dataM = np.column_stack((xVals, yVals, yErrs, modVals))
	np.savetxt(f"{path}/{mname}_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")
	Plot("ratio")
	xVals = Plot.x()
	yVals = Plot.y()
	yErrs = Plot.yErr()
	dataR = np.column_stack((xVals, yVals, yErrs))
	np.savetxt(f"{path}/{mname}_ratio.csv", dataR, delimiter=",", header="xVals,yVals,yErrs", comments="")

	Xset.save(f"{path}/{mname}_model.xcm", info='m')
	AllData.clear()
	Xset.closeLog()

if __name__ == "__main__":
	ip_path = sys.argv[1]
	with open(ip_path, 'r') as file:
		file_paths = [line.strip() for line in file if line.strip()]

	for fpath in file_paths:
		print(f"\n>>> Running Xspec analysis for Obs: {fpath}")

		try:
			if not os.path.exists(fpath):
				raise FileNotFoundError(f"Path does not exist: {fpath}")

			src_file = check_file(fpath, "*mpu7_sr.pha")
			rmf_file = check_file(fpath, "*mpu7.rmf")
			arf_file = check_file(fpath, "*mpu7.arf")
			bkg_file = check_file(fpath, "*mpu7_bg.xcm")

			model1 = run_xspec(pha=src_file, rmf=rmf_file, arf=arf_file, bkg=bkg_file, path=fpath, mname="logpar")
			model2 = run_xspec(pha=src_file, rmf=rmf_file, arf=arf_file, bkg=bkg_file, path=fpath, mname="powerlaw") 
			model3 = run_xspec(pha=src_file, rmf=rmf_file, arf=arf_file, bkg=bkg_file, path=fpath, mname="bknpower")

		except Exception as e:
			error_msg = f"- {fpath}:: {str(e)}\n"
			log_error(error_msg)
			print(f"> Error: {e}")
			print(f"> Error logged for {fpath}. Moving to next path.")
			continue