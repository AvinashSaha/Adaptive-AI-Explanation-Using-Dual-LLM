import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    GEMINI1_API_KEY = os.getenv('GEMINI1_API_KEY')
    GEMINI2_API_KEY = os.getenv('GEMINI2_API_KEY')
    GEMINI1_MODEL = os.getenv('GEMINI1_MODEL', 'gemini-2.5-flash-lite')
    GEMINI2_MODEL = os.getenv('GEMINI2_MODEL', 'gemini-2.5-flash')

    
    # Fixed questions
    HEALTH_QUESTIONS = [
        "How can I improve the quality and consistency of my sleep?",
        "What small changes can I make to eat a more balanced and nutritious diet?",
        "How can I reduce my intake of processed foods and sugars without feeling restricted?",
        "What foods can I include more often to boost my energy and focus throughout the day?",
        "How do hydration needs differ between individuals following plant-based (vegan/vegetarian) diets and those on meat-based diets?",
        "What steps can I take to manage stress and support my mental well-being?",
        "How do diet type and nutrient interactions influence iron absorption and help maintain healthy iron levels?",
        "What can I do to improve my digestion and gut health through diet and lifestyle changes?",
        "How does exposure to natural light and outdoor environments influence energy, mood and overall well-being?",
        "What role do electrolytes (sodium, potassium, magnesium) play in maintaining hydration and muscle performance?"
    ]
    
    # Microsoft Forms URL (replace with your actual form)
    POST_TEST_FORM_URL = "https://forms.office.com/your-post-test-form-url"
