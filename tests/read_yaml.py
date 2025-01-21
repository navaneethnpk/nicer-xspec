"""
ABOUT:

TODO:
[] Make function to read the yaml file

BUG:
"""

import os
import glob
import yaml
import argparse
import pandas as pd

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
	parser = argparse.ArgumentParser(description="Provide the YAML file path")
	parser.add_argument("ip_path", type=str, help="YAML file")
	args = parser.parse_args()
	ip_path = args.ip_path

	with open(ip_path, "r") as file:
		data = yaml.safe_load(file)

	# Get model parameter and test statistics as tables
	mdf = extract_pm(data)
	tdf = extract_ts(data)
	
	# Define model order and process DataFrames (Not really needed)
	morder = ["logpar", "powerlaw", "bknpower"]
	mdf = process_df(mdf, morder)
	tdf = process_df(tdf, morder)

	# Print the tables
	print(f"The model parameter table:\n{mdf}\n")
	print(f"The model test statistics table:\n{tdf}\n")

	pname, tname = "model_pm.csv", "model_ts.csv"
	mdf.to_csv(pname, index=False)
	tdf.to_csv(tname, index=False)
	print(f"The tables are saved: {pname}, {tname}")
