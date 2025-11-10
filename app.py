import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Webhook is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True, force=True)

    user_message = data.get("queryResult", {}).get("queryText", "").lower()

   
    # WEATHER HANDLER
    
    if "weather" in user_message or "temperature" in user_message:
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

    
    #  TIME HANDLER
   
    if "time" in user_message:
        from datetime import datetime
        import pytz

        try:
            ist = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(ist).strftime("%I:%M %p")
            reply = f"The current time in IST is {current_time}."
            return jsonify({"fulfillmentText": reply})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Time error: {str(e)}"})

   
    #  TASK HANDLING (if needed)
  
    if "add task" in user_message or "create task" in user_message:
        task = user_message.replace("add task", "").replace("create task", "").strip()
        reply = f"Task '{task}' has been added successfully."
        return jsonify({"fulfillmentText": reply})

    if "delete task" in user_message:
        task = user_message.replace("delete task", "").strip()
        reply = f"Task '{task}' has been deleted."
        return jsonify({"fulfillmentText": reply})

    if "complete task" in user_message or "mark task" in user_message:
        task = user_message.replace("complete task", "").replace("mark task", "").strip()
        reply = f"Task '{task}' marked as completed."
        return jsonify({"fulfillmentText": reply})

    
    #  FALLBACK (AUTO)
    
    return jsonify({"fulfillmentText": "I'm here to help!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
