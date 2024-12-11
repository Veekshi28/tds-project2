# Importing essential modules
import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import httpx
import chardet

# API Configuration
API_ENDPOINT = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIyZjMwMDA0NDhAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.poWui37OxCs-EgxkK0_i382_ckWLbW_8xdrIVIaUr2s"

def read_csv_with_encoding(file_path):
    """
    Reads a CSV file while detecting its encoding.
    """
    with open(file_path, 'rb') as file:
        detected = chardet.detect(file.read())
    return pd.read_csv(file_path, encoding=detected['encoding'])

def perform_analysis(dataframe):
    """
    Performs a basic analysis on the DataFrame.
    Returns descriptive statistics, missing value count, and correlation data.
    """
    numeric_data = dataframe.select_dtypes(include=['number'])
    return {
        'summary': dataframe.describe(include='all').to_dict(),
        'missing_values': dataframe.isnull().sum().to_dict(),
        'correlation': numeric_data.corr().to_dict()
    }

def create_visualizations(dataframe):
    """
    Creates and saves distribution plots for numeric columns in the DataFrame.
    """
    sns.set_theme(style="whitegrid")
    numeric_cols = dataframe.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        plt.figure()
        sns.histplot(dataframe[col].dropna(), kde=True)
        plt.title(f'Distribution of {col}')
        plt.savefig(f'{col}_distribution.png')
        plt.close()

def generate_text_report(analysis_results):
    """
    Generates a narrative based on analysis results using an external API.
    """
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": f"Analyze the data: {analysis_results}"}]
    }

    try:
        response = httpx.post(API_ENDPOINT, headers=headers, json=payload, timeout=30.0)
        response.raise_for_status()
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', "No response content.")
    except httpx.HTTPStatusError as err:
        print(f"HTTP error: {err}")
    except httpx.RequestError as err:
        print(f"Request error: {err}")
    except Exception as err:
        print(f"Unexpected error: {err}")
    return "Failed to generate narrative."

def execute_pipeline(file_path):
    """
    Orchestrates the data analysis pipeline from loading data to generating a narrative.
    """
    # Step 1: Load the dataset
    dataset = read_csv_with_encoding(file_path)
    
    # Step 2: Analyze the dataset
    analysis_results = perform_analysis(dataset)
    
    # Step 3: Visualize data distributions
    create_visualizations(dataset)
    
    # Step 4: Generate a narrative
    narrative = generate_text_report(analysis_results)
    
    # Step 5: Save the narrative to a file
    with open('README.md', 'w') as output_file:
        output_file.write(narrative)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <path_to_dataset.csv>")
        sys.exit(1)
    
    execute_pipeline(sys.argv[1])
