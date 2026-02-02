build:
	uv run python3 -m nuitka --standalone --onefile --output-filename=visa_tracker visa_tracker.py
	uv run python3 -m nuitka --standalone --onefile --enable-plugin=no-qt --output-filename=visualize_visa_times visualize_visa_times.py
clean:
	rm -r visa_tracker.build visa_tracker.dist visa_tracker.onefile-build visualize_visa_times.build visualize_visa_times.dist visualize_visa_times.onefile-build