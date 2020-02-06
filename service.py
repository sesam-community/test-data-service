from flask import Flask, request, jsonify, Response
import json
import requests
import os
import sys
from sesamutils import VariablesConfig, sesam_logger
import pandas as pd
import random
import urllib3

app = Flask(__name__)
logger = sesam_logger("Steve the logger", app=app)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## Helpers
required_env_vars = ['jwt', 'base_url']

def draw_representative_values(enteties,k=100,pseudonym=False):
    df = pd.DataFrame(enteties)
    if "_id" in df.columns:
        del df["_id"]
    new_df = pd.DataFrame(['test_entity_{}'.format(i) for i in range(k)])
    cols = [col for col in list(df.columns)]
    for col in cols:
        vals = (df[col].value_counts()/len(df[col]))
        if len(vals) == 0:
            properties = [0,1]
            weights = [0,1]
        else:
            properties = list(vals.index)
            weights = list(vals.values)
        
        new_df = pd.concat([new_df,pd.DataFrame(random.choices(properties, k=k,weights=weights))],axis=1)
    new_df.columns = ['_id'] + cols
    return new_df.to_dict(orient='records')


@app.route('/')
def index():
    output = {
        'service': 'Your personal test data service is up and running',
        'To do': 'Go to /create?pipe_id=<the-pipe-id-you-want-to-create-test-data-for>&entities=50 and let me do your work...',
        'Remember': "Only run me once.. :)",
        'remote_addr': request.remote_addr
    }
    return jsonify(output)


@app.route('/create', methods=['GET','POST'])
def create_embedded_data():
    logger.info(f"Test data service is ready to do your bidding..")
    ## Validating env vars
    config = VariablesConfig(required_env_vars)
    if not config.validate():
        sys.exit(1)
    pipe_id = request.args.get('pipe_id')
    max_entities = int(request.args.get('entities'))
    new_source = None
    return_msg = None
    header = {'Authorization': f'Bearer {config.jwt}', "content_type": "application/json"}
    
    try:
        sesam_config_request = requests.get(f"{config.base_url}/pipes/{pipe_id}/config", headers=header, verify=False)
        json_config_response = json.loads(sesam_config_request.content.decode('utf-8-sig'))
        sesam_entity_request = requests.get(f"{config.base_url}/datasets/{pipe_id}/entities", headers=header, verify=False)
        json_entity_response = json.loads(sesam_entity_request.content.decode('utf-8-sig'))

        embedded_data = []
        entities_to_remove = []
        for entity in json_entity_response[0]:
            if pipe_id not in entity and "_id" not in entity:
                    entities_to_remove.append(entity)
        
        json_entity_response = draw_representative_values(json_entity_response,k=max_entities)
        try:
            for mapping_entity in entities_to_remove:
                for entity in json_entity_response:
                    for sesam_property in list(entity):
                        if mapping_entity == sesam_property:
                            entity.pop(sesam_property)
                        if pipe_id in sesam_property:
                            entity[sesam_property.split(":",1)[1]] = entity.pop(sesam_property)
                        
            #for entity in list(json_entity_response[:max_entities]):
            #    _id = entity.get("_id").split(":",1)[1]
            #    entity['_id'] = _id
        
        except Exception as e:
            logger.error(f"Could not remove unnessary properties from this entity. Failed with : {e}")
        
        new_source = {
            "_id": json_config_response["_id"],
            "type": json_config_response["type"],
            "source": {
                "type": "conditional",
                "alternatives": {
                    "prod": json_config_response["source"],
                    "test": {
                        "type": "embedded",
                        "entities": json_entity_response
                    }
            },
            "condition": "$ENV(node-env)"
            },
            "transform": json_config_response["transform"]
            }
        
        check_response = requests.put(f"{config.base_url}/pipes/{pipe_id}/config?force=True", headers=header, data=json.dumps(new_source), verify=False)
        if not check_response.ok:
            return_msg = f"Unexpected error : {check_response.content}", 500
        else:
            return_msg = f"Your pipe with id : {pipe_id} has been updated with test data"
    
    except Exception as e:
        return_msg = f"Your pipe with id : {pipe_id} could unfortunately not be updated... I failed with the following error : {e}"
    
    return jsonify({"Response": f"{return_msg}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)