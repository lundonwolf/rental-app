from flask import Blueprint, request, jsonify, current_app
from src.models.database import db
from src.models.utility import UtilityBill, UtilityCategory
from src.routes.settings import get_all_settings # Helper to get current settings
from openai import OpenAI, OpenAIError
import datetime
import json

ai_bp = Blueprint("ai_bp", __name__)

# Helper function to get AI client based on settings
def get_ai_client(settings):
    provider = settings.get("ai_provider", {}).get("value", "none")
    api_key = settings.get("openai_api_key", {}).get("value")
    base_url = settings.get("local_llm_endpoint", {}).get("value")

    if provider == "openai" and api_key:
        try:
            return OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            return None
    elif provider == "local" and base_url:
        try:
            # For LM Studio or similar local endpoints compatible with OpenAI client
            return OpenAI(base_url=base_url, api_key="not-needed")
        except Exception as e:
            print(f"Error initializing Local LLM client: {e}")
            return None
    else:
        return None

# Helper function to prepare utility data for the prompt
def prepare_utility_data_summary(months=6):
    summary = "Recent Utility Bills:\n"
    try:
        cutoff_date = datetime.date.today() - datetime.timedelta(days=months * 30)
        bills = UtilityBill.query.filter(UtilityBill.billing_period_end >= cutoff_date)\
                               .order_by(UtilityBill.billing_period_end.desc()).all()
        
        if not bills:
            return "No recent utility bill data found."

        for bill in bills:
            category_name = bill.category.name if bill.category else "Unknown Category"
            summary += f"- {category_name}: {bill.billing_period_start} to {bill.billing_period_end}, Amount: ${bill.total_amount:.2f}"
            if bill.usage_data:
                summary += f", Usage: {bill.usage_data}"
            summary += "\n"
        
        return summary
    except Exception as e:
        print(f"Error preparing utility data: {e}")
        return "Error retrieving utility data."

# Endpoint to get AI analysis
@ai_bp.route("/analyze_utilities", methods=["GET"])
def analyze_utilities():
    settings = get_all_settings()
    client = get_ai_client(settings)

    if not client:
        provider = settings.get("ai_provider", {}).get("value", "none")
        if provider == "none":
             return jsonify({"error": "AI analysis is disabled. Please configure an AI provider in Settings."}), 400
        else:
             return jsonify({"error": "AI provider is configured but could not be initialized. Check API key/endpoint in Settings."}), 500

    # Prepare data and prompt
    utility_data_summary = prepare_utility_data_summary(months=12) # Analyze last 12 months
    if "Error" in utility_data_summary or "No recent" in utility_data_summary:
         return jsonify({"analysis": utility_data_summary}), 200 # Return data status if no analysis possible

    system_prompt = (
        "You are a helpful assistant analyzing home utility bill data. "
        "Provide insights into usage patterns, predict potential future trends (next month estimate if possible), "
        "and suggest practical cost-saving recommendations based ONLY on the provided data. "
        "Be concise and format your response clearly, perhaps using sections for Patterns, Predictions, and Recommendations."
    )
    user_prompt = f"Here is the recent utility bill data:\n{utility_data_summary}\nPlease analyze this data."

    try:
        response = client.chat.completions.create(
            model=settings.get("local_llm_model_name", {}).get("value") or "gpt-3.5-turbo", # Default to gpt-3.5 if local model name not set
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.5,
        )
        
        analysis_content = response.choices[0].message.content.strip()
        return jsonify({"analysis": analysis_content}), 200

    except OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        # Check for specific error types if needed (e.g., authentication, rate limits)
        error_message = f"Error communicating with AI provider: {e.type} - {e.code} - {e.body}"
        # Try to provide a more user-friendly message for common errors
        if "authentication" in str(e).lower():
             error_message = "AI Authentication Error. Please check your API Key in Settings."
        elif "rate_limit" in str(e).lower():
             error_message = "AI Rate Limit Exceeded. Please try again later or check your plan."
        elif "connection error" in str(e).lower():
             error_message = "Could not connect to the AI provider endpoint. Please check the URL in Settings and ensure the service is running."
        
        return jsonify({"error": error_message}), 500
    except Exception as e:
        print(f"Generic AI analysis error: {e}")
        return jsonify({"error": f"An unexpected error occurred during AI analysis: {str(e)}"}), 500

