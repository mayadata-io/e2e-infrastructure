#!/bin/bash -x
# Copyright 2017 OpenEBS Authors 
# Made minor modifications to make this work with OpenEBS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#source $CCPROOT/examples/envvars.sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#$DIR/cleanup.sh

# create the service account used in the containers
kubectl create -f $DIR/set-sa.json

# For version Kube 1.6, we must allow the service account to perform
# a label command. For this example, OpenEBS opens up wide permissions
# for all service accounts. This is NOT for production!
kubectl create clusterrolebinding permissive-binding \
  --clusterrole=cluster-admin \
  --user=admin \
  --user=kubelet \
  --group=system:serviceaccounts

# create the services for the example
kubectl create -f $DIR/set-service.json
kubectl create -f $DIR/set-primary-service.json
kubectl create -f $DIR/set-replica-service.json
kubectl create -f $DIR/set.json
