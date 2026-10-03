HUGO ?= hugo

.PHONY: build check serve clean

build:
	$(HUGO) --minify --gc --printI18nWarnings --printPathWarnings

check: build
	python3 ci/check_urls.py public
	python3 ci/check_contrast.py assets/css/site.css
	python3 ci/check_output.py public
	python3 ci/check_budget.py public

serve:
	$(HUGO) server

clean:
	rm -rf public resources
