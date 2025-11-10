import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

TASKS = []   # simple in-memory task list

@app.route("/", methods=["GET"])
def home():
    return "Webhook is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True, force=True)

    # Get intent name
    intent = data.get("queryResult", {}).get("intent", {}).get("displayName", "")
    params = data.get("queryResult", {}).get("parameters", {})
    user_message = data.get("queryResult", {}).get("queryText", "").lower()

    
    if intent == "Weather":
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=28.625&longitude=77.25&current_weather=true"
            weather_json = requests.get(url).json()

            current = weather_json.get("current_weather", {})
            temp = current.get("temperature")
            wind = current.get("windspeed")

            reply = f"The current temperature is {temp}°C with wind speed {wind} km/h."
            return jsonify({"fulfillmentText": reply})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Weather API error: {str(e)}"})

    
    if intent == "Time_Check":
        try:
            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%I:%M %p")
            return jsonify({"fulfillmentText": f"The current time in IST is {current_time}."})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Time error: {str(e)}"})

   
    if intent == "task_creation":
        task_text = params.get("task", "")
        date_time = params.get("date-time", "")

        TASKS.append({"task": task_text, "date": date_time})
        return jsonify({"fulfillmentText": f"Task added: {task_text} (Due: {date_time})"})

   
    if intent == "task_list":
        if not TASKS:
            return jsonify({"fulfillmentText": "You have no tasks."})

        reply = "Here are your tasks:\n"
        for i, t in enumerate(TASKS, 1):
            reply += f"{i}. {t['task']} — Due: {t['date']}\n"

        return jsonify({"fulfillmentText": reply})

    
    if intent == "task_delete":
        number = int(params.get("number", 0))

        if number < 1 or number > len(TASKS):
            return jsonify({"fulfillmentText": "Invalid task number."})

        removed = TASKS.pop(number - 1)
        return jsonify({"fulfillmentText": f"Task deleted: {removed['task']}"})

   
    return jsonify({"fulfillmentText": "I'm here to help!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

