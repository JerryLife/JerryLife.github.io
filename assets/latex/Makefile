TEX := pdflatex
JOB := ZhaominWu
OUT_DIR := ../pdf
BUILD_DIR := build
SOURCES := main.tex resume.cls $(wildcard sections/*.tex)

.PHONY: all clean

all: $(OUT_DIR)/$(JOB).pdf

$(OUT_DIR)/$(JOB).pdf: $(SOURCES) | $(OUT_DIR) $(BUILD_DIR)
	$(TEX) -interaction=nonstopmode -halt-on-error -jobname=$(JOB) -output-directory=$(BUILD_DIR) main.tex
	$(TEX) -interaction=nonstopmode -halt-on-error -jobname=$(JOB) -output-directory=$(BUILD_DIR) main.tex
	cp $(BUILD_DIR)/$(JOB).pdf $@

$(OUT_DIR) $(BUILD_DIR):
	mkdir -p $@

clean:
	rm -rf $(BUILD_DIR)
