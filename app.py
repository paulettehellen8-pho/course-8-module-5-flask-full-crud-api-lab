# Flask: the web framework that creates our app
# jsonify: converts Python dicts into proper JSON HTTP responses
# request: gives us access to the data the client sent us
from flask import Flask, jsonify, request

app = Flask(__name__)

# A named constant instead of a "magic number" buried in the code.
# If the rule changes, we change it in ONE place.
MAX_TITLE_LENGTH = 100


# Simulated data
class Event:
    def __init__(self, id, title):
        self.id = id
        self.title = title

    # Converts the object into a dictionary so jsonify() can handle it
    def to_dict(self):
        return {"id": self.id, "title": self.title}


# In-memory "database": resets whenever the server restarts
events = [
    Event(1, "Tech Meetup"),
    Event(2, "Python Workshop")
]


# ---------- HELPERS ----------

def error_response(message, status):
    """Build a consistent JSON error: {"error": "..."} plus a status code."""
    return jsonify({"error": message}), status


def find_event(event_id):
    """Return the Event with this id, or None if it doesn't exist."""
    # Go through every event in the list, one at a time
    for event in events:
        # Compare this event's id to the id we're looking for
        if event.id == event_id:
            return event  # found it: stop looping and hand it back

    # Nothing matched. Return None explicitly so the caller can decide
    # what to do (PATCH and DELETE both send a 404).
    return None


def get_valid_title():
    """
    Read and validate 'title' from the JSON body.
    Returns a tuple: (title, None) on success, or (None, error) on failure.
    """
    # silent=True makes get_json() return None when the body is missing or
    # isn't valid JSON, instead of raising an HTML error page.
    data = request.get_json(silent=True)

    # The body must be a JSON object (a dict in Python). [], "hello", 5
    # and None (no usable body) are all rejected here.
    if not isinstance(data, dict):
        return None, error_response(
            "Request body must be a JSON object", 400)

    # The "title" key must exist
    if "title" not in data:
        return None, error_response("'title' is required", 400)

    # Safe to read now, because we know the key exists
    title = data["title"]

    # The title must be text. This rejects numbers, lists, null (None), etc.
    if not isinstance(title, str):
        return None, error_response("'title' must be a string", 400)

    # Remove spaces from both ends, so "   " becomes "" and is rejected below
    title = title.strip()

    # An empty string is falsy in Python, so `not title` means "it's empty"
    if not title:
        return None, error_response("'title' cannot be empty", 400)

    # Reject titles that are too long
    if len(title) > MAX_TITLE_LENGTH:
        return None, error_response(
            f"'title' cannot exceed {MAX_TITLE_LENGTH} characters", 400)

    # All checks passed: return the clean title and None for "no error"
    return title, None


def next_event_id():
    """Return highest existing id + 1. An empty list gives 1."""
    # (event.id for event in events) produces every existing id.
    # max() picks the largest one.
    # default=0 is used when `events` is empty. Without it, max() on an
    # empty sequence would crash with a ValueError.
    # We use max + 1 instead of len(events) + 1 because after a delete,
    # len() + 1 can repeat an id that is already in use.
    return max((event.id for event in events), default=0) + 1


# ---------- ROUTES ----------

# NEW - Welcome route
# Rubric: "serves a JSON welcome message at the / route"
# Routes accept only GET by default, so no methods argument is needed.
@app.route("/")
def welcome():
    # A dict with a "message" key, sent as JSON. Status 200 is the default.
    return jsonify({"message": "Welcome to the Events API"}), 200


# NEW - Read all events
# Rubric: "handles a GET request to /events and returns a JSON array"
# This shares the path /events with POST. Flask tells them apart by method.
@app.route("/events", methods=["GET"])
def get_events():
    # List comprehension: build a new list by converting each Event object
    # to a dict. jsonify() can't serialize Event objects directly.
    # Edge case: if `events` is empty this returns [] (a valid empty array),
    # not an error, because "no events yet" is a normal state.
    return jsonify([event.to_dict() for event in events]), 200


# TODO: Task 1 - Define the Problem
# Create a new event from JSON input
@app.route("/events", methods=["POST"])
def create_event():
    # TODO: Task 2 - Design and Develop the Code
    # Validate the input with the shared helper. It returns two values.
    title, error = get_valid_title()

    # If validation failed, `error` holds the (response, status) to send.
    # Returning here stops the function, so nothing gets created.
    if error:
        return error

    # TODO: Task 3 - Implement the Loop and Process Each Element
    # Build the event with a safe, unique id, then add it to the list.
    # append() changes the ORIGINAL list in place (never write `events = ...`).
    event = Event(next_event_id(), title)
    events.append(event)

    # TODO: Task 4 - Return and Handle Results
    # jsonify() closes BEFORE the comma, so 201 is the HTTP status code
    # and not part of the JSON body.
    return jsonify(event.to_dict()), 201


# TODO: Task 1 - Define the Problem
# Update the title of an existing event
@app.route("/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    # TODO: Task 2 - Design and Develop the Code
    # Look up the event FIRST: a missing event is a 404 even if the
    # body is also bad.
    event = find_event(event_id)

    # `is None` is the correct way to check for None
    if event is None:
        return error_response(f"Event {event_id} not found", 404)

    # The event exists, so now validate the new title
    title, error = get_valid_title()
    if error:
        return error

    # TODO: Task 3 - Implement the Loop and Process Each Element
    # (The loop lives inside find_event.) Update the title on the object.
    event.title = title

    # TODO: Task 4 - Return and Handle Results
    # 200 = OK
    return jsonify(event.to_dict()), 200


# TODO: Task 1 - Define the Problem
# Remove an event from the list
@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    # TODO: Task 2 - Design and Develop the Code
    # Same lookup as PATCH, reusing the helper (DRY)
    event = find_event(event_id)
    if event is None:
        return error_response(f"Event {event_id} not found", 404)

    # TODO: Task 3 - Implement the Loop and Process Each Element
    # remove() deletes that exact object from the original list in place.
    # The tests clear and refill this same list, so we must not reassign it.
    events.remove(event)

    # TODO: Task 4 - Return and Handle Results
    # 204 = No Content: success with an empty body, so no jsonify here
    return "", 204


# Runs only when started directly with `python app.py`, not when pytest
# imports the file. debug=True is for development only.
if __name__ == "__main__":
    app.run(debug=True)