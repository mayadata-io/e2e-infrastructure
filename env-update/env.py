import argparse
import yaml
from pprint import pprint
import os


def write_file(path, content):
    try:
        file = open(path, "w+")
        file.write(content)
        file.close()
    except EnvironmentError as e:
        print("File operation failed\nError: %s" % e)
        return "", -1
    return path, 0


def get_file_data(path):
    try:
        file = open(path, 'r')
        data = file.read()
        file.close()
    except EnvironmentError as e:
        print("File operation failed, Error: %s" % e)
        exit(-1)
    return data


def parse_yaml(content):
    try:
        r = yaml.load(content)
    except yaml.YAMLError as e:
        print("YAML operation failed\nError: %s" % e)
        exit(-1)
    return r


def main():
    parser = argparse.ArgumentParser(
        description='cli tool to replace environment variable'
    )
    parser.add_argument(
        '-f', '--filename', help='filename to be parsed', required=True
    )
    args = vars(parser.parse_args())
    yaml_info = parse_yaml(get_file_data(args['filename']))
    for container in yaml_info['spec']['template']['spec']['containers']:
        for env in container['env']:
            if os.getenv(env['name']) is not None:
                env['value'] = os.getenv(env['name'])
    _, err = write_file(
        args['filename'], yaml.dump(yaml_info, default_flow_style=False)
    )
    if err == -1:
        exit(err)


if __name__ == "__main__":
    main()
