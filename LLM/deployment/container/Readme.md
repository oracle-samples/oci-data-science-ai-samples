# Container for Serving LLM Apps and Agents with Flask and uWSGI

This directory contains files for building a container image for serving LLM applications on OCI Data Science model deployment service.
* `Dockerfile`: The Dockerfile for building the image based on Oracle Linux 9.
* `requirements.txt`: The Python dependencies for serving the application.
* `app.py`: The Flask application for serving the LLM applications.

This container image will basic LangChain/LangGraph applications, including the LLM/Chat Models for OCI Model Deployment and OCI Generative AI. You may add additional dependencies into `requirements.txt` as needed.
