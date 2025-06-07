import yaml
import os
import random
from datetime import datetime

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
    except Exception as e:
        print(f"Error loading config {CONFIG_PATH}: {e}")
        return None

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
