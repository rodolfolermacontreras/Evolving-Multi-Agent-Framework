# Evolving Multi-Agent Framework -- developer entry points.
#
# One-command bootstrap for a fresh clone:
#   make setup     -> create .venv, init the local ledger, install the
#                     commit-msg hook, then run lint + the test suite.
#   make doctor    -> one-screen framework health check.

.PHONY: setup doctor

setup:
	python spec-driven-development/cli/bootstrap.py setup

doctor:
	python spec-driven-development/cli/bootstrap.py doctor
