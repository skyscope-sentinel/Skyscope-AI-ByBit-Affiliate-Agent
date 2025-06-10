
import yaml
import os
import random
from datetime import datetime
import google.generativeai as genai # Added for LLM integration
import re # For sanitizing filenames or text

CONFIG_PATH = "ai_marketing_agent/config/settings.yaml"
OUTPUT_DIR = "ai_marketing_agent/generated_content"
IDEAS_FILE = os.path.join(OUTPUT_DIR, "content_ideas.txt")
NEXT_IDEA_FILE = os.path.join(OUTPUT_DIR, "next_article_to_generate.txt") # Can use this for ad copy context

def load_config():
    '''Loads the configuration from the YAML file.'''
    try:
        with open(CONFIG_PATH, 'r') as f: config = yaml.safe_load(f)
        if not config: # Handle empty config file
            print(f"CRITICAL: Config file {CONFIG_PATH} is empty or malformed!")
            return None
        return config
    except FileNotFoundError:
        print(f"CRITICAL: Config file {CONFIG_PATH} not found!")
        return None
    except Exception as e:
        print(f"Error loading config {CONFIG_PATH}: {e}")
        return None

def load_idea_for_ads():
    '''Loads an idea for ad generation, prioritizing the strategic choice.'''
    next_idea = None
    try:
        os.makedirs(os.path.dirname(NEXT_IDEA_FILE), exist_ok=True) # Ensure dir exists
        if os.path.exists(NEXT_IDEA_FILE):
            with open(NEXT_IDEA_FILE, 'r') as f:
                next_idea = f.read().strip()
            if next_idea:
                print(f"Using strategically chosen idea for ad copy: {next_idea}")
                return next_idea
            else:
                print(f"Warning: {NEXT_IDEA_FILE} was empty.")
        else:
            print(f"Info: Strategic choice file {NEXT_IDEA_FILE} not found.")
    except Exception as e:
        print(f"Error loading from {NEXT_IDEA_FILE}: {e}. Will try fallback.")

    try:
        os.makedirs(os.path.dirname(IDEAS_FILE), exist_ok=True) # Ensure dir exists
        if os.path.exists(IDEAS_FILE):
            with open(IDEAS_FILE, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("=") and not "Content Ideas Generated on" in line]
                lines = [line for line in lines if line]
                ideas = [line[2:] if line.startswith("- ") else line for line in lines if line.strip()]
                if ideas:
                    chosen_idea = random.choice(ideas)
                    print(f"Using random idea for ad copy from {IDEAS_FILE}: {chosen_idea}")
                    return chosen_idea
                else:
                    print(f"Warning: {IDEAS_FILE} was empty or had no usable ideas.")
        else:
            print(f"Info: Fallback ideas file {IDEAS_FILE} not found.")
    except Exception as e:
        print(f"Error loading from {IDEAS_FILE}: {e}")

    print("No idea found from files, using default placeholder idea.")
    return "General Bybit Platform Promotion"


def generate_llm_ad_copy(idea_or_feature, api_key, config):
    '''Generates ad copy using LLM.'''
    if not config: return {"error": "Config not loaded for LLM ad copy."}

    print(f"\nAttempting LLM ad copy generation for: {idea_or_feature}")

    restricted_keywords_list = config.get('compliance', {}).get('restricted_keywords', [])
    prompt = f'''
You are an AI Marketing Assistant specialized in creating concise and effective ad copy for Google Ads.
Your task is to generate ad copy for Bybit, a cryptocurrency exchange, based on the following topic.

**Ad Topic/Feature:** {idea_or_feature}

**Ad Copy Requirements (Strict):**
1.  **Headline 1:** Max 30 characters. Must be engaging and relevant to the topic. Include a keyword if possible.
2.  **Headline 2:** Max 30 characters. Highlight a key benefit or unique selling proposition.
3.  **Headline 3 (Optional but Recommended):** Max 30 characters. Can be a call to action or additional benefit.
4.  **Description 1:** Max 90 characters. Expand on headlines, provide more details.
5.  **Description 2 (Optional):** Max 90 characters. Can offer social proof, urgency, or another benefit.
6.  **Tone:** Persuasive, clear, and trustworthy.
7.  **Compliance:**
    *   AVOID ALL PROHIBITED PHRASES: {restricted_keywords_list}.
    *   DO NOT make profit guarantees.
    *   Focus on platform features, security, ease of use.
8.  **Call to Action (CTA):** Ensure a clear CTA is present or implied (e.g., "Sign Up Now", "Trade Today", "Learn More").

**Output Format (Strict JSON-like structure, using simple text):**
Provide a few distinct ad variations if possible.
Format each ad variation like this:
Variation 1:
H1: [Your Headline 1]
H2: [Your Headline 2]
H3: [Your Headline 3]
D1: [Your Description 1]
D2: [Your Description 2]

Variation 2:
H1: [Your Headline 1]
H2: [Your Headline 2]
H3: [Your Headline 3]
D1: [Your Description 1]
D2: [Your Description 2]

Start directly with "Variation 1:". Do not include any other preamble.
'''
    try:
        genai.configure(api_key=api_key)
        model_name = "gemini-1.0-pro"
        model = genai.GenerativeModel(model_name)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
        ]
        response = model.generate_content(prompt, safety_settings=safety_settings)

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            return {"error": f"Prompt blocked by API ({response.prompt_feedback.block_reason})."}
        if not response.candidates:
            return {"error": f"No candidates from LLM. Response: {response}"}

        candidate = response.candidates[0]
        if candidate.finish_reason.name != "STOP":
            if candidate.finish_reason.name == "SAFETY":
                return {"error": "Generation stopped by safety filter for ads."}
            return {"error": f"Generation finished with reason '{candidate.finish_reason.name}'."}

        if candidate.content and candidate.content.parts:
            raw_llm_output = "".join(part.text for part in candidate.content.parts)
            parsed_ads = []
            current_ad = {}
            normalized_output = raw_llm_output.replace('\r\n', '\n').replace('\r', '\n')
            for line in normalized_output.split('\n'):
                line = line.strip()
                if not line: continue
                if line.startswith("Variation"):
                    if current_ad: parsed_ads.append(current_ad)
                    current_ad = {"variation_title": line}
                elif line.startswith("H1:"): current_ad["h1"] = line[3:].strip()
                elif line.startswith("H2:"): current_ad["h2"] = line[3:].strip()
                elif line.startswith("H3:"): current_ad["h3"] = line[3:].strip()
                elif line.startswith("D1:"): current_ad["d1"] = line[3:].strip()
                elif line.startswith("D2:"): current_ad["d2"] = line[3:].strip()
            if current_ad: parsed_ads.append(current_ad)

            if not parsed_ads:
                 return {"error": "LLM output generated but could not parse ad variations.", "raw_output": raw_llm_output}
            return {"ads": parsed_ads, "raw_output": raw_llm_output}

        return {"error": "No valid content parts in LLM ad copy response."}

    except Exception as e:
        return {"error": f"Exception during LLM ad copy call: {e}"}


def save_ad_copy_examples(ad_data, input_idea, llm_used=False):
    '''Saves the generated ad copy examples to a file.'''
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_tag = "llm" if llm_used else "template"
    sanitized_idea = re.sub(r'[^a-zA-Z0-9_]', '_', input_idea[:20]).lower()
    filename = f"ad_copy_{source_tag}_{sanitized_idea}_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    header = f"--- Ad Copy Examples ({source_tag.upper()}) ---\n"
    header += f"Topic/Idea: {input_idea}\n"
    header += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += "=" * 50 + "\n\n"

    try:
        with open(filepath, 'w') as f:
            f.write(header)
            if ad_data.get("error"):
                f.write(f"Error generating ad copy: {ad_data['error']}\n")
                if ad_data.get("raw_output"):
                    f.write(f"Raw LLM Output:\n{ad_data['raw_output']}\n")
                return

            if llm_used:
                if ad_data.get("ads"):
                    for i, ad_variation in enumerate(ad_data.get("ads", [])):
                        f.write(f"{ad_variation.get('variation_title', f'Variation {i+1}')}:\n")
                        f.write(f"  H1: {ad_variation.get('h1', 'N/A')}\n")
                        f.write(f"  H2: {ad_variation.get('h2', 'N/A')}\n")
                        f.write(f"  H3: {ad_variation.get('h3', 'N/A')}\n")
                        f.write(f"  D1: {ad_variation.get('d1', 'N/A')}\n")
                        f.write(f"  D2: {ad_variation.get('d2', 'N/A')}\n\n")
                else:
                    f.write("No ad variations parsed from LLM output.\n")
                    if ad_data.get("raw_output"):
                         f.write(f"Raw LLM Output:\n{ad_data.get('raw_output')}\n")
            else:
                 f.write("Template-based ad copy generation is not active in this version.\n")

        print(f"Successfully saved ad copy examples to {filepath}")
    except IOError as e:
        print(f"Error saving ad copy examples to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting Ad Copy Generator...")
    config_data = load_config()
    if not config_data:
        print("Exiting due to config load failure.")
        exit(1)

    selected_input_idea = load_idea_for_ads()

    use_llm_for_ads = False
    gemini_api_key_name = config_data.get('gemini_api_key_env_var', "GEMINI_API_KEY")
    api_key = os.environ.get(gemini_api_key_name)

    if api_key:
        print(f"Gemini API Key ({gemini_api_key_name}) found. Will attempt LLM-based ad copy generation.")
        use_llm_for_ads = True
    else:
        print(f"Gemini API Key ({gemini_api_key_name}) not found. LLM-based ad copy generation will be SKIPPED.")
        print("To enable LLM ad copy, run 'python ai_marketing_agent/scripts/setup_env.py' or set the env var manually.")

    if use_llm_for_ads:
        ad_copy_data = generate_llm_ad_copy(selected_input_idea, api_key, config_data)
        save_ad_copy_examples(ad_copy_data, selected_input_idea, llm_used=True)
    else:
        print("Skipping ad copy generation as API key is not available and no template fallback is active.")

    print("\nAd Copy Generator script finished.")
