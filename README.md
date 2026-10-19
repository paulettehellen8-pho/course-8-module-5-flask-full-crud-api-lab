# Events API

A small RESTful API built with Flask for managing a list of events.
It supports creating, updating and deleting events using JSON.

Data is stored in an in-memory Python list, so it resets every time
the server restarts. A real database is the next step.

## Setup

```bash
pipenv install
pipenv shell
python app.py
```

The server runs at `http://localhost:5000`.

## Running the tests

```bash
pytest
```

## Routes

| Method | Route          | Purpose                    | Success status |
|--------|----------------|----------------------------|----------------|
| POST   | `/events`      | Create a new event         | 201 Created    |
| PATCH  | `/events/<id>` | Update an event's title    | 200 OK         |
| DELETE | `/events/<id>` | Remove an event            | 204 No Content |

## Validation rules for `title`

- The request body must be a JSON object.
- `title` is required and must be a string.
- `title` cannot be empty or only spaces (surrounding spaces are trimmed).
- `title` cannot exceed 100 characters.

## Example requests and responses

### Create an event

```bash
curl -i -X POST http://localhost:5000/events \
  -H "Content-Type: application/json" \
  -d '{"title": "Hackathon"}'
```

Response: `201 Created`

```json
{ "id": 3, "title": "Hackathon" }
```

### Update an event

```bash
curl -i -X PATCH http://localhost:5000/events/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Hackathon 2025"}'
```

Response: `200 OK`

```json
{ "id": 1, "title": "Hackathon 2025" }
```

### Delete an event

```bash
curl -i -X DELETE http://localhost:5000/events/2
```

Response: `204 No Content` (empty body)

## Error responses

Every error returns JSON in the same shape: `{ "error": "message" }`.

| Situation                          | Status | Response body                                           |
|------------------------------------|--------|---------------------------------------------------------|
| Missing or invalid JSON body       | 400    | `{"error": "Request body must be a JSON object (send valid JSON with Content-Type: application/json)"}` |
| `title` missing                    | 400    | `{"error": "'title' is required"}`                      |
| `title` not a string               | 400    | `{"error": "'title' must be a string"}`                 |
| `title` empty or only spaces       | 400    | `{"error": "'title' cannot be empty"}`                  |
| `title` longer than 100 characters | 400    | `{"error": "'title' cannot exceed 100 characters"}`     |
| Event id does not exist            | 404    | `{"error": "Event 99 not found"}`                       |

## Design notes

- Repeated logic (finding an event, validating the title, building errors)
  lives in helper functions, so each rule exists in one place.
- New ids use the highest existing id + 1, so an id is never reused
  after a deletion.
- PATCH checks that the event exists before validating the body,
  so a missing event always returns 404.

## Known limitations

- Data is not saved between server restarts.
- Requests to unknown routes (e.g. `/events/abc`) or with an unsupported
  method (e.g. `GET /events`) return Flask's default HTML error page,
  not JSON.