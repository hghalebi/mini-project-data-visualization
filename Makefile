requirmets:
	@echo "Installing requirements"
	sudo apt-get update
	sudo apt-get install python3-pip
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	@echo "Running app"
	streamlit run app.py --server.maxMessageSize=2048
all: requirmets run