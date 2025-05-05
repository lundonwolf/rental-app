from src.models.database import db

# Model for storing application settings (key-value pairs)
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True) # Optional description of the setting

    def __repr__(self):
        return f"<Setting {self.key}>"

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "description": self.description
        }

# Example settings keys:
# - ai_provider: "openai" or "local"
# - openai_api_key: "sk-..."
# - local_llm_endpoint: "http://localhost:1234/v1/chat/completions"
# - local_llm_model_name: "Optional model name for local LLM"

