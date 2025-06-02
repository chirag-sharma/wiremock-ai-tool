import json
import logging
import os

def list_yaml_files(input_dir="input"):
    """List all YAML/YML files in the input directory."""
    return [f for f in os.listdir(input_dir) if f.endswith(('.yaml', '.yml'))]

def select_input_file():
    """Prompt user to select a Swagger file from input/ folder."""
    files = list_yaml_files()
    if not files:
        raise FileNotFoundError("No YAML files found in 'input/' directory.")

    print("\nAvailable Swagger/OpenAPI files:")
    for idx, f in enumerate(files, 1):
        print(f"  {idx}. {f}")

    choice = input("\nSelect a file by number: ").strip()
    try:
        selected = files[int(choice) - 1]
        return os.path.join("input", selected)
    except (IndexError, ValueError):
        raise ValueError("Invalid selection. Please choose a valid number.")

def write_json_file(file_path: str, data: list):
    """
    Writes the provided data to a JSON file at the given path.

    Args:
        file_path (str): Output path including filename.
        data (list): A list of WireMock mapping objects (dicts).
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logging.debug(f"✅ Successfully wrote JSON to {file_path}")
    except Exception as e:
        logging.error(f"❌ Failed to write JSON file {file_path}: {e}")
        raise

def read_json_file(path):
    """Reads a JSON file and returns the parsed data."""
    with open(path, "r") as f:
        return json.load(f)