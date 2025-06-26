# Introduction

This example is a fork from [REDIS MCP](https://github.com/redis/mcp-redis) server and showcase how we can host a redis mcp server on OCI Data Science Model deployment.
Following additions are done to accommodate it on OCI - 

- Dockerize the application to host this as Bring Your Own Container(BYOC)
- Add a custom route for health endpoint
- Use streamable-http as the default mcp transport protocol

# OCI Cache integration
Create an OCI Cache cluster using [documentation](https://docs.oracle.com/en-us/iaas/Content/ocicache/createcluster.htm) and fetch the Redis cluster endpoint.
We will use this endpoint to configure MCP redis server using TLS enabled config.

Configure this endpoint as `REDIS_HOST` configuration in .env file or pass environment variables for dynamic binding.

# Example
Sample script on how to create a model deployment is present [here](./model-deplyment.py) and perform inferencing is shared in [here](./inference.py).

# Help
You can raise issues in this repository for any assistance.