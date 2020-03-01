clean:
	@find . -depth -type d -name '__pycache__' -exec rm -fr {} \;
	@rm -fr pyan.egg-info

#
# QA
#
qa_lines_count:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

qa_check_code:
	@flake8 pyan/*.py

