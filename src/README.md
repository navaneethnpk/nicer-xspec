run_xspec.py - To run the pyXspec    
command: `python run_xspec.py obslist.txt`    
Inputs: spectrum file (.pha) and arf, bkg, rmf files.  
Outputs: xspec plot (.ps), spectrum (.csv), ratio (.csv), xspec log file (.log) - for each model.  

read_log.py - Reading the xspec log file  
command: `python read_log.py obslist.txt`  
Inputs: xspec log file.  
Outputs: model_pm.csv - model parameters, model_ts.csv - test statistics, model_fx.csv - flux values.  

plot_spec.py - Plotting the spectrum  
command: `python plot_spec.py obslist.txt`  
Inputs: spectrum and ratio files.  
Outputs: plot (.png) - for each model.  

`obslist.txt`: Text file containing path of the observations  