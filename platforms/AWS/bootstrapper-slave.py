import argparse
import os
import shutil
import testrail
import requests
import json

import yaml

ACCESS_RIGHT = 0o755


def create_init_directory(args, plan):
    path = args['base_path'] + "/" + plan['Platform_name']
    return create_directory(path)


def write_file(path, content):
    try:
        file = open(path, "w+")
        file.write(content)
        file.close()
    except EnvironmentError as e:
        print("File operation failed\nError: %s" % e)
        return "", -1
    return path, 0


def save_file(url, path):
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Request for url: %s failed\nError: %s" % (url, e))
        return "", -1
    return write_file(path, r.text)


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
    return 0


def clean_up(path, err):
    if remove_directory(path) == -1:
        print("Cleaning up failed")
    else:
        print("Cleaning up successful")
    print("Bootstrapping unsuccessful")
    exit(err)


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
    if 'Testrail_project_id' not in plans.keys() or 'Platform_name' not in plans.keys():
        print("Error parsing yml file")
        return {}, -1
    return plans, 0


def get_base_path():
    # path = str(os.environ['WORKSPACE'])
    path = os.path.expanduser('~')+"/e2e"
    if len(path) == 0:
        return "", -1
    return path, 0


def get_testrail_client(args, plan):
    client = testrail.APIClient(plan['Test_rail_url'])
    client.user, client.password=args['testrail_username'], args['testrail_password']
    return client


def create_testrail_plan(client, plan):
    plan_name = str(plan['Build_date'] + " " + plan['Build_time'] + " Build-" + plan['Platform_name'] + "-") + str(
        plan['Build_number'])
    description = plan['Description']
    return client.send_post('add_plan/' + str(plan['Testrail_project_id']), {'name': plan_name, 'description': description})


def add_suite(add_suites_args, client):
    suite_id, description, plan_id = add_suites_args['suite_id'], add_suites_args['description'], add_suites_args['Plan_id']
    return client.send_post('add_plan_entry/' + str(plan_id), {'suite_id': suite_id, 'description': description})


def get_cases(get_cases_args, client):
    return client.send_get('get_cases/' + str(get_cases_args['project_id']) + '&suite_id=' + str(get_cases_args['suite_id']))


def create_case_resources(args, create_case_resources_args):
    plan = create_case_resources_args['plan']
    testrail_client = get_testrail_client(args, plan)
    get_cases_args = {'suite_id': create_case_resources_args['suite_id'], 'project_id': plan['Testrail_project_id']}
    cases = get_cases(get_cases_args, testrail_client)
    case_result, master_playbook_result = {}, []
    # Iterating over cases
    for case in cases:
        if len(case['refs'].split(',')) != 3:
            print("Case Id: %s's refs not in correct format" % str(case['id']))
            return {}, [], -1

        #  Splitting url,reponame and issue_number from case reference
        case_result['url'], case_result['reponame'], case_result['issue_number'] = case['refs'].split(',')

        case_result['case_id'] = case['id']

        # Creating directory for test
        tmp_path, err = create_directory(args['workspace_path'] + "/cases/" + str(case['id']))
        if err == -1:
            return {}, [], err

        # Downloading playbook and saving to file
        _, err = save_file(case_result['url'],  tmp_path + "/playbook.yml")
        if err == -1:
            return {}, [], err

        # Linking local yml to master yml
        master_playbook_result.append({'include': "cases/" + str(case['id']) + '/playbook.yml'})

    return case_result, master_playbook_result, 0


def create_suite_resources(args, create_suite_resources_args):
    plan, plan_response = create_suite_resources_args['plan'], create_suite_resources_args['plan_response']
    map_src_id = {}

    testrail_client = get_testrail_client(args, plan)
    master_playbook_yaml = []
    for suite in plan['Test_suite']:
        for suite_name, suite_info in suite.items():

            description = suite_info if suite_info is not None else ""
            add_suite_args = {'suite_id': int(suite_name), 'Plan_id': plan_response['id'], 'description': description}
            tmp_suite = add_suite(add_suite_args, testrail_client)

            if tmp_suite['suite_id'] is None:
                print("Adding suite " + str(suite_name) + " failed")
                return {}, -1

            # Mapping suite_id with run_id
            map_src_id[tmp_suite['suite_id']] = {'run_id': tmp_suite['runs'][0]['id'], 'cases': []}
            create_case_resources_args = {'plan': plan, 'suite_id': int(suite_name)}
            cases_result, case_master_playbook_yaml, err = create_case_resources(args, create_case_resources_args)
            if err == -1:
                return {}, [], err

            # Adding information to maps
            map_src_id[tmp_suite['suite_id']]['cases'].append(
                {'case_id': cases_result['case_id'], 'url': cases_result['url'], 'reponame': cases_result['reponame'],
                 'issue_number': cases_result['issue_number']})

            master_playbook_yaml = master_playbook_yaml + case_master_playbook_yaml

    return map_src_id, master_playbook_yaml, 0


def write_maps(path, maps):
    for filename, value in maps.items():
        _, err = write_file(path + "/" + filename, value)
        if err == -1:
            return err
    return 0


def create_plan_resources(args, plan):
    testrail_client = get_testrail_client(args, plan)
    plan_response = create_testrail_plan(testrail_client, plan)
    if plan_response['id'] is None:
        print("Plan creation failed")
        return -1

    cases_path, err = create_directory(args['workspace_path'] + '/cases')
    if err == -1:
        return err

    create_suite_resources_args = {'plan': plan, 'plan_response': plan_response}
    map_src_id, master_playbook_yml, err = create_suite_resources(args, create_suite_resources_args)
    if err == -1:
        return err
    maps = {'mapping.json': json.dumps(map_src_id),
            'master.yml': yaml.dump(master_playbook_yml, default_flow_style=False)}
    err = write_maps(args['workspace_path'], maps)
    if err == -1:
        return err
    return 0


def driver(args):
    plan, err = parse_yml(args['base_path'] + "/AWS.yml")
    if err == -1:
        return err
    print("Setting up " + plan['Platform_name'])
    workspace_path, err = create_init_directory(args, plan)
    if err == -1:
        return err
    args['workspace_path'] = workspace_path
    err = create_plan_resources(args, plan)
    if err == -1:
        return err
    return 0


def main():
    parser = argparse.ArgumentParser(description="Command Line tool for e2e-slave job")
    parser.add_argument('-tuser', '--testrail-username', help='username for testrail', required=True)
    parser.add_argument('-tpass', '--testrail-password', help='password for testrail', required=True)
    args = vars(parser.parse_args())
    base_path, err = get_base_path()
    if err == -1:
        print("Unable to find workspace variable")
        exit(-1)
    args['base_path'] = base_path
    err = driver(args)
    if err == -1:
        clean_up(args['base_path'], err)
    print("Successfully completed bootstrapper-slave")


if __name__ == "__main__":
    main()
