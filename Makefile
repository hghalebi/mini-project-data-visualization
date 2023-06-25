requirmets:
	@echo "Installing requirements"
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	@echo "Running app"
	streamlit run app.py

all: requirmets run