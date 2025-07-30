build:
	nuitka --standalone --onefile --output-filename=visa_tracker visa_tracker.py
	nuitka --standalone --onefile --enable-plugin=no-qt --output-filename=visualize_visa_times visualize_visa_times.py