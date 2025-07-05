from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import db
from app.models import WebhookEvent

webhook = Blueprint("webhook", __name__, url_prefix='/webhook')

# # # For testing of POST request
# @webhook.route('/receiver', methods=["GET","POST"])
# def receiver():
#     # event_type = request.headers.get('X-GitHub-Event')
#     payload = request.get_json(force=True)
#     print("REceived JSON: ",payload)
#     return {"status":"success"}, 200


@webhook.route('/receiver', methods=["GET","POST"])
def receiver():
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.get_json(force=True)

    if not event_type or not payload:
        return jsonify({"error": "Missing data"}), 400

    timestamp = datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")

    event = WebhookEvent(
        request_id=None,
        author=None,
        action=event_type.upper(),
        from_branch=None,
        to_branch=None,
        timestamp=timestamp
    )

    if event_type == "push":
        event.author = payload["pusher"]["name"]
        event.to_branch = payload["ref"].split("/")[-1]
        event.request_id = payload["after"]

    elif event_type == "pull_request":
        pr = payload["pull_request"]
        event.author = pr["user"]["login"]
        event.from_branch = pr["head"]["ref"]
        event.to_branch = pr["base"]["ref"]
        event.request_id = str(pr["id"])

        if payload["action"] == "closed" and pr.get("merged"):
            event.action = "MERGE"

    else:
        return jsonify({"error": "Unsupported event"}), 400

    db.session.add(event)
    db.session.commit()

    return jsonify({"status": "success"}), 200

@webhook.route('/events', methods=["GET"])
def events():
    all_events = WebhookEvent.query.order_by(WebhookEvent.id.desc()).all()
    result = []
    for ev in all_events:
        result.append({
            "id": ev.id,
            "request_id": ev.request_id,
            "author": ev.author,
            "action": ev.action,
            "from_branch": ev.from_branch,
            "to_branch": ev.to_branch,
            "timestamp": ev.timestamp
        })
    return jsonify(result)

@webhook.route('/viewer', methods=["GET"])
def viewer():
    return """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Webhook Events Viewer</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 20px;
          background-color: #f8f8f8;
        }
        h2 {
          color: #333;
        }
        .event {
          background: white;
          border-radius: 5px;
          padding: 10px;
          margin: 5px 0;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
      </style>
    </head>
    <body>
      <h2>Recent GitHub Events</h2>
      <div id="events"></div>

      <script>
        async function fetchEvents() {
          const res = await fetch('/webhook/events');
          const data = await res.json();
          const container = document.getElementById('events');
          container.innerHTML = '';

          data.forEach(ev => {
            let msg = '';
            if (ev.action === "PUSH") {
              msg = ${ev.author} pushed to ${ev.to_branch} on ${ev.timestamp};
            } else if (ev.action === "PULL_REQUEST") {
              msg = ${ev.author} submitted a pull request from ${ev.from_branch} to ${ev.to_branch} on ${ev.timestamp};
            } else if (ev.action === "MERGE") {
              msg = ${ev.author} merged branch ${ev.from_branch} to ${ev.to_branch} on ${ev.timestamp};
            }
            const div = document.createElement('div');
            div.className = 'event';
            div.textContent = msg;
            container.appendChild(div);
          });
        }

        fetchEvents();
        setInterval(fetchEvents, 15000);
      </script>
    </body>
    </html>
    """