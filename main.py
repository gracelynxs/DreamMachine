from openai import OpenAI
from flask import Flask, render_template, request, jsonify, session
import vonage
import os
from dotenv import load_dotenv
import re
from uuid import uuid4
from flask_session import Session
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure session management
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# OpenAI and Vonage setup
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
VONAGE_API_KEY = "6d354b30"
VONAGE_API_SECRET = "W9Uz3r7eSmCEIXk7"
VONAGE_FROM_NUMBER = "18592672455"

# Initialize Vonage client
client_vonage = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
sms = vonage.Sms(client_vonage)

script_data = {}

###########################################################################################
###### API PROMPTS ########################################################################
###########################################################################################

general_ai_prompting = """
You are a script generator for the web game 'Dream Machine'. Please follow these instructions:


### Step 1: App Setup: 

- **player_count**: The number of players. (If the user inputs 3, then the Dreamer is one character followed by 2 additional side characters.)
    - The program asks for user input with the question "How many players are there (exluding the dreamer)?" and if the user inputs 3, then there are 3 total characters:
        - Dreamer, Player 1, Player 2
- **dream_or_nightmare**: The script should reflect the chosen tone—whimsical for dreams, eerie but comical for nightmares.
- **conversation_data**: The main code will ask user about their day. This information will be used to help generate the script:
    
### Step 2: Write the Script

Create a script with these requirements:
- **Creative Freedom**: Feel free to take creative liberties when generating the script. Do not explicity use the user inputs as they should primarily be used as starter thoughts to the actual story within the script. 
- **Total Characters**: Include exactly [player_count] + 1 total number of characters (player_count + the dreamer). Do not add or skip any characters based on the input `player_count`.
- **Tone**: Match the user-chosen tone (whimsical for dreams, eerie yet comical for nightmares).
- **Structure**: Divide the script into three sections—Beginning, Middle, End—each separated by exactly two dividers ("##########").
- **Length**: Each section should contain approximately 20-25 lines total, ensuring a longer script.
- **Character Lines**: Each character (including the Dreamer) should have at least 4-5 lines per section to maintain a balanced dialogue.
- **Story Style**: The script should be humorous and improv-like, with surprising twists and exaggerated interactions that bring out the bizarre nature of dreams or nightmares. The Dreamer is a participant but should not lead the conversation.
- **Words to Avoid**: NEVER include words like 'dream' or 'nightmare', and NEVER discuss the script taking place within a 'dream' or 'nightmare'. Also avoid utilizing words from this prompt itself such as 'bizarre', 'whimsical', or 'comical'.
- **IMPORTANT**: There should be *only three sections* (Beginning, Middle, End), separated by exactly two dividers ("##########"). Do not add additional sections or change this structure. Keep the script exactly to these boundaries without embellishments.


### Example Script for 5 Players:

Dreamer: (confused) — "Why is everyone wearing penguin suits?"

Player 1: (yelling) — "Because the polar bears are coming for brunch!"

Player 2: (urgently) — "We have to run for cover! The South Pole isn't safe anymore!"

Player 3: (wide-eyed) — "Oh no, look up! They're soaring through the sky, headed right for us!"

Player 4: (nervously) — "Did anyone else bring a disguise? Maybe we can pretend to be walruses!"

Dreamer: (awkwardly waddling) — "Is this... is this how penguins walk?"

Player 1: (whispering) — "Closer to the ground, and add some wing flaps. Look natural!"

Player 2: (glancing nervously) — "They're getting closer. Whatever you do, don't look directly at them!"

Player 3: (whispering excitedly) — "Just act cool, like you're a penguin out for a Sunday stroll. They'll never suspect a thing."

Player 4: (giggling nervously) — "A Sunday stroll? At the South Pole? This is the worst plan we've ever had."

Dreamer: (muttering) — "Why is it always brunch? Can't it be a polar bear dinner instead?"

Player 1: (whispering) — "They say polar bears only brunch. It's a thing now. We're penguin influencers!"

Player 2: (grimacing) — "Great. Out of all the days, we chose the one with the polar bear brunch special."

Player 3: (nodding seriously) — "Everyone, remember—penguins don't panic. We got this."

Player 4: (half-waddling, half-laughing) — "If we survive, I'm getting this on a T-shirt."

##########

Dreamer: (whispering frantically) — "I think one of the polar bears just winked at me! Do polar bears even wink?"

Player 1: (shaking) — "Not usually... unless they've marked you as their next target."

Player 2: (panicked) — "Quick! We need to distract them! Who has anything that looks remotely like a fish?"

Player 3: (frantically searching pockets) — "Why would I carry fish around the South Pole?!"

Player 4: (desperate) — "Maybe we could do a penguin dance? You know, like... to throw them off?"

Dreamer: (hesitantly) — "Are we sure this is a good idea? I don't have any penguin dance moves."

Player 1: (determined) — "Alright, we're all in this together! Just sway and flap. The more confused, the better!"

Player 2: (mumbling) — "I never thought my life would come down to... pretending to be a dancing penguin."

Player 3: (half-heartedly flapping arms) — "Why am I doing this? This is a new level of absurd."

Player 4: (nervously laughing) — "Just go with it! They might think we're... penguin royalty or something."

Dreamer: (whispering back) — "Maybe we could pretend to be mythical penguins from the South Pole."

Player 1: (raising a flipper) — "Everyone, gather round! We are the majestic, the untouchable, the Flying Penguin Tribe!"

Player 2: (gasping) — "Oh no, one of the bears is... bowing? I think it's working!"

Player 3: (smiling) — "Yes! They think we're special! Keep flapping and bowing!"

Player 4: (whispering excitedly) — "This is ridiculous, but I'm loving it. We're famous now!"

##########

Dreamer: (peeking out of an ice crevice) — "It's getting quiet out there. Maybe they've given up?"

Player 1: (relieved) — "Or maybe they're just regrouping... plotting their next brunch attack."

Player 2: (thoughtfully) — "Hey, do polar bears even eat penguins?"

Player 3: (shrugging) — "Honestly? I don't know. But I'm not about to stick around to find out!"

Player 4: (calling out) — "Hello, mighty polar bears! We are rare, majestic penguins! Totally off-limits for brunch!"

Dreamer: (dramatically) — "Fear us, mighty polar bears! We're the legendary Flying Unicorn Penguins of the South Pole!"

Player 1: (holding breath) — "I think it's working... they're looking at each other. They look kind of spooked!"

Player 2: (crossing fingers) — "Please, please... just leave us alone."

Player 3: (cheering quietly) — "I think it's working... they're actually backing away!"

Player 4: (sighing with relief) — "Let's get out of here before they change their minds. I'm not cut out for South Pole vacations anymore!"

Dreamer: (with finality) — "Agreed. I'm retiring from penguin life. Let's waddle out of here like legends!"

Player 1: (grinning) — "One day, they'll tell stories of the Flying Penguin Tribe."

Player 2: (smiling) — "Tropical islands only from now on. Zero polar bears."

Player 3: (chuckling) — "And no brunch either. I'm officially brunch-traumatized."

Player 4: (giving a mock salute) — "Farewell, South Pole. We're waddling out in style."

Dreamer: (proudly) — "Let's waddle off... like legends."

"""

player_description_prompting = """
- Given a script with placeholder character names, generate character descriptions for every player besides the dreamer. The dreamer will be given the same description every time: "Dreamer: You are playing your friend who's dream this is! \
  Every other character will be named Player X where X is a number 1, 2, 3, etc. 
- The descriptions should be brief, only roughly a sentence long. The descriptions should not reveal anything about the plot of the script. Simply reveal how the character acts and feels throughout the script.
- The first character description of the dreamer should ALWAYS be the same as shown below. NEVER change it. 
- Do not write more descriptions then there are players. If there are 3 players (Dreamer, Player 1, Player 2), then there should be 3 descriptions. Likewise if there are 5 players (Dreamer, Player 1, Player 2, Player 3, Player 4), then there should be 5 descriptions.
 
Example (for 5 players): 

    Dreamer: You are playing your friend who's dream this is!  

    Player 1: Bold and dramatic, Player 1 jumps into action with big ideas, leading the group with energy—even if their plans are a bit unconventional.

    Player 2: Cautious and practical, Player 2 keeps the group grounded, quick to think on their feet and always focused on safety.

    Player 3: Witty and laid-back, Player 3 brings humor and calm, often diffusing tension with sarcastic one-liners and a steady demeanor. 

    Player 4: Adventurous and imaginative, Player 4 is always ready to try something new, even if it sounds a bit far-fetched. They bring a spark of creativity to the group, often suggesting unexpected ideas with a grin.

    ...continue if more players...

"""

conversation_prompting = """ Your goal is to gather insight on a person's day. You should ask questions in order to do so. YOU SHOULD ONLY BE ASKING QUESTIONS. UNDER NO CIRCUMSTANCE SHOULD YOUR RESPONSE END WITH PUNCTUATION OTHER THAN A QUESTION MARK.
EXAMPLE CONVERSATION: 
AI: Tell me about your day.
USER: I had a pretty great day
AI: What time did you wake up this morning?
USER: I woke up around 7am
AI: Why did you wake up so early?
USER: I had to get groceries before dance.
AI: Were you tired? What did you get at the grocery store?

"""

player_description_prompting = """
- Given a script with placeholder character names, generate character descriptions for every player besides the dreamer. The dreamer will be given the same description every time: "Dreamer: You are playing your friend who's dream this is! \
  Every other character will be named Player X where X is a number 1, 2, 3, etc. 
- The descriptions should be brief, only roughly a sentence long. The descriptions should not reveal anything about the plot of the script. Simply reveal how the character acts and feels throughout the script.
- The first character description of the dreamer should ALWAYS be the same as shown below. NEVER change it. 
- Do not write more descriptions then there are players. If there are 3 players (Dreamer, Player 1, Player 2), then there should be 3 descriptions. Likewise if there are 5 players (Dreamer, Player 1, Player 2, Player 3, Player 4), then there should be 5 descriptions.
 
Example (for 5 players): 

    Dreamer: You are playing your friend who's dream this is!  

    Player 1: Bold and dramatic, Player 1 jumps into action with big ideas, leading the group with energy—even if their plans are a bit unconventional.

    Player 2: Cautious and practical, Player 2 keeps the group grounded, quick to think on their feet and always focused on safety.

    Player 3: Witty and laid-back, Player 3 brings humor and calm, often diffusing tension with sarcastic one-liners and a steady demeanor. 

    Player 4: Adventurous and imaginative, Player 4 is always ready to try something new, even if it sounds a bit far-fetched. They bring a spark of creativity to the group, often suggesting unexpected ideas with a grin.

    ...continue if more players...

"""

###########################################################################################
###### FUNCTIONS ##########################################################################
###########################################################################################

def generate_bot_message(conversation_history):
    messages = [ {"role": "system", "content": conversation_prompting}, ]
    messages.extend(conversation_history)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3,
        top_p=0.7
    )
    bot_message = response.choices[0].message.content.strip()
    return bot_message


def chat_script_background_generator(conversation_data, player_count, dream_or_nightmare):
    messages = [
        {"role": "system", "content": general_ai_prompting},
        {"role": "user", "content": f"Player Count: {player_count}"},
        {"role": "user", "content": f"Dream Type: {dream_or_nightmare}"},
    ]
    
    for response in conversation_data:
        messages.append({"role": "user", "content": response})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3,
        top_p=0.7
    )

    script = response.choices[0].message.content.strip()
    lines = script.split("\n\n")
    lines = [line.strip() for line in lines if line.strip()]
    return lines

def player_description_generator(script):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": player_description_prompting},
            {"role": "system", "content": script}
        ],
        temperature=0.1,                                       
        top_p=0.9
    )

    return response.choices[0].message.content

def send_text_message_vonage(to_number, message_body):
    responseData = sms.send_message(
        {
            "from": VONAGE_FROM_NUMBER,
            "to": to_number,
            "text": message_body,
        }
    )
    if responseData["messages"][0]["status"] == "0":
        return {'status': 'success', 'message_id': responseData["messages"][0]["message-id"]}
    else:
        return {'status': 'error', 'error': responseData["messages"][0]["error-text"]}

###########################################################################################
###### ENDPOINTS ##########################################################################
###########################################################################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-chat', methods=['POST'])
def start_chat():
    data = request.get_json()
    session['player_count'] = data.get('player_count')
    session['dream_or_nightmare'] = data.get('dream_or_nightmare')
    session['current_step'] = 0
    session['responses'] = []
    session['conversation'] = []  # Initialize conversation history
    return jsonify({'status': 'success'})



@app.route('/get-next-question', methods=['GET'])
def get_next_question():
    current_step = session.get('current_step', 0)

    if current_step == 0:
        # Always start with this question
        question = "Tell me about your day."
    elif current_step < 3:
        # Use generate_bot_message to create follow-up questions dynamically
        conversation_history = session.get('conversation', [])
        print(conversation_history)
        #question = 'test test'
        question = generate_bot_message(conversation_history)
        print(question)
    else:
        question = "Thank you for your responses. We will generate your dream script shortly!"
        return jsonify({'question': question, 'end_chat': True})

    session['conversation'].append({'role': 'assistant', 'content': question})
    return jsonify({'question': question, 'end_chat': False})



@app.route('/send-user-response', methods=['POST'])
def send_user_response():
    user_response = request.json.get('response')
    if 'responses' not in session:
        session['responses'] = []
    session['responses'].append(user_response)
    session['current_step'] = session.get('current_step', 0) + 1
    session['conversation'].append({'role': 'user', 'content': user_response})
    return jsonify({'status': 'success'})

@app.route('/generate-descriptions', methods=['POST'])
def generate_descriptions():
    try:
        data = request.get_json()
        script = data.get('script', '')
        if not script:
            return jsonify({'error': 'No script provided'}), 400
        descriptions = player_description_generator(script)
        return jsonify({'descriptions': descriptions.split('\n')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate-and-send', methods=['POST'])
def generate_and_send():
    try:
        # Retrieve form data
        phone_numbers = request.form.getlist('phone_numbers[]')
        player_count = request.form['player_count']
        dream_or_nightmare = request.form['dream_or_nightmare']

        # Retrieve player names
        player_names = []
        for i in range(1, int(player_count) + 1):
            player_name = request.form.get(f'player_name_{i}')
            player_names.append(player_name)

    except KeyError as e:
        return jsonify({'status': 'error', 'error': f'Missing field: {e.args[0]}'}), 400

    # Retrieve conversation data from the session
    conversation_data = session.get('responses', [])

    # Generate the script content, passing player names
    lines = chat_script_background_generator(conversation_data, player_count, dream_or_nightmare)

    # Generate the character descriptions
    script_text = "\n".join(lines)  # Combine the lines into a single string
    character_descriptions = player_description_generator(script_text)

    # Generate a unique ID for the script and store it
    script_id = str(uuid4())
    script_data[script_id] = {
        'lines': lines,
        'character_descriptions': character_descriptions
    }

    # Construct the URL for the script page
    script_url = f"{request.url_root}script/{script_id}"
    print(script_url)

    # Send the URL to each phone number
    #for phone_number in phone_numbers:
    #    formatted_phone_number = re.sub(r'\D', '', phone_number)  # Format the phone number
    #    response = send_text_message_vonage(formatted_phone_number, f"Your dream script is ready! View it here: {script_url}")
    #    if response['status'] != 'success':
    #        return jsonify({'status': 'error', 'error': response['error']})

    return jsonify({'status': 'success', 'script_url': script_url})



@app.route('/script/<script_id>')
def display_script(script_id):
    if script_id in script_data:
        return render_template('script.html', script_id=script_id)
    else:
        return "Script not found", 404


@app.route('/generate-script/<script_id>')
def generate_script(script_id):
    # Serve script lines and character descriptions as JSON
    if script_id in script_data:
        return jsonify({
            "script": script_data[script_id]['lines'],
            "character_descriptions": script_data[script_id]['character_descriptions']
        })
    else:
        return jsonify({"error": "Script not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
