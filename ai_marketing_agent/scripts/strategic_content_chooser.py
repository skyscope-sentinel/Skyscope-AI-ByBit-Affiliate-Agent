import os
import csv
import random

IDEAS_FILE = "ai_marketing_agent/generated_content/content_ideas.txt"
PERFORMANCE_DATA_FILE = "ai_marketing_agent/sim_data/simulated_performance_data.csv"
TRENDING_TOPICS_FILE = "ai_marketing_agent/sim_data/simulated_trending_topics.txt"
OUTPUT_CHOICE_FILE = "ai_marketing_agent/generated_content/next_article_to_generate.txt"

def load_ideas():
    try:
        with open(IDEAS_FILE, 'r') as f:
            # Filter out header, separator lines, and then strip leading "- "
            lines = [line.strip() for line in f.readlines() if line.strip()]
            if not lines: return []

            # Remove "Content Ideas Generated on..." header if present
            if "Content Ideas Generated on" in lines[0]:
                lines = lines[1:]
            # Remove separator lines like "==="
            lines = [line for line in lines if not all(c == '=' for c in line)]
            # Remove leading "- " from actual idea lines
            cleaned_ideas = []
            for line in lines:
                if line.startswith("- "):
                    cleaned_ideas.append(line[2:].strip())
                elif line: # Add non-empty lines that don't start with "- " directly (e.g. if format varies)
                    cleaned_ideas.append(line)
            return [idea for idea in cleaned_ideas if idea] # Final filter for any empty strings
    except FileNotFoundError:
        print(f"Warning: Ideas file not found at {IDEAS_FILE}")
        return []
    except Exception as e:
        print(f"Error loading ideas: {e}")
        return []

def load_performance_data():
    data = {}
    try:
        with open(PERFORMANCE_DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row['idea_title_exact_match']] = {
                    'views': int(row['sim_views']),
                    'ctr': float(row['sim_ctr']),
                    'conversions': int(row['sim_conversions'])
                }
    except FileNotFoundError:
        print(f"Warning: Performance data file not found at {PERFORMANCE_DATA_FILE}")
        # It's okay to return empty if no historical data, script should handle this
        return {}
    except Exception as e:
        print(f"Error loading performance data: {e}")
        return {}
    return data

def load_trending_topics():
    trends = {}
    try:
        with open(TRENDING_TOPICS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line: continue
                parts = line.split(',')
                if len(parts) == 2:
                    # Remove quotes from topic if they exist
                    topic = parts[0].strip().replace('"', '')
                    try:
                        score = int(parts[1].strip())
                        trends[topic] = score
                    except ValueError:
                        print(f"Warning: Could not parse trend score for: {line}")
                elif line: # Non-empty, non-comment line that doesn't fit format
                    print(f"Warning: Malformed line in trending topics: {line}")

    except FileNotFoundError:
        print(f"Warning: Trending topics file not found at {TRENDING_TOPICS_FILE}")
        # Okay to return empty if no trending data
        return {}
    except Exception as e:
        print(f"Error loading trending topics: {e}")
        return {}
    return trends

def choose_next_article(ideas, performance_data, trending_topics):
    if not ideas:
        return "Error: No content ideas available to choose from."

    scored_ideas = []
    for idea_text in ideas:
        score = 0
        # Performance boost: Lower past performance gets higher score (opportunity for improvement)
        perf = performance_data.get(idea_text)
        if perf:
            # Max possible conversions/views used for normalization (hypothetical)
            # Score higher for lower conversions (more room for growth)
            score += (30 - perf.get('conversions', 0)) * 0.5
            # Score higher for lower views (less saturated, more potential)
            score += (10000 - perf.get('views', 0)) / 2000.0
        else:
            # Idea has no performance data (new idea), give it a baseline score
            score += 15

        # Trend boost: Add score based on matching trending topics
        for topic, trend_score in trending_topics.items():
            if topic.lower() in idea_text.lower():
                score += trend_score * 2.5 # Weight trendiness

        # Random factor for variety / tie-breaking
        score += random.uniform(0, 8)
        scored_ideas.append((idea_text, round(score, 2)))

    # Sort by score in descending order
    scored_ideas.sort(key=lambda x: x[1], reverse=True)

    if scored_ideas:
        print(f"Top 3 Scored Ideas (Idea, Score): {scored_ideas[:3]}")
        return scored_ideas[0][0] # Return the text of the highest scored idea

    # Fallback if scoring somehow fails or list is empty after scoring (should not happen if ideas is not empty)
    print("Warning: No scored ideas, picking randomly from available ideas.")
    return random.choice(ideas)

if __name__ == "__main__":
    print("Running Strategic Content Chooser...")
    # Ensure generated_content directory exists for OUTPUT_CHOICE_FILE
    # os.path.dirname will return "ai_marketing_agent/generated_content"
    output_dir_for_choice = os.path.dirname(OUTPUT_CHOICE_FILE)
    if not os.path.exists(output_dir_for_choice):
        os.makedirs(output_dir_for_choice)
        print(f"Created directory: {output_dir_for_choice}")

    available_ideas = load_ideas()

    chosen_idea_to_write = ""

    if not available_ideas:
        print("No content ideas found. Please generate ideas first (e.g., run content_idea_generator.py).")
        chosen_idea_to_write = "Generated Default Idea: What is Bybit and How to Use It?"
        print(f"Using dummy idea for {OUTPUT_CHOICE_FILE} as no ideas were found.")
    else:
        print(f"Loaded {len(available_ideas)} ideas.")
        perf_data = load_performance_data()
        trends = load_trending_topics()

        print(f"Loaded {len(perf_data)} performance records.")
        print(f"Loaded {len(trends)} trending topics.")

        chosen_idea = choose_next_article(available_ideas, perf_data, trends)

        if "Error:" not in chosen_idea:
            chosen_idea_to_write = chosen_idea
            print(f"Strategic choice: '{chosen_idea_to_write}'")
        else:
            print(chosen_idea) # Print the error message
            chosen_idea_to_write = "Error in choosing idea. Fallback: General Bybit Overview"
            print(f"Using fallback idea: {chosen_idea_to_write}")

    try:
        with open(OUTPUT_CHOICE_FILE, 'w') as f:
            f.write(chosen_idea_to_write)
        print(f"Chosen idea saved to {OUTPUT_CHOICE_FILE}")
    except IOError as e:
        print(f"Error saving chosen idea to {OUTPUT_CHOICE_FILE}: {e}")
