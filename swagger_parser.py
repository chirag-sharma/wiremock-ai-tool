import yaml
import logging
from collections import defaultdict

def load_and_parse_swagger(file_path):
    """
    Loads the Swagger/OpenAPI file and parses it.
    Returns:
        - parsed_spec: full parsed dict
        - endpoints: dict of path -> method -> YAML snippet
    Raises:
        Exception on invalid format or unsupported version
    """
    try:
        with open(file_path, 'r') as f:
            spec = yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Failed to read YAML: {e}")

    if 'swagger' in spec and spec['swagger'].startswith("2."):
        version = "2.0"
        paths = spec.get("paths", {})
    elif 'openapi' in spec and spec['openapi'].startswith("3."):
        version = "3.x"
        paths = spec.get("paths", {})
    else:
        raise Exception("Unsupported or unrecognized Swagger/OpenAPI version")

    logging.info(f"📘 Detected OpenAPI version: {version}")

    # Build nested structure: { path: { method: snippet } }
    endpoints = {}
    for path, path_item in paths.items():
        methods_dict = {}
        for method, method_block in path_item.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                methods_dict[method.lower()] = method_block
        if methods_dict:
            endpoints[path] = methods_dict

    return spec, endpoints


def extract_yaml_for_endpoint(file_path, selected_path, selected_method):
    """
    Extracts only the YAML snippet corresponding to the selected path + method.
    This is used to feed the LLM a minimal prompt instead of full spec.
    """
    try:
        with open(file_path, 'r') as f:
            all_lines = f.readlines()
    except Exception as e:
        raise Exception(f"Failed to read YAML file: {e}")

    in_path_block = False
    in_method_block = False
    indent_stack = []
    snippet_lines = []

    for idx, line in enumerate(all_lines):
        # Normalize spacing
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue

        if stripped.startswith(selected_path + ":"):
            in_path_block = True
            indent_stack = [len(line) - len(line.lstrip())]
            snippet_lines.append(line)
            continue

        if in_path_block and stripped.startswith(selected_method + ":"):
            in_method_block = True
            indent_stack.append(len(line) - len(line.lstrip()))
            snippet_lines.append(line)
            continue

        if in_method_block:
            current_indent = len(line) - len(line.lstrip())
            if current_indent > indent_stack[-1]:
                snippet_lines.append(line)
            else:
                break  # Method block ends

        elif in_path_block and not in_method_block:
            current_indent = len(line) - len(line.lstrip())
            if current_indent > indent_stack[0]:
                snippet_lines.append(line)
            else:
                break  # Path block ends

    if not snippet_lines:
        raise Exception(f"No YAML found for {selected_method.upper()} {selected_path}")

    return "".join(snippet_lines)
