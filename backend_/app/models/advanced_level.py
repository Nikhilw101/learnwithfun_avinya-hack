from app.db import db

class AdvancedLevel(db.Model):
    __tablename__ = 'advanced_level'

    id = db.Column(db.Integer, primary_key=True)
    sub_level = db.Column(db.Integer, nullable=False)
    concept = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.TIMESTAMP)

    def __repr__(self):
        return f"<AdvancedLevel(sub_level={self.sub_level}, concept={self.concept})>"

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()