import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter, LogLocator

def plot_axsetup(ax, xlabel=None, ylabel=None):
	"""
	Configure the axes of a matplotlib plot with the specified scales and labels.
	"""
	ax.set_xscale("log")
	ax.set_yscale("log")
	ax.xaxis.set_major_formatter(ScalarFormatter())
	ax.yaxis.set_major_formatter(ScalarFormatter())
	ax.xaxis.set_minor_formatter(ScalarFormatter())
	ax.yaxis.set_minor_formatter(ScalarFormatter())
	ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=[0.5], numticks=10))
	ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=[0.5], numticks=10))
	ax.tick_params(axis="both", direction="in", length=3, width=0.5, colors="black", pad=4, which="both", labelsize=8)
	if xlabel:
		ax.set_xlabel(xlabel, fontsize=10)
	if ylabel:
		ax.set_ylabel(ylabel, fontsize=10)
	return

def plot_spectrum(df_spect, fpath, mname, df_ratio=None, single_plot=False):
	"""
	Plot a spectrum with optional ratio data in either a single or dual plot layout.
	"""
	iname = os.path.join(fpath, f"{mname}_plot.png")

	x1, y1, y1e, mdl = df_spect["xVals"], df_spect["yVals"], df_spect["yErrs"], df_spect["modVals"]

	if single_plot:
		fig, ax = plt.subplots(figsize=(8, 6))
		ax.errorbar(x1, y1, yerr=y1e, fmt="o", markersize=4, label="Data", color="royalblue", ecolor="lightblue", elinewidth=1, capsize=1)
		ax.plot(x1, mdl, label="Model", color="crimson", linestyle="-", linewidth=1)
		plot_axsetup(ax, xlabel="Energy (keV)", ylabel=r"keV$^2$ (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)")
		ax.legend()
	else:
		x2, y2, y2e = df_ratio["xVals"], df_ratio["yVals"], df_ratio["yErrs"]
		fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [7, 3]}, sharex=True)
		
		ax1.errorbar(x1, y1, yerr=y1e, fmt="o", markersize=2, label="Data", color="royalblue", ecolor="lightblue", elinewidth=1, capsize=1)
		ax1.plot(x1, mdl, label="Model", color="crimson", linestyle="-", linewidth=1)
		plot_axsetup(ax1, ylabel=r"keV$^2$ (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)")
		ax1.legend()

		ax2.errorbar(x2, y2, yerr=y2e, fmt="o", markersize=2, color="seagreen", ecolor="lightgreen", elinewidth=1, capsize=1)
		ax2.axhline(1.0, color="crimson", linestyle="-", linewidth=1)
		plot_axsetup(ax2, xlabel="Energy (keV)", ylabel="Ratio")

		plt.subplots_adjust(hspace=0.1)

	fig.suptitle(f"Spectrum: {mname} Model", fontsize=12)
	plt.tight_layout()
	plt.savefig(iname, dpi=300, bbox_inches="tight")
	# plt.show()

def log_error(errmsg):
	"""
	Helper function for logging errors
	"""
	with open('failed_plots.txt', 'a') as file:
		file.write(errmsg)
	return


if __name__ == "__main__":
	ip_path = sys.argv[1]
	with open(ip_path, 'r') as file:
		file_paths = [line.strip() for line in file if line.strip()]

	for fpath in file_paths:
		print(f"\n>>> Making spectrum plot for Obs: {fpath}")
		try:
			morder = ["logpar", "powerlaw", "bknpower"]
			for m in morder:
				scsv = os.path.join(fpath, f"{m}_spec.csv")
				rcsv = os.path.join(fpath, f"{m}_ratio.csv")

				df_spect = pd.read_csv(scsv)
				df_ratio = pd.read_csv(rcsv)

				plot_spectrum(df_spect=df_spect, fpath=fpath, mname=m, df_ratio=df_ratio)
		except Exception as e:
			error_msg = f"- {fpath}:: {str(e)}\n"
			log_error(error_msg)
			print(f"> Error: {e}")
			print(f"> Error logged for {fpath}. Moving to next path.")
			continue

