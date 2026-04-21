import json
import yaml
import csv
import io

def json_to_yaml(json_str: str) -> str:
    """Converts a JSON string to a YAML string."""
    data = json.loads(json_str)
    return yaml.dump(data, sort_keys=False)

def yaml_to_json(yaml_str: str) -> str:
    """Converts a YAML string to a JSON string."""
    data = yaml.safe_load(yaml_str)
    return json.dumps(data, indent=2)

def csv_to_json(csv_str: str) -> str:
    """Converts a CSV string to a JSON string (list of dicts)."""
    reader = csv.DictReader(io.StringIO(csv_str))
    data = list(reader)
    return json.dumps(data, indent=2)

def json_to_csv(json_str: str) -> str:
    """Converts a JSON string (list of dicts) to a CSV string."""
    data = json.loads(json_str)
    if not data:
        return ""
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()
