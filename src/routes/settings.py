from flask import Blueprint, request, jsonify
from src.models.database import db
from src.models.settings import Setting

settings_bp = Blueprint("settings_bp", __name__)

# Define default settings keys and descriptions
DEFAULT_SETTINGS = {
    "ai_provider": {"value": "none", "description": "AI provider for analysis (	'openai'	, 	'local'	, or 	'none'	)"},
    "openai_api_key": {"value": "", "description": "Your OpenAI API Key (leave blank if using local)"},
    "local_llm_endpoint": {"value": "http://localhost:1234/v1/chat/completions", "description": "API endpoint for your local LLM (LM Studio compatible)"},
    "local_llm_model_name": {"value": "", "description": "(Optional) Model name required by your local LLM API"}
    # Add other settings here if needed, e.g., default_currency
}

# Helper to get all settings, creating defaults if they don't exist
def get_all_settings():
    settings_dict = {}
    try:
        # Ensure default settings exist
        for key, data in DEFAULT_SETTINGS.items():
            setting = Setting.query.filter_by(key=key).first()
            if not setting:
                setting = Setting(key=key, value=data["value"], description=data["description"])
                db.session.add(setting)
        db.session.commit() # Commit any new default settings

        # Fetch all settings
        settings = Setting.query.all()
        settings_dict = {setting.key: setting.to_dict() for setting in settings}
        return settings_dict
    except Exception as e:
        db.session.rollback()
        print(f"Error getting settings: {e}")
        # Return defaults in case of DB error during fetch after defaults check
        return {key: {"key": key, **data} for key, data in DEFAULT_SETTINGS.items()}

# Get all settings
@settings_bp.route("", methods=["GET"])
def get_settings():
    settings = get_all_settings()
    return jsonify(settings), 200

# Update multiple settings
@settings_bp.route("", methods=["PUT"])
def update_settings():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        updated_settings = []
        for key, value in data.items():
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                # Special handling for sensitive keys like API keys?
                # For now, just update the value.
                setting.value = str(value) # Ensure value is stored as string
                updated_settings.append(setting.key)
            else:
                # Optionally allow creating new settings or return an error
                print(f"Warning: Attempted to update non-existent setting 	'{key}	'")
                # return jsonify({"error": f"Setting 	'{key}	' not found."}), 404
        
        if updated_settings:
            db.session.commit()
            return jsonify({"message": f"Settings updated: {', '.join(updated_settings)}"}), 200
        else:
             return jsonify({"message": "No valid settings found to update."}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Get a specific setting
@settings_bp.route("/<string:key>", methods=["GET"])
def get_setting(key):
    setting = Setting.query.filter_by(key=key).first()
    if setting:
        return jsonify(setting.to_dict()), 200
    else:
        # Check if it's a default setting that hasn't been created yet
        if key in DEFAULT_SETTINGS:
             # Create it now
             try:
                 default_data = DEFAULT_SETTINGS[key]
                 new_setting = Setting(key=key, value=default_data["value"], description=default_data["description"])
                 db.session.add(new_setting)
                 db.session.commit()
                 return jsonify(new_setting.to_dict()), 200
             except Exception as e:
                 db.session.rollback()
                 return jsonify({"error": f"Database error creating default setting: {str(e)}"}), 500
        else:
            return jsonify({"error": f"Setting 	'{key}	' not found"}), 404

# Update a specific setting (alternative to PUT on base route)
@settings_bp.route("/<string:key>", methods=["PUT"])
def update_setting(key):
    data = request.get_json()
    if not data or "value" not in data:
         return jsonify({"error": "Missing 'value' in request body"}), 400

    setting = Setting.query.filter_by(key=key).first()
    if not setting:
         return jsonify({"error": f"Setting 	'{key}	' not found."}), 404

    try:
        setting.value = str(data["value"])
        db.session.commit()
        return jsonify(setting.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

