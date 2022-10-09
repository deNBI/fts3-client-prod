A client that eases the handling of FTS3 transfers to an S3 bucket.

# Set up
This README is about setting up the FTS3-Client.  
For more information on how to set up the whole software stack, please visit the Wiki.

## Requirements
### Docker
The FTS3-Client is best used with Docker and Docker-compose. For installation information, please
see [here](https://docs.docker.com/get-docker/).
### Keys
Make sure you have certificates for the FTS3 cluster. More info can be found in the Wiki.
### Credentials
Make sure you have credentials for the S3 bucket. More info can be found in the Wiki.

## Settings
1. Place a `fts3.cert.pem`, `fts3.key.pem` and `CA.pem` in the `keys` folder.
2. Copy the `.env.in` to `.env` and fill out the fields.
* DEBUG: Can be True or False. For more debug output.
* S3_URL: The S3 endpoint without protocol.
* S3_BUCKET: The name of the S3 bucket.
* FTS3_URL: The endpoint of the FTS3 cluster with protocol.
* LOG_LEVEL: DEBUG/INFO/WARN etc. sets the general log level of all loggers.
3. Copy all files from `.secrets.in` to `.secrets` and fill them with the according information.
* API_KEY: Authorization key to access clients endpoints.
* S3_ACCESS_KEY: Access key of the S3 bucket.
* S3_SECRET_KEY: Secret key of the S3 bucket.

# Running the client
A `Makefile` eases the start of the FTS3-Client. Run `make help` for mor information about the commands.
# Production
To start the FTS3-Client run `make` which starts the `docker-compose.yml` file.
## Develop
Run `make dev-build` to build a local image.  
Run `make dev` to run the dev image or to build it in case it does not exist.
The endpoints are exposed at localhost:8080.

# Usage
An overview of the endpoints can be found at example.de:8080/docs. When running in dev mode,
you may find them at localhost:8080.

Example curl:  
`curl -H "X-AUTH-HEADER: <YOUR-API-KEY>" -H "Content-Type: application/json" -X POST -d @/path/to/your/database.json localhost:8080/transfer/dry`
