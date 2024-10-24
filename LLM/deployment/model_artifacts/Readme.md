# Artifacts for Deploying LLM Apps and Agents

This directory contains model artifacts and examples for deploying LLM apps and agents with OCI Data Science Model Deployment Service.
* `score.py`. This is the module handling the requests and invoking the user modules.
* `runtime.yaml`. This file is currently not used but reserved for the future developments.

To add your application, simply add a Python module containing your application with an `invoke()` function.

The following files are example applications:
* `app.py`, a bare minimum app.
* `translate.py`, a LangChain app translating English to French.
* `exchange_rate.py`, a LangChain agent which can answer question with real time exchange rate.
* `graph.py`, a LangGraph multi-agent example.
