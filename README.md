# Test data service 
A connector for automatically creating "embedded" test data.

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
    "_id": "test-data-servive",
    "type": "system:microservice",
    "docker": {
        "environment": {
        "base_url": "$SECRET(sesam_jwt_token)",
        "jwt": "$ENV(base_sesam_api_url)"
        },
        "image": "sesamcommunity/test-data-service:version1.0",
        "port": 5000
    },
    "proxy": {
        "header_blacklist": ["CUSTOM_AUTHORIZATION"],
        "sesam_authorization_header": "CUSTOM_AUTHORIZATION"
      },
    "verify_ssl": true
    }
```

2. Connect to the system via the /proxy/ to see that it works :

    1. Go into the System permissions tab and under 'local Permissions' add the following :

        ![Permissions](Permissions.png)

    2. Go to the following url example to see how to use the service:

        https://<"your_node_ID">.sesam.cloud/api/systems/test-data-service/proxy/

## Routes

```
    / <- this is index route for seeing what you need to do..
    /create?pipe_id=<the-pipe-you-want-to-update>
```