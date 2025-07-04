from app.extensions import db

class WebhookEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(100))
    author = db.Column(db.String(100))
    action = db.Column(db.String(50))
    from_branch = db.Column(db.String(100))
    to_branch = db.Column(db.String(100))
    timestamp = db.Column(db.String(100))
    
    def serialize(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "author": self.author,
            "action": self.action,
            "from_branch": self.from_branch,
            "to_branch": self.to_branch,
            "timestamp": self.timestamp}