import re
import os
import sys
import glob
import yaml
import numpy as np
import pandas as pd


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

def log_error(errmsg):
	"""
	Helper function for logging errors
	"""
	with open('failed_logs.txt', 'a') as file:
		file.write(errmsg)
	return

if __name__ == "__main__":
	ip_path = sys.argv[1]
	with open(ip_path, 'r') as file:
		file_paths = [line.strip() for line in file if line.strip()]

	for fpath in file_paths:
		print(f"\n>>> Running Xspec analysis for Obs: {fpath}")

		try:
			# Reading Xspec log files
			log_files = glob.glob(os.path.join(fpath, "*xspec.log"))
			if len(log_files) != 3:
				raise ValueError(f"Expected 3 Xspec log files, but found {len(log_files)}.")
			mdata = read_xspec_log(log_files, fpath)
			if not mdata:
				raise ValueError("Model parameters were not collected successfully.")

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
			mdf.to_csv(os.path.join(fpath, "model_pm.csv"), index=False)
			tdf.to_csv(os.path.join(fpath, "model_ts.csv"), index=False)
		except Exception as e:
			error_msg = f"- {fpath}:: {str(e)}\n"
			log_error(error_msg)
			print(f"> Error: {e}")
			print(f"> Error logged for {fpath}. Moving to next path.")
			continue