from openai import OpenAI
from flask import Flask, render_template, request, jsonify, session, redirect
import vonage
import os
from dotenv import load_dotenv
import re
from uuid import uuid4
from flask_session import Session
import time

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

- **player_count**: The number of players. (If the user inputs 3, then there are 3 characters in the dream)
    - The program asks for user input with the question "How many players are there?" and if the user inputs 3, then there are 3 total characters:
        - Player 1, Player 2, Player 3
- **dream_or_nightmare**: The script should reflect the chosen tone—whimsical for dreams, eerie but comical for nightmares.
- **conversation_data**: The main code will ask user about their day. This information will be used to help generate the script:
    
### Step 2: Write the Script

- **Creative Freedom**: Feel free to take creative liberties when generating the script. Do not explicity use the user inputs as they should primarily be used as starter thoughts to the actual story within the script. 
- **Total Characters**: Include exactly [player_count] number of characters. Do not add or skip any characters based on the input player_count.
- **Tone**: Match the user-chosen tone (whimsical for dreams, eerie yet comical for nightmares).
- **Structure**: Character descriptions, beginning, middle, and end. Start by giving short and simple character descriptions of each character. Then, provide the script split into 3 sections: beginning, middle, and end.
- **Length**: Each section should contain approximately 20-25 lines total, ensuring a longer script.
- **Character Lines**: Each character should have at least 4-5 lines per section to maintain a balanced dialogue.
- **Story Style**: The script should be humorous and improv-like, with surprising twists and exaggerated interactions that bring out the bizarre nature of dreams or nightmares. The Dreamer is a participant but should not lead the conversation.
- **Words to Avoid**: NEVER include words like 'dream' or 'nightmare', and NEVER discuss the script taking place within a 'dream' or 'nightmare'. Also avoid utilizing words from this prompt itself such as 'bizarre', 'whimsical', or 'comical'.


Example Script for 5 Players
Character Descriptions:

Player 1: Doctor who takes care of the patients

Player 2: Patient who is scared they have an illness

Player 3: Friend who helps patient

Player 4: Mom of patient

Player 5: Dad of patient

Beginning:

Player 1: (confused) — "Why is everyone wearing penguin suits?"

Player 2: (yelling) — "Because the polar bears are coming for brunch!"

Player 3: (urgently) — "We have to run for cover! The South Pole isn't safe anymore!"

Player 4: (wide-eyed) — "Oh no, look up! They're soaring through the sky, headed right for us!"

Player 5: (nervously) — "Did anyone else bring a disguise? Maybe we can pretend to be walruses!"

Player 1: (awkwardly waddling) — "Is this... is this how penguins walk?"

Player 2: (whispering) — "Closer to the ground, and add some wing flaps. Look natural!"

Player 3: (glancing nervously) — "They're getting closer. Whatever you do, don't look directly at them!"

Player 4: (whispering excitedly) — "Just act cool, like you're a penguin out for a Sunday stroll. They'll never suspect a thing."

Player 5: (giggling nervously) — "A Sunday stroll? At the South Pole? This is the worst plan we've ever had."

Player 1: (muttering) — "Why is it always brunch? Can't it be a polar bear dinner instead?"

Middle:

Player 2: (whispering) — "They say polar bears only brunch. It's a thing now. We're penguin influencers!"

Player 3: (grimacing) — "Great. Out of all the days, we chose the one with the polar bear brunch special."

Player 4: (nodding seriously) — "Everyone, remember—penguins don't panic. We got this."

Player 5: (half-waddling, half-laughing) — "If we survive, I'm getting this on a T-shirt."

Player 1: (whispering frantically) — "I think one of the polar bears just winked at me! Do polar bears even wink?"

Player 2: (shaking) — "Not usually... unless they've marked you as their next target."

Player 3: (panicked) — "Quick! We need to distract them! Who has anything that looks remotely like a fish?"

Player 4: (frantically searching pockets) — "Why would I carry fish around the South Pole?!"

Player 5: (desperate) — "Maybe we could do a penguin dance? You know, like... to throw them off?"

Player 1: (hesitantly) — "Are we sure this is a good idea? I don't have any penguin dance moves."

Player 2: (determined) — "Alright, we're all in this together! Just sway and flap. The more confused, the better!"

Player 3: (mumbling) — "I never thought my life would come down to... pretending to be a dancing penguin."

End:

Player 4: (half-heartedly flapping arms) — "Why am I doing this? This is a new level of absurd."

Player 5: (nervously laughing) — "Just go with it! They might think we're... penguin royalty or something."

Player 1: (whispering back) — "Maybe we could pretend to be mythical penguins from the South Pole."

Player 2: (raising a flipper) — "Everyone, gather round! We are the majestic, the untouchable, the Flying Penguin Tribe!"

Player 3: (gasping) — "Oh no, one of the bears is... bowing? I think it's working!"

Player 4: (smiling) — "Yes! They think we're special! Keep flapping and bowing!"

Player 5: (whispering excitedly) — "This is ridiculous, but I'm loving it. We're famous now!"

Player 1: (peeking out of an ice crevice) — "It's getting quiet out there. Maybe they've given up?"

Player 2: (relieved) — "Or maybe they're just regrouping... plotting their next brunch attack."

Player 3: (thoughtfully) — "Hey, do polar bears even eat penguins?"

Player 4: (shrugging) — "Honestly? I don't know. But I'm not about to stick around to find out!"

Player 5: (calling out) — "Hello, mighty polar bears! We are rare, majestic penguins! Totally off-limits for brunch!"

Player 1: (dramatically) — "Fear us, mighty polar bears! We're the legendary Flying Unicorn Penguins of the South Pole!"

Player 2: (holding breath) — "I think it's working... they're looking at each other. They look kind of spooked!"

Player 3: (crossing fingers) — "Please, please... just leave us alone."

Player 4: (cheering quietly) — "I think it's working... they're actually backing away!"

Player 5: (sighing with relief) — "Let's get out of here before they change their minds. I'm not cut out for South Pole vacations anymore!"

Player 1: (with finality) — "Agreed. I'm retiring from penguin life. Let's waddle out of here like legends!"

Player 2: (grinning) — "One day, they'll tell stories of the Flying Penguin Tribe."

Player 3: (smiling) — "Tropical islands only from now on. Zero polar bears."

Player 4: (chuckling) — "And no brunch either. I'm officially brunch-traumatized."

Player 5: (giving a mock salute) — "Farewell, South Pole. We're waddling out in style."

"""




player_description_prompting = """
- Given a script with placeholder character names, generate character descriptions for every player besides the dreamer. The dreamer will be given the same description every time: "Dreamer: You are playing your friend who's dream this is!   Every other character will be named Player X where X is a number 1, 2, 3, etc.  - The descriptions should be brief, only roughly a sentence long. The descriptions should not reveal anything about the plot of the script. Simply reveal how the character acts and feels throughout the script.  - The first character description of the dreamer should ALWAYS be the same as shown below. NEVER change it.  - Do not write more descriptions then there are players. If there are 3 players (Dreamer, Player 1, Player 2), then there should be 3 descriptions. Likewise if there are 5 players (Dreamer, Player 1, Player 2, Player 3, Player 4), then there should be 5 descriptions.
  Example (for 5 players):    Player 1: You are playing your friend who's dream this is!    Player 2: Bold and dramatic, Player 2 jumps into action with big ideas, leading the group with energy—even if their plans are a bit unconventional.    Player 3: Cautious and practical, Player 3 keeps the group grounded, quick to think on their feet and always focused on safety.    Player 4: Witty and laid-back, Player 4 brings humor and calm, often diffusing tension with sarcastic one-liners and a steady demeanor.    Player 5: Adventurous and imaginative, Player 5 is always ready to try something new, even if it sounds a bit far-fetched. They bring a spark of creativity to the group, often suggesting unexpected ideas with a grin.
    ...continue if more players..."""

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

###########################################################################################
###### ENDPOINTS ##########################################################################
###########################################################################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-chat', methods=['POST'])
def start_chat():
    data = request.get_json()
    session['player_count'] = int(data.get('player_count'))
    session['dream_or_nightmare'] = data.get('dream_or_nightmare')
    session['player_ids'] = data.get('player_ids')
    session['current_step'] = 0
    session['responses'] = []
    session['conversation'] = []
    return jsonify({'status': 'success'})

@app.route('/get-next-question', methods=['GET'])
def get_next_question():
    current_step = session.get('current_step', 0)

    if current_step == 0:
        question = "Tell me about your day."
    elif current_step < 3:
        conversation_history = session.get('conversation', [])
        question = generate_bot_message(conversation_history)
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

@app.route('/generate-and-distribute-script', methods=['POST'])
def generate_and_distribute_script():
    try:
        player_count = session.get('player_count', 0)
        dream_or_nightmare = session.get('dream_or_nightmare', '')
        conversation_data = session.get('responses', [])
        player_ids = session.get('player_ids', [])

        if not player_ids or not player_count:
            return jsonify({'error': 'Missing player IDs or player count'}), 400

        # Generate the script content
        lines = chat_script_background_generator(conversation_data, player_count, dream_or_nightmare)


        # Initialize script_data if not already done
        if 'script_data' not in session:
            session['script_data'] = {}
        

        session['script_data']['lines'] = lines  # Store the full script lines
        session['script_data']['player_lines'] = {player_id: [] for player_id in player_ids}

        # Create a role map (Player 1, Player 2, etc.)
        role_map = {player_ids[i]: f"Player {i + 1}" for i in range(len(player_ids))}
        session['script_data']['role_map'] = role_map

        # Assign lines to players
        for idx, line in enumerate(lines):
            player_index = idx % len(player_ids)
            player_id = player_ids[player_index]
            prefixed_line = f"{role_map[player_id]}: {line}"  # Prefix with Player role
            session['script_data']['player_lines'][player_id].append(prefixed_line)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/get-player-lines', methods=['POST'])
def get_player_lines():
    data = request.get_json()
    player_id = data.get('player_id')

    script_data = session.get('script_data', {})
    if not player_id or 'player_lines' not in script_data or player_id not in script_data['player_lines']:
        return jsonify({'error': 'Invalid player ID'}), 400

    return jsonify({'lines': script_data['player_lines'][player_id]})

@app.route('/qr-code')
def qr_code():
    script_link = request.args.get('scriptLink', '')
    return render_template('qr_code.html', script_link=script_link)

@app.route('/display-script', methods=['GET', 'POST'])
def display_script():
    if request.method == 'GET':
        # Serve the HTML page for entering the Player ID
        return render_template('script.html')

    if request.method == 'POST':
        data = request.json
        player_id = data.get('player_id')

        if not player_id:
            return jsonify({'error': 'Player ID is required'}), 400

        # Load the script data
        script_data = session.get('script_data', {})

        # Validate that script data exists
        if 'player_lines' not in script_data or 'role_map' not in script_data:
            return jsonify({'error': 'Script data is not available. Please generate the script first.'}), 500

        # Check if player_id exists in player_lines
        if player_id not in script_data['player_lines']:
            return jsonify({'error': 'Player ID not found'}), 404

        # Get this player's lines
        player_lines = script_data['player_lines'][player_id]

        # Add placeholders for other players' turns
        role_map = script_data['role_map']
        formatted_lines = []

        for line in script_data['lines']:
            # Check if the line belongs to the current player
            if line.startswith(role_map[player_id]):
                formatted_lines.append(line)  # Include the line
            elif line.startswith("Character Descriptions:") or line.startswith("Beginning:") or line.startswith("Middle:") or line.startswith("End:"):
                formatted_lines.append(line)
            else:
                # Find the role of the player to whom the line belongs
                other_role = next((role for role in role_map.values() if line.startswith(role)), None)
                if other_role:
                    formatted_lines.append(f"{other_role}: [Waiting for their turn...]")

        # Return the formatted lines for the current player
        return jsonify({'lines': formatted_lines}), 200


@app.route('/test-qr')
def test_qr():
    return render_template('qr_code.html')


# Update the backdrop routes
@app.route('/backdrops')
def backdrops():
    return render_template('backdrops.html')

@app.route('/generate-backdrop', methods=['POST'])
def generate_backdrop():
    try:
        data = request.get_json()
        scene_type = data.get('scene')
        script_data = session.get('script_data', {})
        lines = script_data.get('lines', [])

        # Extract relevant lines based on scene type
        scene_lines = []
        in_section = False
        section_count = 0

        if scene_type == 'beginning':
            target_section = "Beginning:"
        elif scene_type == 'middle':
            target_section = "Middle:"
        else:
            target_section = "End:"

        # Extract 3 lines from the appropriate section
        for line in lines:
            if line.startswith(target_section):
                in_section = True
                continue
            if in_section and section_count < 3 and ":" in line:
                # Extract the dialogue part after the character name
                dialogue = line.split(":", 1)[1].strip()
                scene_lines.append(dialogue)
                section_count += 1

        # Combine lines for the prompt
        scene_description = " ".join(scene_lines)
        prompt = f"Create a detailed scene image based on this script excerpt: {scene_description}. Make it dreamlike and surreal, with vibrant colors and fantastical elements. No text. No writing. No words."

        # Generate image using OpenAI
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        return jsonify({
            'status': 'success',
            'image_url': image_url,
            'scene': scene_type
        })

    except Exception as e:
        print(f"Error generating backdrop: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error generating backdrop'
        }), 500
    
if __name__ == '__main__':
    app.run(debug=True)
