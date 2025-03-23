from flask import Flask, request, jsonify, send_from_directory
from google import genai
from flask_cors import CORS
from google.genai import types


app = Flask(__name__)
CORS(app)

API_KEY = 'AIzaSyDEq-iFbyogj_iBVe-cUMwCFLTc_Wj1NxQ'

# Define available genres
GENRES = ['Story', 'Poetry', 'Sci-Fi', 'Fantasy', 'Mystery', 'Romance', 'Dialogue', 'Speech']

def get_prompt_template(theme, genre):
    prompts = {
        "Poetry": f"""Write a creative poem about {theme}.
            Guidelines:
            - Express deep emotions and feelings
            - Use vivid imagery and symbolism
            - Create powerful metaphors
            - 4-8 lines in length""",
        
        "Story": f"""Create an engaging story about {theme}.
            Guidelines:
            - Develop complex plot
            - Build deep characters
            - Include rich details
            - Natural dialogue and flow""",
        
        "Romance": f"""Write a romantic story about {theme}.
            Guidelines:
            - Focus on deep emotions
            - Create memorable characters
            - Build natural chemistry
            - Include meaningful moments""",
        
        "Mystery": f"""Create an intriguing mystery about {theme}.
            Guidelines:
            - Build intense suspense
            - Include clever twists
            - Develop complex characters
            - Create satisfying resolution""",
            
        "Dialogue": f"""Write a one-on-one conversation between two people about {theme}.
            Guidelines:
            - Create natural, flowing dialogue between exactly two characters
            - Show personality through their speaking styles
            - Include their reactions and emotions
            - Add meaningful dialogue tags
            - Balance speech with brief action/context
            - Keep it as a focused conversation between just these two people""",
            
        "Speech": f"""Write a compelling speech about {theme}.
            Guidelines:
            - Use persuasive language
            - Include rhetorical devices
            - Create powerful opening/closing
            - Incorporate audience engagement""",
            
        "default": f"""Create a {genre} piece about {theme}.
            Guidelines:
            - Use powerful expression
            - Develop engaging content
            - Include vivid details
            - Make it unforgettable"""
    }
    return prompts.get(genre, prompts["default"])

def generate_creative_text(theme, genre):
    try:
        client = genai.Client(
            api_key=API_KEY,
            http_options={'api_version': 'v1alpha'}
        )
        
        prompt = get_prompt_template(theme, genre)
        
        # Updated parameters to match current Gemini API
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048
            )
        )
        
        if hasattr(response, 'text'):
            return response.text.strip()
        
        return f"Here's a simple {genre.lower()} about {theme}:\n\n" + \
               f"In a world where anything is possible, {theme} becomes the center of attention."
               
    except Exception as e:
        print(f"Generation error: {str(e)}")
        return f"A {genre.lower()} about {theme} will be coming soon."

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        theme = data.get('theme', '').strip()
        genre = data.get('genre', 'Story')
        
        if not theme:
            return jsonify({'error': 'Theme is required'}), 400
            
        generated_text = generate_creative_text(theme, genre)
        
        if "error" in generated_text.lower() or "could not generate" in generated_text.lower():
            return jsonify({'error': generated_text}), 500
            
        return jsonify({'generatedText': generated_text})
        
    except Exception as e:
        print(f"Server error: {str(e)}")
        return jsonify({'error': 'An error occurred. Please try again.'}), 500

def run_cli_mode():
    """Run in CLI mode when executed directly"""
    print("\nCreative Text Generator CLI Mode")
    theme = input("Enter your theme: ")
    print("\nAvailable genres:")
    for i, genre in enumerate(GENRES, 1):
        print(f"{i}. {genre}")
    genre_choice = input("\nChoose genre number (1-8): ")

    try:
        genre_index = int(genre_choice) - 1
        if 0 <= genre_index < len(GENRES):
            genre = GENRES[genre_index]
        else:
            print("Invalid choice. Defaulting to Story.")
            genre = 'Story'
    except ValueError:
        print("Invalid input. Defaulting to Story.")
        genre = 'Story'

    print(f"\nGenerating {genre} about '{theme}'...\n")
    generated_text = generate_creative_text(theme, genre)
    print(generated_text)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        run_cli_mode()
    else:
        app.run(debug=True)