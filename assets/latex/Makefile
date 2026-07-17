TEX := pdflatex
JOB := ZhaominWu
OUT_DIR := ../pdf
BUILD_DIR := build
PYTHON ?= python3
GENERATOR := ../../scripts/build_cv_content.py
CONTENT_SOURCES := \
	../../_data/content/profile.yml \
	../../_data/content/site.yml \
	$(wildcard ../../_data/content/cv/*.yml) \
	$(wildcard ../../_data/content/service/*.yml) \
	../../_data/content/teaching.yml \
	../../_data/content/mentoring.yml \
	../../_data/content/talks.yml \
	$(wildcard ../../_data/content/publications/*.bib)
SOURCES := $(JOB).tex resume.cls $(GENERATOR) $(CONTENT_SOURCES) $(wildcard generated/*.tex)

.PHONY: all clean watch content validate

all: $(OUT_DIR)/$(JOB).pdf

content:
	$(PYTHON) $(GENERATOR) build

validate:
	$(PYTHON) $(GENERATOR) validate

$(OUT_DIR)/$(JOB).pdf: content $(SOURCES) | $(OUT_DIR) $(BUILD_DIR)
	$(TEX) -interaction=nonstopmode -halt-on-error -jobname=$(JOB) -output-directory=$(BUILD_DIR) $(JOB).tex
	$(TEX) -interaction=nonstopmode -halt-on-error -jobname=$(JOB) -output-directory=$(BUILD_DIR) $(JOB).tex
	cp $(BUILD_DIR)/$(JOB).pdf $@

$(OUT_DIR) $(BUILD_DIR):
	mkdir -p $@

clean:
	rm -rf $(BUILD_DIR)

watch:
	../../build_cv_pdf.sh watch
