# ChangeLog

## [V1.0] - 21-Jan-2025
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
[] generalise the code such that you can use it on any source. 
BUGS:
[x] Ignoring bad channel only working in AllData
[x] Only spectrum plot data is able to save. The ratio plot data is not able to save
[x] the xspec three models are running continuously. So, the spectrum is getting added to next session. How to exit xspec after doing on model.
