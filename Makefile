# scurry — Makefile
#
# Build and tooling targets for the scurry project, for AppleScript and Python macros stuff.
#
# --- Variables ---
VENV_DIR = .venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
ACTIVATE = . $(VENV_ACTIVATE)
PIP = $(ACTIVATE) && pip
SETUP_STAMP = $(VENV_DIR)/.setup_stamp

# KarabinerConverter paths
KE_SCRIPT    = scripts/KarabinerConverter/karabiner_converter.py
KE_DATA      = data/KarabinerConverter
KE_BUILD     = build/KarabinerConverter
KE_DEPLOY    = $(HOME)/.config/karabiner/assets/complex_modifications

# --- Phony targets ---
.PHONY: all setup build run clean format showtree gentree filesdump help test test-verbose
.PHONY: karabiner-export karabiner-import karabiner-deploy

# Default target
all: setup

# --- Python Virtual Environment ---

$(VENV_ACTIVATE):
	python3 -m venv $(VENV_DIR)

$(SETUP_STAMP): $(VENV_ACTIVATE) requirements.txt
	@echo "--- Installing Python dependencies ---"
	$(PIP) install -r requirements.txt
	@echo "--- Setup complete ---"
	@touch $(SETUP_STAMP)

setup: $(SETUP_STAMP) ## Create venv and install Python dependencies

# --- Testing ---

test: $(SETUP_STAMP) ## Run Python tests (quiet mode)
	$(ACTIVATE) && pytest -q

test-verbose: $(SETUP_STAMP) ## Run Python tests with verbose output
	$(ACTIVATE) && pytest -v -s

# --- Code Formatting ---

format: ## Format Python (black) files
	@echo "--- Formatting Python ---"
	$(ACTIVATE) && black tools/

# --- App helpers ---

# --- AppleScript Build ---

build: ## Compile plain-text AppleScripts to runnable .scpt files
	@echo "--- Compiling AppleScripts ---"
	@mkdir -p build/MailExporter
	osacompile -o build/MailExporter/export_mail.scpt macros/MailExporter/export_mail.applescript
	@echo "--- Build complete. Executables are in build/ ---"

clean-build: ## Remove compiled scripts
	rm -rf build/

# --- KarabinerConverter ---

karabiner-export: $(SETUP_STAMP) ## Convert KE rules xlsx → json
	@mkdir -p $(KE_BUILD)
	$(ACTIVATE) && python $(KE_SCRIPT) xlsx2json $(KE_DATA)/rules.xlsx $(KE_BUILD)/rules.json

karabiner-import: $(SETUP_STAMP) ## Import KE rules json → xlsx (from complex_modifications)
	$(ACTIVATE) && python $(KE_SCRIPT) json2xlsx $(KE_DEPLOY)/rules.json $(KE_DATA)/rules.xlsx

karabiner-deploy: karabiner-export ## Export + deploy rules to Karabiner Elements
	@if [ -f "$(KE_DEPLOY)/rules.json" ]; then \
		mkdir -p bak; \
		cp "$(KE_DEPLOY)/rules.json" "bak/rules_$$(date +%Y%m%d_%H%M%S).json"; \
		echo "--- Backed up existing rules to bak/ ---"; \
	fi
	@mkdir -p "$(KE_DEPLOY)"
	cp $(KE_BUILD)/rules.json "$(KE_DEPLOY)/rules.json"
	@echo "--- Deployed to $(KE_DEPLOY)/rules.json ---"
	@echo "--- Now remove and re-enable the ruleset in Karabiner Elements ---"

# --- Utility Targets ---

clean: ## Remove venv, cache, and tmp files
	rm -rf $(VENV_DIR) .pytest_cache tmp
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +

showtree: ## Show project directory structure
	@tree -I "node_modules|dist|build|.git|.idea|.vscode|.venv|__pycache__|tmp|cache|*egg-info|DerivedData|xcuserdata" -L 3

gentree: ## Save tree structure to tmp/project-tree.txt
	@mkdir -p tmp
	@tree -I "node_modules|dist|build|.git|.idea|.vscode|.venv|__pycache__|tmp|cache|*egg-info|DerivedData|xcuserdata" > tmp/project-tree.txt
	@echo "Project tree saved to tmp/project-tree.txt"

filesdump: gentree ## Create context dump for LLMs
	@echo "--- Generating filesdump ---"
	$(ACTIVATE) && python tools/concat_files.py manifest.lst > tmp/filesdump.txt
	@echo "Filesdump created at tmp/filesdump.txt"

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
