import yaml
import os
from datetime import datetime

CONFIG_PATH = "ai_marketing_agent/config/settings.yaml"
OUTPUT_DIR = "ai_marketing_agent/generated_content"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "content_ideas.txt")

def load_config():
    """Loads the configuration from the YAML file."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        if not config:
            print(f"Error: Config file {CONFIG_PATH} is empty or malformed.")
            return None
        return config
    except FileNotFoundError:
        print(f"Error: Config file {CONFIG_PATH} not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML in {CONFIG_PATH}: {e}")
        return None

def generate_content_ideas(config):
    """Generates content ideas based on predefined topics and config keywords."""
    if not config or 'target_keywords' not in config:
        print("Error: Target keywords not found in config.")
        return []

    target_keywords = config.get('target_keywords', [])

    # Predefined list of crypto topics (simulating Google Trends or similar inspiration)
    simulated_trending_topics = [
        "Understanding Bitcoin Halving",
        "Ethereum's Next Upgrade",
        "Top Altcoins to Watch",
        "Beginner's Guide to Crypto Staking",
        "Latest Developments at Bybit",
        "Security Best Practices for Crypto Wallets",
        "Exploring DeFi Yield Farming",
        "NFTs and the Metaverse",
        "How to Analyze Crypto Market Trends",
        "Comparing Crypto Exchanges"
    ]

    content_ideas = []

    # Idea 1: Combine trending topics with "Bybit"
    for topic in simulated_trending_topics:
        if "Bybit" in topic:
            content_ideas.append(f"{topic}: A Deep Dive")
        else:
            content_ideas.append(f"{topic} (and How It Relates to Bybit Users)")

    # Idea 2: Create "How-To" guides using Bybit and target keywords
    how_to_starters = ["How to Get Started with", "A Beginner's Guide to", "Mastering"]
    for starter in how_to_starters:
        for keyword in target_keywords:
            if "Bybit" in keyword or "crypto" in keyword:
                 content_ideas.append(f"{starter} {keyword} on Bybit")

    # Idea 3: "Vs" posts
    competitors = ["Binance", "Kraken", "Coinbase"] # Common competitors
    for competitor in competitors:
        content_ideas.append(f"Bybit vs. {competitor}: Which is Right for You in {datetime.now().year}?")

    # Idea 4: Questions based on keywords
    for keyword in target_keywords:
        if keyword.startswith("Is") or keyword.startswith("What are") or keyword.startswith("How does"):
            content_ideas.append(f"Answering: {keyword}")
        elif "review" in keyword:
            content_ideas.append(f"An In-Depth {datetime.now().year} {keyword.capitalize()}")
        else:
            content_ideas.append(f"Exploring {keyword.capitalize()}: What You Need to Know")

    # Idea 5: Feature spotlights from Bybit (using a placeholder for actual features)
    # In a real scenario, this would come from kb_bybit_features.txt
    simulated_bybit_features = ["Spot Trading", "Derivatives", "Bybit Earn", "Trading Bots"]
    for feature in simulated_bybit_features:
        content_ideas.append(f"Unlocking the Power of Bybit's {feature} Tools")

    # Remove duplicates and limit number of ideas for this simulation
    unique_ideas = sorted(list(set(content_ideas)))
    return unique_ideas[:50] # Keep the list manageable

def save_content_ideas(ideas):
    """Saves the generated content ideas to a file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"Content Ideas Generated on {timestamp}\n"
    header += "=" * 30 + "\n\n"

    try:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(header)
            for idea in ideas:
                f.write(f"- {idea}\n")
        print(f"Successfully saved content ideas to {OUTPUT_FILE}")
    except IOError as e:
        print(f"Error saving content ideas to {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    config_data = load_config()
    if config_data:
        ideas = generate_content_ideas(config_data)
        if ideas:
            save_content_ideas(ideas)
        else:
            print("No content ideas were generated.")
    else:
        print("Could not load configuration. Exiting.")
