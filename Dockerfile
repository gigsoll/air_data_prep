FROM jupyter/datascience-notebook:latest

# 1. Install LSP & Python Language Server
# 2. Install a pretty theme (e.g., Catppuccin)
RUN pip install --no-cache-dir jupyterlab-lsp 'python-lsp-server[all]' jupyterlab-gruvbox-dark jupyterthemes

# Expose the work directory
WORKDIR /home/jovyan/work
