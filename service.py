from flask import Flask, request, jsonify, Response
import json
import requests
import os
import sys
from sesamutils import VariablesConfig, sesam_logger

app = Flask(__name__)
logger = sesam_logger("Steve the logger", app=app)

## Helpers
required_env_vars = ['jwt', 'base_url']

@app.route('/')
def index():
    output = {
        'service': 'Your personal test data service is up and running',
        'To do': 'Go to /create?pipe_id=<the-pipe-id-you-want-to-create-test-data-for> and let me do your work...',
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

    new_source = None
    return_msg = None
    header = {'Authorization': f'Bearer {config.jwt}', "content_type": "application/json"}
    try:
        sesam_config_request = requests.get(f"{config.base_url}/pipes/{pipe_id}/config", headers=header)
        json_config_response = json.loads(sesam_config_request.content.decode('utf-8-sig'))
        sesam_entity_request = requests.get(f"{config.base_url}/datasets/{pipe_id}/entities", headers=header)
        json_entity_response = json.loads(sesam_entity_request.content.decode('utf-8-sig'))
        embedded_data = []
        entities_to_remove = []
        for entity in json_entity_response[0]:
            if pipe_id not in entity and "_id" not in entity: 
                    entities_to_remove.append(entity)
                     
        try:
            for mapping_entity in entities_to_remove:
                for entity in json_entity_response[0:10]:
                    for sesam_property in list(entity):
                        if mapping_entity == sesam_property:
                            entity.pop(sesam_property) 
                        if pipe_id in sesam_property:
                            entity[sesam_property.split(":",1)[1]] = entity.pop(sesam_property)
                    
            for entity in list(json_entity_response[0:10]):
                _id = entity.get("_id").split(":",1)[1]
                entity['_id'] = _id     

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
        
        requests.put(f"{config.base_url}/pipes/{pipe_id}/config?force=True", headers=header, data=json.dumps(new_source))
        return_msg = f"Your pipe with id : {pipe_id} has been updated with test data"
    
    except Exception as e:
        return_msg = f"Your pipe with id : {pipe_id} could unfortunately not be updated... I failed with the following error : {e}"

    return jsonify({"Response": f"{return_msg}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)