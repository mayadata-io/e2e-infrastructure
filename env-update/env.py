# Standard library imports
import os
import argparse

# Third party imports
import yaml


def write_file(path, content):
    try:
        with open(path, 'w+') as f:
            f.write(content)
    except EnvironmentError as e:
        print('File operation failed\nError: %s' % e)
        return '', -1
    return path, 0


def get_file_data(path):
    try:
        with open(path, 'r') as f:
            data = f.read()
    except EnvironmentError as e:
        print('File operation failed, Error: %s' % e)
        exit(-1)
    return data


def parse_yaml(content):
    try:
        r = yaml.load(content)
    except yaml.YAMLError as e:
        print('YAML operation failed\nError: %s' % e)
        exit(-1)
    return r


def populate_yaml_with_env_vars(yaml_info):
    containers = yaml_info['spec']['template']['spec']['containers']
    for container in containers:
        for env in container['env']:
            if os.getenv(env['name']) is not None:
                env['value'] = os.getenv(env['name'])
    return yaml_info


def main():
    parser = argparse.ArgumentParser(
            description='cli tool to replace environment variable'
        )
    parser.add_argument(
            '-f', '--filename', help='filename to be parsed', required=True
        )
    args = vars(parser.parse_args())
    file_data = get_file_data(args['filename'])
    yaml_info = parse_yaml(file_data)
    yaml_info = populate_yaml_with_env_vars(yaml_info)
    _, err = write_file(args['filename'], yaml.dump(yaml_info, default_flow_style=False))
    if err == -1:
        exit(err)


if __name__ == '__main__':
    main()
