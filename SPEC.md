# HTTP Server - Take-Home Test

## Background

**Ancelotti** is our in-house proxy software that routes customer traffic through our proxies. **Carlo** handles all business logic for that to happen, which includes authentication, geographic targeting, and proxy selection at high throughput. These two services communicate over HTTP/1.1 with JSON payloads. 

In this take-home test, you'll build a simplified version of Carlo's auth and routing pipeline. This will give you hands-on experience with the architectural patterns we use in production while keeping the scope manageable.

---

## Overview

Create an HTTP server with two endpoints:
1. **Auth Service** - Validate user credentials and parse routing parameters from the username
2. **Route Service** - Select a proxy based on the user selected parameters and a protocol

### The Context

The **Context** is the central data structure that flows through the request pipeline. It accumulates state as the request passes through each service stage.

In a real proxy server, a request flows through multiple stages: Auth → Route → Bind → Report. Each stage enriches the context with its results, passing it to the next stage. The context acts as a carrier for all request-related data.

For this test:
1. The client calls `/auth` with credentials
2. Auth validates the user and parses routing parameters from the username
3. Auth returns a **Context** containing the parsed parameters
4. The client calls `/route` with the context from auth
5. Route uses the parameters in the context to select a proxy

This pattern decouples authentication from routing logic while maintaining a clear data flow and gives great observability in production.

---

## API Specification


### POST /auth

Authenticate a user and parse routing parameters from the username.

**Request Body:**
```json
{
  "username": "alice_residential_c_us_city_new_york",
  "password": "secretpass123"
}
```

**Success Response (200):**
```json
{
  "context": {
    "auth_service": {
      "proxy_user_id": "alice_residential",
      "available_bandwidth": 10737418240,
      "residential_params": {
        "country": "us",
        "city": "new_york"
      }
    }
  },
  "available_bandwidth": 10737418240
}
```

**Error Response (401):**
```json
{
  "internal_error_code": 1001,
  "error_message": "invalid password"
}
```

[Country Targeting Syntax](https://documentation.pingproxies.com/general/generating-residential-proxies#country-targeting)<br>
[City Targeting Syntax](https://documentation.pingproxies.com/general/generating-residential-proxies#city-targeting)


---

### POST /route

Select a proxy based on the context from auth.

**Request Body:**
```json
{
  "context": {
    "auth_service": {
      "proxy_user_id": "alice_residential",
      "available_bandwidth": 10737418240,
      "residential_params": {
        "country": "us",
        "city": "new_york"
      }
    }
  },
  "protocol": "http"
}
```

**Success Response (200):**
```json
{
  "context": {
    "auth_service": {
      "proxy_user_id": "alice_residential",
      "available_bandwidth": 10737418240,
      "residential_params": {
        "country": "us",
        "city": "new_york"
      }
    },
    "route_service": {
      "proxy_addr": {
        "ip": "192.168.1.1",
        "port": 8080
      },
      "protocol": "http"
    }
  },
  "proxy_addr": {
    "ip": "192.168.1.1",
    "port": 8080
  }
}
```

**Routing Logic:**
1. If an exact country + city match exists, return it
2. If no city match, fallback to any proxy in that country
3. If no country match, return error
4. If no routing parameters specified, select a random proxy
5. All results need to support the chosen protocol

**Error Response (404):**
```json
{
  "internal_error_code": 3400,
  "error_message": "no proxy found for country"
}
```

---

## Database Setup

A PostgreSQL database is provided via Docker Compose. Start it with:

```bash
docker compose up -d
```

Connection details:
- Host: `localhost`
- Port: `5432`
- Database: `ping_residential`
- User: `ping_dev`
- Password: `localdev`

---

## Evaluation Criteria

### Areas of Focus

Ping focuses on fast and reliable proxying. We're evaluating whether you can take a set of business requirements and design a maintainable and extensible system.

- **Code structure** - Clean separation of concerns, easy to navigate and extend
- **Error handling** - We want to easily debug any issues that arise in production
- **Business requirements** - How you've interpreted and implemented the spec
- **Performance** - Consideration for efficiency and scale

### Trade-Offs

We're happy for you to cut corners to avoid scope creep. If you do, please leave comments in your code explaining what you would do differently with more time. 

You can do this using TODO comments such as the one below 

```
// TODO add db connection pooling. 
// Currently creates a DB connection per request
// I would use pgx pool library to implement this https://pkg.go.dev/github.com/jackc/pgx/v5/pgxpool

```
 
### Questions

If anything in the spec is ambiguous, please ask for clarification. We welcome questions and won't judge you for asking them. That said, we do expect you to make reasonable assumptions and figure out implementation details on your own.

**Good question:** "Should I support all types of residential params (ASN, state, zip code, etc.)?"

**Answer:** For this test, just support country and city params.

**Bad question:** "How do I connect to PostgreSQL in Go?"

---

## Timing

We don't expect you to spend more than **3 hours** on this task. A working solution that covers the core requirements is more valuable than a polished but incomplete one.

That said, we do expect you to come prepared with ideas about how you would improve or extend your implementation given more time. We'll discuss these in the follow-up conversation.

---

## Deliverables

Please submit your solution as a GitHub repository (public or private, your choice).

Include a README with:
- Instructions on how to run the server
- Any assumptions you made

---

