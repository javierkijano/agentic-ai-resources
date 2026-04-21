import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../core/logic')))
import converters

def test_json_to_yaml():
    json_str = '{"name": "test", "value": 123}'
    yaml_str = converters.json_to_yaml(json_str)
    assert "name: test" in yaml_str
    assert "value: 123" in yaml_str

def test_yaml_to_json():
    yaml_str = "name: test\nvalue: 123"
    json_str = converters.yaml_to_json(yaml_str)
    data = json.loads(json_str)
    assert data["name"] == "test"
    assert data["value"] == 123

def test_csv_to_json():
    csv_str = "name,value\ntest,123\n"
    json_str = converters.csv_to_json(csv_str)
    data = json.loads(json_str)
    assert data[0]["name"] == "test"
    assert data[0]["value"] == "123"

def test_json_to_csv():
    json_str = '[{"name": "test", "value": "123"}]'
    csv_str = converters.json_to_csv(json_str)
    assert "name,value" in csv_str
    assert "test,123" in csv_str

if __name__ == '__main__':
    test_json_to_yaml()
    test_yaml_to_json()
    test_csv_to_json()
    test_json_to_csv()
    print("All converters tests passed!")
