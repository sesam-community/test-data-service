# Test data service 
A connector for automatically creating "embedded" test data.

## Support of property structures (nested elements)
The service supports 3 layers of nested dicts in dicts and nested lists with 1 layer of nested dicts

## Prerequisites
python3

## How to:

*Run program in development*

The below config considering yarn is optional.

This repo uses the file ```package.json``` and [yarn](https://yarnpkg.com/lang/en/) to run the required commands.

1. Set your required env vars.
```
    base_url, should look like https://<datahub-id>.sesam.cloud/api
    jwt
```
2. Make sure you have installed yarn.
3. Run:
    ```
        yarn install
    ```
4. Execute to run the script:
    ```
        yarn swagger
    ```

*Run program in production*

1. Make sure the required env variables are defined in the system config.

#### System config :

```
    {
    "_id": "test-data-service",
    "type": "system:microservice",
    "docker": {
        "environment": {
        "jwt": "$SECRET(sesam_jwt_token)",
        "base_url": "$ENV(base_sesam_api_url)"
        },
        "image": "sesamcommunity/test-data-service:version1.0",
        "port": 5000
    },
    "verify_ssl": false
    }
```

2. Connect to the system via the /proxy/ to see that it works :

    **The below method makes the url publically available, so use with caution and remove the "Anonymous" permission after use**
    
    Either choose :
    1. Go into the System permissions tab and under 'local Permissions' add the following :

        ![Permissions](Permissions.png)

    Or :
    1. Use your browser and modify headers so that you can set the Bearer token to accept a jwt token in request headers.
        - I.e. in Google Chrome, use "Modify Headers" app to set request headers like so :
            -   Authorization : Bearer <"Your bearer token">  

    2. Go to the following url example to see how to use the service:

        https://<"your_node_ID">.sesam.cloud/api/systems/test-data-service/proxy/

## Routes

```
    / <- this is index route for seeing what you need to do..
    /create?pipe_id=<the-pipe-you-want-to-update>&entities=<your-desired-number>
```