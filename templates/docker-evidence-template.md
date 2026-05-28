# Docker Evidence – Lab 04

## Team

* Team name: Nhóm A3 - Phạm Đình Tuấn Anh, Lê Tiến Được, Nguyễn Văn Thống
* Service: Access Gate
* Image tag: `fit4110/access-gate:lab04`
* Version tag: `fit4110/access-gate:v0.1.0-team-gate`

## 1. Build evidence

Command:

```bash
docker build -t fit4110/access-gate:lab04 .
```

Result:

Docker image was built successfully for the Access Gate service.

Evidence:

```text
reports/screenshots/01-docker-build.png
```

## 2. Image tag evidence

Command:

```bash
docker tag fit4110/access-gate:lab04 fit4110/access-gate:v0.1.0-team-gate
docker images
```

Result:

The Docker image has the required Lab 04 tag convention:

```text
fit4110/access-gate:lab04
fit4110/access-gate:v0.1.0-team-gate
```

Evidence:

```text
reports/screenshots/02-docker-images-tag.png
```

## 3. Run evidence

Command:

```bash
docker run -d --name fit4110-access-gate-lab04 -p 8000:8000 --env-file .env.example fit4110/access-gate:lab04
```

Result:

The Access Gate container started successfully and exposed port `8000`.

Evidence:

```text
reports/screenshots/03-docker-run-container.png
```

## 4. Healthcheck evidence

Command:

```bash
curl -i http://localhost:8000/health
```

Result:

```json
{
  "status": "ok",
  "service": "access-gate"
}
```

The container returned `HTTP/1.1 200 OK` for `GET /health`.

Evidence:

```text
reports/screenshots/04-health-check.png
```

## 5. ProblemDetails evidence

Command:

```bash
curl -i "http://localhost:8000/access/logs/recent?limit=999" -H "Authorization: Bearer lab-token" -H "X-Correlation-Id: 22222222-2222-2222-2222-222222222222"
```

Result:

The service returned a validation error using the ProblemDetails-style response body, including fields such as:

```json
{
  "type": "https://campus.local/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "errors": []
}
```

Evidence:

```text
reports/screenshots/05-problemdetails-error.png
```

## 6. Newman evidence

Command:

```bash
npm run test:local
```

Report path:

```text
reports/newman-lab04-local.html
reports/newman-lab04-local.xml
```

Result:

The Postman Collection from Lab 03 was executed against the Access Gate service running inside the Docker container.

Evidence:

```text
reports/screenshots/08-newman-local-pass.png
```

## 7. Notes

* Known limitation: Lab 04 uses in-memory data for Access Gate instead of a real database. Database integration is prepared through environment variables in `.env.example`.
* Next step for Lab 05: Add Docker Compose and connect Access Gate to a real database/service network if required.
