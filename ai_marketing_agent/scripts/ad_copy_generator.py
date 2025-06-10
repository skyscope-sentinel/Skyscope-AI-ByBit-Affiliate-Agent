feat/ai-marketing-agent-foundation

=======
main
import yaml
import os
import random
from datetime import datetime
feat/ai-marketing-agent-foundation
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
=======

CONFIG_PATH = "ai_marketing_agent/config/settings.yaml"
OUTPUT_DIR = "ai_marketing_agent/generated_content"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ad_copy_examples.txt")
IDEAS_FILE = os.path.join(OUTPUT_DIR, "content_ideas.txt") # Optional: to pick an idea

def load_config():
    """Loads the configuration from the YAML file."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        return config
main
    except Exception as e:
        print(f"Error loading config {CONFIG_PATH}: {e}")
        return None
feat/ai-marketing-agent-foundation
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
=======
def load_content_ideas():
    """Loads content ideas from the ideas file (optional)."""
    try:
        with open(IDEAS_FILE, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("=")]
            if len(lines) > 1:
                if "Content Ideas Generated on" in lines[0]:
                    lines = lines[1:]
                lines = [line for line in lines if not all(c == '=' for c in line)]
                lines = [line for line in lines if line.strip()]
                return [line[2:] if line.startswith("- ") else line for line in lines if line.strip()]
        return []
    except Exception: # Silently fail if not found, as it's optional
        return []

def generate_ad_copy(idea_or_feature, config):
    """Generates simulated ad copy examples."""
    if not config:
        return {"error": "Config not loaded."}

    keywords = config.get('target_keywords', ['Bybit', 'crypto trading'])
    affiliate_link_placeholder = config.get('bybit_affiliate_link', 'YOUR_BYBIT_LINK') # For display URL
    disclosure = config.get('compliance', {}).get('disclosure_texts', {}).get('default', '#Ad')
    restricted_keywords = config.get('compliance', {}).get('restricted_keywords', [])

    # Helper to check for restricted words
    def check_restricted(text):
        for r_keyword in restricted_keywords:
            if r_keyword.lower() in text.lower():
                return True
        return False

    ad_examples = []

    # Example 1: Generic Ad for Bybit
    headline1 = f"Trade Crypto on Bybit {disclosure}"
    headline2 = f"Low Fees, Top Security"
    headline3 = f"Sign Up & Get Bonus!"
    description1 = f"Join Bybit for advanced trading tools, 24/7 support. {random.choice(keywords)}. Sign up today!"
    description2 = f"Explore Spot, Derivatives, and Earn products. Your premier crypto destination."
    display_url = affiliate_link_placeholder.split("://")[1].split("/")[0] + "/Trade" # e.g. bybit.com/Trade

    if not any(check_restricted(h) for h in [headline1, headline2, headline3]) and not any(check_restricted(d) for d in [description1, description2]):
        ad_examples.append({
            "campaign_name": "Bybit_Brand_Generic",
            "ad_group": "General_Crypto_Interest",
            "headlines": [headline1, headline2, headline3],
            "descriptions": [description1, description2],
            "final_url_placeholder": affiliate_link_placeholder,
            "display_url": display_url,
            "notes": "Generic brand awareness ad."
        })

    # Example 2: Ad based on the input idea/feature
    input_keyword = idea_or_feature.replace("Bybit's", "").replace("Understanding", "").replace("Exploring", "").strip().split(":")[0] # Simplify

    headline1_feat = f"{input_keyword} on Bybit {disclosure}"
    headline2_feat = f"Learn & Trade Today"
    headline3_feat = f"Expert Tools & Guides"
    description1_feat = f"Discover {idea_or_feature}. Bybit offers resources and tools for all levels. {affiliate_link_placeholder}"
    description2_feat = f"Safe, secure, and user-friendly platform. {random.choice(keywords)}."

    if not any(check_restricted(h) for h in [headline1_feat, headline2_feat, headline3_feat]) and not any(check_restricted(d) for d in [description1_feat, description2_feat]):
        ad_examples.append({
            "campaign_name": f"Bybit_Feature_{input_keyword.replace(' ', '_')[:15]}",
            "ad_group": f"{input_keyword.replace(' ', '_')[:20]}_Target",
            "headlines": [headline1_feat, headline2_feat, headline3_feat],
            "descriptions": [description1_feat, description2_feat],
            "final_url_placeholder": affiliate_link_placeholder,
            "display_url": display_url,
            "notes": f"Ad focusing on: {idea_or_feature}"
        })

    # Placeholder for Google Ads API call
    api_call_simulation = """
    # --- SIMULATED GOOGLE ADS API CALL ---
    # from google.ads.googleads.client import GoogleAdsClient
    # client = GoogleAdsClient.load_from_storage('path/to/google-ads.yaml') # Needs auth
    # campaign_service = client.get_service('CampaignService')
    # ad_group_ad_service = client.get_service('AdGroupAdService')
    # ... many steps to build campaign, ad group, and ad objects ...
    # print("Ad campaign created/updated via Google Ads API (Simulated).")
    # --- END SIMULATION ---
    """

    return {"ads": ad_examples, "api_simulation": api_call_simulation}

def save_ad_copy_examples(ad_data):
    """Saves the generated ad copy examples to a file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"""--- Ad Copy Examples Generated on {timestamp} ---
This file contains simulated ad copy.
It includes placeholders for where real API calls to Google Ads would occur.
Compliance checks (disclosures, restricted keywords) are simulated based on config.
"""
    header += "=" * 50 + "\n\n"

    try:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(header)
            if ad_data.get("error"):
                f.write(f"Error: {ad_data['error']}\n")
                return

            for i, ad_group in enumerate(ad_data.get("ads", [])):
                f.write(f"**Ad Example {i+1}**\n")
                f.write(f"  Campaign Name (Simulated): {ad_group['campaign_name']}\n")
                f.write(f"  Ad Group (Simulated): {ad_group['ad_group']}\n")
                f.write(f"  Headlines:\n")
                for h in ad_group['headlines']:
                    f.write(f"    - {h}\n")
                f.write(f"  Descriptions:\n")
                for d in ad_group['descriptions']:
                    f.write(f"    - {d}\n")
                f.write(f"  Final URL (Placeholder): {ad_group['final_url_placeholder']}\n")
                f.write(f"  Display URL (Simulated): {ad_group['display_url']}\n")
                f.write(f"  Notes: {ad_group['notes']}\n\n")

            f.write("\n--- Google Ads API Call Simulation ---\n")
            f.write(ad_data.get("api_simulation", "No API simulation block generated."))
            f.write("\n" + "=" * 50 + "\n")

        print(f"Successfully saved ad copy examples to {OUTPUT_FILE}")
    except IOError as e:
        print(f"Error saving ad copy examples to {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    # Ensure PyYAML is installed
    try:
        import yaml
    except ImportError:
        print("PyYAML not found. Attempting to install...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
            print("PyYAML installed successfully.")
            import yaml # Try importing again
        except subprocess.CalledProcessError as e:
            print(f"Failed to install PyYAML: {e}. Please install it manually.")
            sys.exit(1)
        except Exception as e: # General exception for import
            print(f"An error occurred during PyYAML import after installation: {e}")
            sys.exit(1)

    config_data = load_config()
    if not config_data:
        print("Could not load configuration. Exiting.")
    else:
        # Use a Bybit feature or a random idea for ad generation
        ideas = load_content_ideas()
        if ideas and random.choice([True, False]):
            selected_input = random.choice(ideas)
            print(f"Generating ad copy based on content idea: {selected_input}")
        else:
            selected_input = "Bybit's Advanced Charting Tools" # Default feature
            print(f"Generating ad copy based on Bybit feature: {selected_input}")

        ad_copy_data = generate_ad_copy(selected_input, config_data)
        save_ad_copy_examples(ad_copy_data)
main
