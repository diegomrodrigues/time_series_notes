import os
from pathlib import Path

# Define the logical order of linear algebra topics
topic_order = [
    "Differential Equations",
    "Lag Operators",
    "Linear Regression Models",
    "Linear System of Eq",
    "Stationary ARMA",
    "Vector Autoregressions",
    "Covariance Stationary Vector Processes",
    "Deterministic Time Trends",
    "Models of Nonstationary Time Series",
    "Univariate Processes with Unit Roots",
    "Univariate Roots in Multivariate Time Series",
    "Cointegration",
    "Forecasting",
    "Maximum Likelihood Est",
    "Full Information MLE Analysis",
    "Bayesian Analysis",
    "Generalized Method of Moments",
    "Asymptotic Dist. Theory",
    "The Kalman Filter",
    "Time Series of Heteroskedastic",
    "Spectral Analysis"
]

def rename_pdf_in_folder(folder_path):
    """Rename PDF files in the given folder by prepending 'Ref -'"""
    for file in folder_path.glob('*.pdf'):
        if not file.name.startswith('Ref -'):
            new_name = f"Ref - {file.name}"
            try:
                file.rename(folder_path / new_name)
                print(f"Renamed PDF: {file.name} -> {new_name}")
            except Exception as e:
                print(f"Error renaming PDF {file.name}: {e}")

def rename_folders():
    workspace_path = Path.cwd()
    
    for idx, topic in enumerate(topic_order, 1):
        old_path = workspace_path / topic
        new_name = f"{idx:02d}. {topic}"
        new_path = workspace_path / new_name
        
        if old_path.exists():
            try:
                # First rename any PDFs in the current folder
                rename_pdf_in_folder(old_path)
                # Then rename the folder itself
                old_path.rename(new_path)
                print(f"Renamed folder: {topic} -> {new_name}")
            except Exception as e:
                print(f"Error renaming {topic}: {e}")

if __name__ == "__main__":
    rename_folders()
