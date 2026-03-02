# Aidan McKellar - Takehome Test

## Setup

I have modified the docker-compose.yml file so it starts both the postgres and app container.

```bash
docker compose up --build
```

## Code Structure

I used FastAPI and used FastAPI routers to seperate the endpoints into their own files.

## Error handling & debugging

Every error in each endpoint returns a unique error code. Running the app using fastapi dev mode allows me to see each endpoint hit and the code returned.
I also used some postman requests to automatically send both valid and invalid inputs to the endpoints.

## Improvements to be made.

1. Convert from docker-compose to kubernetes to improve scalability.
2. Remove the database bottleneck by adding a cache. Implementation here could vary.
3. Add a load balancer and multiple instances of the app so more users can be served.
4. Move the models from the endpoints into their own seperate files as they are unlikely to change often.
5. Add examples to the models so the generated docs are more useful: https://fastapi.tiangolo.com/tutorial/schema-extra-example/
6. Potentially change the database pooling parameters: https://deepwiki.com/fastapi/sqlmodel/2.5-engine-and-database-connection#sqlmodel-vs-sqlalchemy-engine

