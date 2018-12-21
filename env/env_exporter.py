#
# Copyright 2018 The OpenEBS Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
#
# Info:
# This Python script can be used to generate the image name with tag
# HOW TO EXPORT:
# $ export OPENEBS_IO_JIVA_CONTROLLER_IMAGE=$(eval python env_exporter.py -f ../baseline/baseline -o jcontroller)
# -o, --option: jcontroller, jreplica, mapi and iovolume

import argparse


def get_maya_detail(commit, option, *args, **kwargs):
    '''
    It takes commit as an input and return corresponding docker_image_name with tag
    If the option doesn't belongs to Maya it will return None
    args and kwargs can be used for passing additional variable and futher customizing the function
    '''
    mayaDetails = ['maya', commit.rstrip('\n')]
    if option == 'mapi':
        return 'openebs/m-apiserver:'+mayaDetails[1]
    if option == 'cvolmgmt':
        return 'openebs/cstor-volume-mgmt:'+mayaDetails[1]
    if option == 'cpoolmgmt':
        return 'openebs/cstor-pool-mgmt:'+mayaDetails[1]
    if option == 'iovolume':
        return 'openebs/m-exporter:'+mayaDetails[1]
    return None


def get_jiva_detail(commit, option, *args, **kwargs):
    '''
        It takes commit as an input and return corresponding docker_image_name with tag
        If the option doesn't belongs to Jiva it will return None
        args and kwargs can be used for passing additional variable and futher customizing the function
    '''
    jivaDetails = ['jiva', commit.rstrip('\n')]
    if option == 'jcontroller':
        return 'openebs/jiva:'+jivaDetails[1]
    if option == 'jreplica':
        return 'openebs/jiva:'+jivaDetails[1]
    return None


def get_cstor_detail(commit, option, *args, **kwargs):
    '''
    It takes commit as an input and return corresponding docker_image_name with tag
    If the option doesn't belongs to Cstor it will return None
    args and kwargs can be used for passing additional variable and futher customizing the function
    '''
    cstorDetails = ['zfs', commit.rstrip('\n')]
    if option == 'cstorpool':
        return 'openebs/cstor-pool:'+cstorDetails[1]
    return None

def get_istgt_detail(commit, option, *args, **kwargs):
    '''
    It takes commit as an input and return corresponding docker_image_name with tag
    If the option doesn't belongs to Cstor it will return None
    args and kwargs can be used for passing additional variable and futher customizing the function
    '''
    istgtDetails = ['istgt', commit.rstrip('\n')]
    if option == 'target':
        return 'openebs/cstor-pool:'+istgtDetails[1]
    return None

def get_ndm_detail(commit, option, *args, **kwargs):
    '''
    It takes commit as an input and return corresponding docker_image_name with tag
    If the option doesn't belongs to Cstor it will return None
    args and kwargs can be used for passing additional variable and futher customizing the function
    '''
    ndmDetails = ['node-disk-manager', commit.rstrip('\n')]
    if option == 'ndm':
        return 'openebs/node-disk-manager-amd64:'+ndmDetails[1]
    return None

def get_es_detail(commit, option, *args, **kwargs):
    '''
    It takes commit as an input and return corresponding docker_image_name with tag
    If the option doesn't belongs to Cstor it will return None
    args and kwargs can be used for passing additional variable and futher customizing the function
    '''
    esDetails = ['external-storage', commit.rstrip('\n')]
    if option == 'provisioner':
        return 'openebs/openebs-k8s-provisioner:'+esDetails[1]
    if option == 'snapprovisioner':
        return 'openebs/snapshot-provisioner:'+esDetails[1]
    if option == 'snapcontroller':
        return 'openebs/snapshot-controller:'+esDetails[1]
    return None

def get_docker_image_name_with_tag(filename, option):
    content = None
    storage_eng_detail_map = {
        'maya': get_maya_detail,
        'jiva': get_jiva_detail,
        'zfs': get_cstor_detail,
        'istgt': get_istgt_detail,
        'node-disk-manager': get_ndm_detail,
        'external-storage' : get_es_detail
    }

    with open(filename, 'r') as f:
        content = f.readlines()

    # Iterate over each commit message
    for line in content:
        # sample line: date=10-12-18,time=18:45:13,repo=maya,branch=master,commit=20364c17
        _, _, repo, branch, commit = line.split(',')
        _, repo_name = repo.split('=')
        _, commit_hash = commit.split('=')
        # getting the corresponding function that can be used to get docker_img_name_with_tag for the repo
        get_docker_img_name_func = storage_eng_detail_map[repo_name]
        data = get_docker_img_name_func(commit_hash, option)
        if data:
            # if the commit belongs to the options that is provided in input.
            return data
    return None


def run(filename, option):
    data = get_docker_image_name_with_tag(filename, option)
    if data:
        print(data)
    else:
        print('It looks like you provided invalid option or there is no commits for the given option')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='returns')
    parser.add_argument('-fp', '--filename', help='Enter the name of file(with path)', required=True)
    parser.add_argument('-o', '--option', help='Enter the repo name', required=True)
    args = vars(parser.parse_args())
    run(args['filename'], args['option'])