send-data-package:
	python3 .\test_datapackage.py

host-kmz:
	cd kmz-server-root && python -m http.server 8000 && exit

generate-kmz:
	python3 .\test_kmz.py
