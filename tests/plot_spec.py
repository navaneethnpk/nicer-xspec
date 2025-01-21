"""
ABOUT:

TODO:
[] Make function to plot spectrum and/or ratio plot.
[] Make choices: user can choose whether to include ratio plot or not. or (1) only spectrum (2) spectrum and ratio plot
[] Save the plot in publication format

BUG:
"""

import os
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, LogLocator








if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Provide the CSV files path")
	parser.add_argument("ip_path1", type=str, help="CSV file - Spectrum")
	parser.add_argument("ip_path2", type=str, help="CSV file - Ratio")
	args = parser.parse_args()
	ip_path1 = args.ip_path1
	ip_path2 = args.ip_path2

	df_spect = pd.read_csv(ip_path1)
	df_ratio = pd.read_csv(ip_path2)

	x1_col, y1_col, y1e_col, mod1_val = df_spect["xVals"], df_spect["yVals"], df_spect["yErrs"], df_spect["modVals"]
	plt.figure(figsize=(8, 6))

	plt.errorbar(x1_col, y1_col, yerr=y1e_col, fmt="o", markersize=4, label="Data", color="royalblue", ecolor="lightblue", capsize=2, zorder=1)
	plt.plot(x1_col, mod1_val, label="Model", color="crimson", linestyle="-", linewidth=1, zorder=2)

	plt.xlabel("Energy (keV)", fontsize=10)
	plt.ylabel(r"keV$^2$ (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)", fontsize=10)
	plt.title("Spectrum: __ Model", fontsize=12)
	
	plt.xscale("log")
	plt.yscale("log")
	plt.gca().xaxis.set_major_formatter(ScalarFormatter())
	plt.gca().yaxis.set_major_formatter(ScalarFormatter())
	plt.gca().tick_params(axis="x", direction="in", length=3, width=0.5, colors="black", pad=4, which="both", labelsize=8)
	plt.gca().tick_params(axis="y", direction="in", length=3, width=0.5, colors="black", pad=4, which="both", labelsize=8)

	plt.legend()
	plt.tight_layout()
	plt.show()


	x1_col, y1_col, y1e_col, mod1_val = df_spect["xVals"], df_spect["yVals"], df_spect["yErrs"], df_spect["modVals"]
	x2_col, y2_col, y2e_col = df_ratio["xVals"], df_ratio["yVals"], df_ratio["yErrs"]
	plt.rcParams['font.family'] = 'sans-serif'
	fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [7, 3]}, sharex=True)
	fig.suptitle("Spectrum: __ Model", fontsize=12)

	ax1.errorbar(x1_col, y1_col, yerr=y1e_col, fmt="o", markersize=2, label="Data", color="royalblue", ecolor="lightblue", capsize=1, zorder=1)
	ax1.plot(x1_col, mod1_val, label="Model", color="crimson", linestyle="-", linewidth=1, zorder=2)
	# ax1.set_xlabel("Energy (keV)", fontsize=10)
	ax1.set_ylabel(r"keV$^2$ (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)", fontsize=10)
	ax1.set_xscale("log")
	ax1.set_yscale("log")
	ax1.xaxis.set_major_formatter(ScalarFormatter())
	ax1.yaxis.set_major_formatter(ScalarFormatter())
	ax1.xaxis.set_minor_formatter(ScalarFormatter())
	ax1.yaxis.set_minor_formatter(ScalarFormatter())
	ax1.xaxis.set_minor_locator(LogLocator(base=10.0, subs=[0.5], numticks=10))
	ax1.yaxis.set_minor_locator(LogLocator(base=10.0, subs=[0.5], numticks=10))
	ax1.tick_params(axis="x", direction="in", length=3, width=0.5, colors="black", pad=4, which="both", labelsize=8)
	ax1.tick_params(axis="y", direction="in", length=3, width=0.5, colors="black", pad=4, which="both", labelsize=8)
	ax1.legend()


	ax2.errorbar(x2_col, y2_col, yerr=y2e_col, fmt="o", markersize=2, color="seagreen", ecolor="lightgreen", capsize=1, zorder=1)
	ax2.axhline(1.0, color="crimson", linestyle="-", linewidth=1, zorder=2)
	ax2.set_xlabel("Energy (keV)", fontsize=10)
	ax2.set_ylabel(r"Ratio", fontsize=10)
	ax2.set_xscale("log")
	ax2.set_yscale("log")
	ax2.xaxis.set_major_formatter(ScalarFormatter())
	ax2.yaxis.set_major_formatter(ScalarFormatter())
	ax2.xaxis.set_minor_formatter(ScalarFormatter())
	ax2.yaxis.set_minor_formatter(ScalarFormatter())
	ax2.xaxis.set_minor_locator(LogLocator(base=10.0, subs=[0.5], numticks=10))
	ax2.yaxis.set_minor_locator(LogLocator(base=10.0, subs=[0.5], numticks=10))
	ax2.tick_params(axis="x", direction="in", length=3, width=0.5, colors="black", pad=4, which="both", labelsize=8)
	ax2.tick_params(axis="y", direction="in", length=3, width=0.5, colors="black", pad=4, which="both", labelsize=8)

	plt.subplots_adjust(hspace=0.1)
	plt.tight_layout()
	plt.show()
