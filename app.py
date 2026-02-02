from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from config import Config
from llm_service import LLMService
import uuid

app = Flask(__name__)
app.config.from_object(Config)
llm_service = LLMService()

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/portal")
def index():
    return render_template("index.html", questions=Config.HEALTH_QUESTIONS)

@app.route("/process", methods=["POST"])
def process():
    question = request.form.get("question")
    if question not in Config.HEALTH_QUESTIONS:
        return jsonify({"error": "Invalid question. Please select from the provided options."}), 400
    session_id = str(uuid.uuid4())
    try:
        llm1_response = llm_service.get_llm1_response(question)
        llm2_data = llm_service.get_llm2_response(question, llm1_response)
        session["current_query"] = {
            "session_id": session_id,
            "question": question,
            "llm1_response": llm1_response,
            "llm2_response": llm2_data,
        }
        return redirect(url_for("results"))
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route("/results")
def results():
    if "current_query" not in session:
        return redirect(url_for("index"))
    query_data = session["current_query"]
    return render_template(
        "results.html",
        query_data=query_data,
        llm1_model=Config.GEMINI1_MODEL,
        llm2_model=Config.GEMINI2_MODEL,
        post_form_url=Config.POST_TEST_FORM_URL,
    )

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
