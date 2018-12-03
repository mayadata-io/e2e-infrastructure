This folder contains the yaml files for fluentd(forwarder and aggregator), elasticsearch and kibana that runs on main cluster. Forwarder collect logs form the cluster and send to aggregator. Aggregator then send the logs to elasticsearch running on same cluster. Elasticsearch also receives logs from other fluentd-aggregators running on another cluster. Ultimately, Kibana visualizes the logs by reading the logs stored in Elasticsearch DB.

---
### Setting Up Elasticsearch and Kibana :

First, we need to deploy **Elasticsearch** statefulset:
`kubectl apply -f https://raw.githubusercontent.com/openebs/e2e-infrastructure/master/production/efk-server/elasticsearch/es-statefulset.yaml`

Then the Elasticsearch service:
`kubectl apply -f https://raw.githubusercontent.com/openebs/e2e-infrastructure/master/production/efk-server/elasticsearch/es-svc.yaml`

Now it’s **Kibana** turn. First’ we’ll apply the deployment:
`kubectl apply -f https://raw.githubusercontent.com/openebs/e2e-infrastructure/master/production/efk-server/kibana/kibana-deployment.yaml`

And then, the Kibana service:
`kubectl apply -f https://raw.githubusercontent.com/openebs/e2e-infrastructure/master/production/efk-server/kibana/kibana-svc.yaml`


Now, since we have the indices  as *cluster-logs-DATE* , we need to make a curl request to Kibana to create the index pattern as **cluster-logs-***.
(Note: We can make the index-pattern from Kibana’s UI also, but the index-pattern-id should be the same, else it won’t be able to find the desired index-pattern-id that is mandatory as we are redirecting the users from *openebs.ci* in logs link with a specified index-pattern-id )
So, the curl request goes like this:

```
curl -XPOST https://e2elogs.openebs.ci/api/saved_objects/index-pattern/8d3d6950-ea9c-11e8-8cff-a161f7929609 -d '
   {
     "attributes": {
       "title": "cluster-logs-*",
       "timeFieldName": "@timestamp"
     }
   }' -H 'Content-Type: application/json' -H 'kbn-xsrf: true'
```
And that's all!   *Gracias! :)*

---
##### Situation when Elasticsearch storage exceeds 80% of the alloted space:
The moment when elasticsearch is unable to store data (that occurs generally after 80+% of storage gets filled) then it sets a variable *read_only_allow_delete* to **true**, which stops pushing any more data to ES. So for re-enabling Elasticsearch to get the data, we need to make a curl request to Elasticsearch to set *read_only_allow_delete* to **false** :
Exec into Elasticsearch Pod and execute the below curl request:
```
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": false}'
```