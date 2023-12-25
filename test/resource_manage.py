import os
import sys
import subprocess
import yaml

dir_path = os.path.dirname(os.path.realpath(__file__))
serverless_functions_dir = os.path.join(
    dir_path, "serverless-functions/Parsec")


def get_knative_serverless_names():
    result = subprocess.run(["kubectl", "get", "ksvc", "-n", "blackscholes", "-o",
                            "jsonpath='{.items[*].metadata.name}'"], text=True, capture_output=True)
    if result.returncode == 0:
        return result.stdout.strip().strip("'").split()
    else:
        print(
            f"Error al obtener los nombres de los servicios: {result.stderr}")
        sys.exit(1)


def get_knative_pods_names():
    result = subprocess.run(["kubectl", "get", "pods", "-n", "blackscholes", "-o",
                            "jsonpath='{.items[*].metadata.name}'"], text=True, capture_output=True)
    if result.returncode == 0:
        return result.stdout.strip().strip("'").split()
    else:
        print(
            f"Error al obtener los nombres de los pods: {result.stderr}")
        sys.exit(1)


def load_and_save_yaml(file, limit_cpu, limit_memory, request_cpu, request_memory):
    file_path = os.path.join(serverless_functions_dir, f"{file}.yaml")
    with open(file_path, 'r') as stream:
        try:
            yaml_data = yaml.safe_load(stream)
            yaml_data['spec']['template']['spec']['containers'][0]['resources'] = {
                'limits': {
                    'cpu': limit_cpu,
                    'memory': limit_memory
                },
                'requests': {
                    'cpu': request_cpu,
                    'memory': request_memory
                }
            }
        except yaml.YAMLError as exc:
            print(f"Error al cargar el archivo YAML {file}: {exc}")
            sys.exit(1)

    with open(file_path, 'w') as outfile:
        yaml.dump(yaml_data, outfile, default_flow_style=False)


def apply_yaml(file):
    file_path = os.path.join(serverless_functions_dir, f"{file}.yaml")
    result = subprocess.run(
        ["kn", "service", "apply", "-f", file_path, "-n", "blackscholes"], text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error al aplicar el archivo YAML {file}: {result.stderr}")
