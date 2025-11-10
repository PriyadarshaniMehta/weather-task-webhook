import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

TASKS = []   # simple in-memory task list

# Load News API Key
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

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

    # WEATHER INTENT
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


    # TIME CHECK INTENT
    if intent == "Time_Check":
        try:
            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%I:%M %p")
            return jsonify({"fulfillmentText": f"The current time in IST is {current_time}."})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Time error: {str(e)}"})


    #  NEWS INTENT
    if intent == "News_Update":

        # Optional category detection from user message
        category = None
        if "tech" in user_message:
            category = "technology"
        elif "sport" in user_message:
            category = "sports"
        elif "world" in user_message:
            category = "world"
        elif "india" in user_message:
            category = "india"
        elif "finance" in user_message:
            category = "business"

        try:
            url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}"

            if category:
                url += f"&category={category}"

            news_json = requests.get(url).json()
            articles = news_json.get("results", [])

            if not articles:
                return jsonify({"fulfillmentText": "I couldn't find any news at the moment."})

            # Take first 3 headlines
            top3 = [a.get("title") for a in articles[:3]]
            reply = "Here are the latest headlines:\n\n" + "\n".join([f"- {h}" for h in top3])

            return jsonify({"fulfillmentText": reply})

        except Exception as e:
            return jsonify({"fulfillmentText": f"News error: {str(e)}"})


    # TASK COMPLETION
    if intent == "task_complete":
        number = int(params.get("number", 0))

        if number < 1 or number > len(TASKS):
            return jsonify({"fulfillmentText": "Invalid task number."})

        TASKS[number - 1]["completed"] = True
        task_text = TASKS[number - 1]["task"]
        return jsonify({"fulfillmentText": f"Task marked as completed: {task_text}"})


    # TASK CREATION
    if intent == "task_creation":
        task_text = params.get("task", "")
        date_time = params.get("date-time", "")

        TASKS.append({"task": task_text, "date": date_time})
        return jsonify({"fulfillmentText": f"Task added: {task_text} (Due: {date_time})"})


    # TASK LIST
    if intent == "task_list":
        if not TASKS:
            return jsonify({"fulfillmentText": "You have no tasks."})

        reply = "Here are your tasks:\n"
        for i, t in enumerate(TASKS, 1):
            reply += f"{i}. {t['task']} — Due: {t['date']}\n"

        return jsonify({"fulfillmentText": reply})


    # TASK DELETE
    if intent == "task_delete":
        number = int(params.get("number", 0))

        if number < 1 or number > len(TASKS):
            return jsonify({"fulfillmentText": "Invalid task number."})

        removed = TASKS.pop(number - 1)
        return jsonify({"fulfillmentText": f"Task deleted: {removed['task']}"})


    # FALLBACK
    return jsonify({"fulfillmentText": "I'm here to help!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


