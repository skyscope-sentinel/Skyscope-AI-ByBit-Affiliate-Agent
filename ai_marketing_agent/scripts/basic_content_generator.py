import yaml
import os
import random
from datetime import datetime

CONFIG_PATH = "ai_marketing_agent/config/settings.yaml"
KB_DIR = "ai_marketing_agent/knowledge_base"
IDEAS_FILE = "ai_marketing_agent/generated_content/content_ideas.txt"
OUTPUT_DIR = "ai_marketing_agent/generated_content"

def load_config():
    """Loads the configuration from the YAML file."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config {CONFIG_PATH}: {e}")
        return None

def load_knowledge_base_file(filename):
    """Loads a specific file from the knowledge base directory."""
    filepath = os.path.join(KB_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading knowledge base file {filepath}: {e}")
        return ""

def load_content_ideas():
    """Loads content ideas from the ideas file."""
    try:
        with open(IDEAS_FILE, 'r') as f:
            # Skip header lines
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("=")]
            if len(lines) > 1: # Check if there are ideas after header
                 # Remove potential header like "Content Ideas Generated on..."
                if "Content Ideas Generated on" in lines[0]:
                    lines = lines[1:]
                # Remove lines that are just separators like "==="
                lines = [line for line in lines if not all(c == '=' for c in line)]
                 # Remove empty lines again after filtering
                lines = [line for line in lines if line.strip()]
                # Remove the leading "- " from ideas
                return [line[2:] if line.startswith("- ") else line for line in lines if line.strip()]
        return []
    except Exception as e:
        print(f"Error loading content ideas from {IDEAS_FILE}: {e}")
        return []

def generate_blog_post_draft(idea, config, kb_features, kb_ethics):
    """Generates a simulated blog post draft using templates."""
    if not config:
        return "Error: Config not loaded."

    affiliate_link = config.get('bybit_affiliate_link', '[YOUR_AFFILIATE_LINK]')
    author = config.get('default_author', 'Bybit Enthusiast')
    disclosure = config.get('compliance', {}).get('disclosure_texts', {}).get('blog', '#Ad')
    risk_disclaimer = config.get('compliance', {}).get('risk_disclaimer', 'Trade responsibly.')

    # Simulate using a couple of features
    feature_lines = kb_features.split('\n')
    # Ensure k is not greater than the population size for random.sample
    valid_feature_lines = [line for line in feature_lines if line.strip() and not line.startswith("##")]
    sample_k = min(2, len(valid_feature_lines))
    simulated_feature_discussion = "\n".join(random.sample(valid_feature_lines, k=sample_k)) if valid_feature_lines else "No features available to discuss."

    draft = f"""---
Title: {idea}
Author: {author}
Date: {datetime.now().strftime('%Y-%m-%d')}
Tags: Bybit, Crypto, Trading, {random.choice(config.get('target_keywords', ['exchange']))}
---

{disclosure}

## Introduction

Welcome to our deep dive into '{idea}'. In the ever-evolving world of cryptocurrency, staying informed is key.
This post aims to provide valuable insights for both beginners and experienced traders looking to leverage the Bybit platform.

## Understanding the Core Concept

[This section would typically elaborate on the main topic of '{idea}'. For this simulation, we're keeping it brief.
The AI would use its knowledge base and the specific idea to generate several paragraphs here.]

## Leveraging Bybit for '{idea}'

Bybit offers a robust suite of tools and features that can help you navigate the complexities of the crypto market.
Here are a couple of relevant aspects:

{simulated_feature_discussion}

By exploring these features, users can enhance their trading strategies and potentially make more informed decisions.
Remember to always do your own research (DYOR).

## Getting Started with Bybit

Ready to explore what Bybit has to offer? You can sign up using our affiliate link: {affiliate_link}
This helps support our content creation efforts at no extra cost to you!

## Important Considerations & Risks

[This section would discuss specific risks related to the content idea. The AI would pull from its ethical guidelines.]

{kb_ethics[:300]}... (summary of ethical guidelines)

**Disclaimer:** {risk_disclaimer} All trading involves risk. Only invest what you can afford to lose.
This content is for informational purposes only and should not be considered financial advice.

---
"""
    return draft

def generate_social_media_posts(idea, config):
    """Generates simulated social media posts using templates."""
    if not config:
        return "Error: Config not loaded."

    affiliate_link = config.get('bybit_affiliate_link', '[YOUR_AFFILIATE_LINK]')
    disclosure = config.get('compliance', {}).get('disclosure_texts', {}).get('default', '#Ad')

    posts = []
    posts.append(f"**Twitter Post:**\nThinking about '{idea}'? Learn how Bybit can help! {affiliate_link} {disclosure} #Bybit #Crypto")
    posts.append(f"**Facebook Post:**\n'{idea}' - A hot topic in crypto right now! We explore what this means for traders and how Bybit's platform provides the tools you need. Check it out: {affiliate_link} {disclosure}\n#BybitTrading #CryptoNews")
    posts.append(f"**LinkedIn Post:**\nAn analysis of '{idea}' and its implications for the digital asset space. Bybit offers professional-grade tools for navigating these markets. More info: {affiliate_link} {disclosure} #Cryptocurrency #DigitalAssets #BybitPro")

    return "\n\n".join(posts)

def save_generated_content(content_type, idea, content_body):
    """Saves the generated content to a timestamped file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize idea for filename
    safe_idea_part = "".join(c if c.isalnum() else "_" for c in idea[:30])
    filename = f"draft_{content_type}_{safe_idea_part}_{timestamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    header = f"""--- Generated Content ---
Type: {content_type.capitalize()}
Idea: {idea}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

"""
    try:
        with open(filepath, 'w') as f:
            f.write(header)
            f.write(content_body)
        print(f"Successfully saved {content_type} content to {filepath}")
    except IOError as e:
        print(f"Error saving content to {filepath}: {e}")

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
        content_ideas = load_content_ideas()
        if not content_ideas:
            print("No content ideas found or error loading ideas. Exiting.")
        else:
            # For simulation, pick a random idea
            selected_idea = random.choice(content_ideas)
            print(f"Selected content idea: {selected_idea}")

            kb_features_content = load_knowledge_base_file("kb_bybit_features.txt")
            kb_ethics_content = load_knowledge_base_file("kb_ethical_guidelines.txt")

            # Decide randomly to generate a blog post or social media posts for this simulation
            if random.choice([True, False]):
                print("Generating simulated blog post draft...")
                blog_draft = generate_blog_post_draft(selected_idea, config_data, kb_features_content, kb_ethics_content)
                save_generated_content("blog_post", selected_idea, blog_draft)
            else:
                print("Generating simulated social media posts...")
                social_posts = generate_social_media_posts(selected_idea, config_data)
                save_generated_content("social_media", selected_idea, social_posts)
