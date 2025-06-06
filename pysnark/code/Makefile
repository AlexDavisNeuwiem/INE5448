PYTHON := python3
PIP := pip3
VENV_DIR := venv
SRC_DIR := .
REQ_FILE := requirements.txt
TARGET := main.py
INPUT ?=

.PHONY: all run install clean venv

all: install run

# Cria ambiente virtual
venv:
	$(PYTHON) -m venv $(VENV_DIR)

# Instala dependências no ambiente virtual
install: venv
	$(VENV_DIR)/bin/$(PIP) install -r $(REQ_FILE)

# Executa o programa dentro do ambiente virtual
run:
	PYSNARK_BACKEND=snarkjs $(VENV_DIR)/bin/$(PYTHON) $(SRC_DIR)/$(TARGET) $(if $(INPUT),$(INPUT),)

# Limpa ambiente virtual e arquivos temporários
clean:
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete