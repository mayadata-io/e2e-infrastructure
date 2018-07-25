import argparse
from datetime import datetime
import os
import requests
import yaml
import shutil

ACCESS_RIGHT = 0o755


def create_init_directory():
    date = str(datetime.now())[:10]
    path = os.path.expanduser('~') + "/e2e/"
    path, err = create_directory(path)
    return path, err, date


def write_file(path, content):
    try:
        file = open(path, "w+")
        file.write(content)
        file.close()
    except EnvironmentError as e:
        print("File operation failed\nError: %s" % e)
        return "", -1
    return path, 0


def create_directory(path):
    try:
        os.makedirs(path, ACCESS_RIGHT)
    except OSError as e:
        print("Directory %s creation failed\nError: %s " % (path, e))
        return path, -1
    print("Successfully created directory %s" % path)
    return path, 0


def remove_directory(path):
    try:
        shutil.rmtree(path, ignore_errors=True)
    except OSError as e:
        print("Directory %s creation failed\nError: %s" % (path, e))
        return -1
    return 1


def save_file(url, path):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Request for url: %s failed\nError: %s" % (url, e))
        return "", -1
    return write_file(path, r.text)


def get_yml(url, path):
    return save_file(url, path + "/test.yml")


def parse_yml(filename):
    try:
        file = open(filename, 'r')
        plans = yaml.load(file.read())
        file.close()
    except EnvironmentError as e:
        print("File operation failed\nError %s" % e)
        return None, -1
    except yaml.YAMLError as e:
        print("YAML operation failed\nError: %s" % e)
        return None, -1
    if 'TestRailProjectID' not in plans.keys() or 'Platform' not in plans.keys():
        print("Error parsing yml file")
        return {}, -1
    return plans, 0


def create_platform_yml(plans, args):
    project_id = plans['TestRailProjectID']
    path = args['base_path']
    # Iterating over platforms
    for platform in plans['Platform']:
        # Iterating over platform dictionary
        for platform_name, platform_info in platform.items():
            print("Processing " + platform_name)
            platform_yml = {'Testrail_project_id': project_id, 'Build_date': args['date'],
                            'Build_number': args['build_number'],
                            'Platform_name': platform_name,
                            'Build_time': str(datetime.now())[11:16], 'Description': platform_info['Description'],
                            'Test_suite': platform_info['Test Suite'], 'Test_rail_url': args['test_rail_api']}

            _, err = write_file(path + "/" + platform_name + ".yml", yaml.dump(platform_yml, default_flow_style=False))
            if err == -1:
                return err
    return 0


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def clean_up(path, err):
    if remove_directory(path) == -1:
        print("Cleaning up failed")
    else:
        print("Cleaning up successful")
    print("Bootstrapping unsuccessful")
    exit(err)


def main():
    parser = argparse.ArgumentParser(description="Command Line tool for e2e-master job")
    parser.add_argument('-yl', '--yml-url', help="yml location url")
    parser.add_argument('-bn', '--build-number', help="Build number", type=check_positive)
    parser.add_argument('-turl', '--test-rail-api', help='API url of testrail', required=True)
    args = vars(parser.parse_args())
    args['base_path'], err, args['date'] = create_init_directory()
    if err == -1:
        clean_up(args['base_path'], err)
    path, err = get_yml(args['yml_url'], args['base_path'])
    if err == -1:
        clean_up(args['base_path'], err)
    plans, err = parse_yml(path)
    err = create_platform_yml(plans, args)
    if err == -1:
        clean_up(args['base_path'], err)
    print("Successfully completed bootstrapper-master")
    exit(0)


if __name__ == '__main__':
    main()
