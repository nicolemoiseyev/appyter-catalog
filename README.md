# appyter-catalog: A catalog of [appyters](https://github.com/maayanLab/appyter/)

Pull requests encouraged, please refer to the [example](./appyters/example/) for registering your own appyter.

## Deployment

Currently, because this application deals with several independent appyters, we construct Dockerfiles independently for each and facilitate deployment with docker-compose.yml. In the future this can be extended to automatically generating a kubernetes deployment or simply using docker-in-docker, but for now a simple Makefile will do the trick of hosting the docker-compose on a single system.

```bash
# Download the catalog locally
git clone git@github.com:MaayanLab/appyter-catalog.git

# Start the server (this has several dependent steps including constructing dockerfiles, docker-compose and building it all)
make start

# Update the server with latest github (WARNING: this will force delete anything not tracked in your current directory, then restart the application)
make update
```
