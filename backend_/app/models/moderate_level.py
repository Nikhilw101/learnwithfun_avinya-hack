from app.db import db

class ModerateLevel(db.Model):
    __tablename__ = 'moderate_level'

    id = db.Column(db.Integer, primary_key=True)
    sub_level = db.Column(db.Integer, nullable=False)  # Level number (1, 2, 3, etc.)
    concept = db.Column(db.String(255), nullable=False)  # Concept name
    description = db.Column(db.Text, nullable=True)  # Concept description (optional)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Foreign key to User model
    is_completed = db.Column(db.Boolean, default=False)  # Track completion status
    completed_at = db.Column(db.TIMESTAMP)  # Timestamp for completion

    def __repr__(self):
        return f"<ModerateLevel(sub_level={self.sub_level}, concept={self.concept})>"

    def save_to_db(self):
        """
        Save the current object to the database.
        """
        db.session.add(self)
        db.session.commit()

    def mark_as_completed(self):
        """
        Mark the concept as completed and set the completion timestamp.
        """
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.save_to_db()

    @classmethod
    def find_by_concept(cls, concept):
        """
        Find a ModerateLevel entry by concept name.
        """
        return cls.query.filter_by(concept=concept).first()

    @classmethod
    def find_by_user_id(cls, user_id):
        """
        Find all ModerateLevel entries for a specific user.
        """
        return cls.query.filter_by(user_id=user_id).all()