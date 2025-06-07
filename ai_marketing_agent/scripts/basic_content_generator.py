
import yaml
import os
import random
from datetime import datetime
import google.generativeai as genai
import re

CONFIG_PATH = "ai_marketing_agent/config/settings.yaml"
KB_DIR = "ai_marketing_agent/knowledge_base"
IDEAS_FILE = "ai_marketing_agent/generated_content/content_ideas.txt" # Fallback
NEXT_IDEA_FILE = "ai_marketing_agent/generated_content/next_article_to_generate.txt"
OUTPUT_DIR = "ai_marketing_agent/generated_content"

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f: config = yaml.safe_load(f)
        if not config: # Check if config is None or empty
            print(f"CRITICAL: Config file {CONFIG_PATH} is empty or malformed!")
            return None
        return config
    except FileNotFoundError:
        print(f"CRITICAL: Config file {CONFIG_PATH} not found!")
        return None
    except Exception as e:
        print(f"Error loading config {CONFIG_PATH}: {e}")
        return None

def load_knowledge_base_file(filename):
    filepath = os.path.join(KB_DIR, filename)
    try:
        with open(filepath, 'r') as f: return f.read()
    except FileNotFoundError:
        print(f"Warning: KB file {filepath} not found. Proceeding with empty content for this KB.")
        return "" # Return empty string if KB file not found, script can handle this
    except Exception as e:
        print(f"Error loading KB file {filepath}: {e}")
        return ""

def load_content_ideas(): # Fallback
    try:
        with open(IDEAS_FILE, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("=") and not "Content Ideas Generated on" in line]
            lines = [line for line in lines if line]
            return [line[2:] if line.startswith("- ") else line for line in lines if line.strip()]
    except FileNotFoundError: # Explicitly handle FileNotFoundError
        print(f"Warning: Fallback ideas file {IDEAS_FILE} not found.")
        return []
    except Exception as e:
        print(f"Error loading fallback ideas from {IDEAS_FILE}: {e}")
        return []

def load_next_idea():
    try:
        # Ensure directory for NEXT_IDEA_FILE exists before trying to read from it
        os.makedirs(os.path.dirname(NEXT_IDEA_FILE), exist_ok=True)
        if not os.path.exists(NEXT_IDEA_FILE):
             print(f"Info: Strategic choice file {NEXT_IDEA_FILE} not found. Will use fallback ideas list.")
             return None
        with open(NEXT_IDEA_FILE, 'r') as f:
            chosen_idea = f.read().strip()
            # Return None if file is empty, so fallback can be triggered
            return chosen_idea if chosen_idea else None
    except Exception as e:
        print(f"Error loading next idea from {NEXT_IDEA_FILE}: {e}")
        return None

def get_content_type(idea_text):
    if not idea_text: return "general_article" # Handle None or empty idea_text
    idea_lower = idea_text.lower()
    if "how to" in idea_lower or "guide" in idea_lower or "getting started" in idea_lower: return "how-to"
    if "vs" in idea_lower or "versus" in idea_lower or "compare" in idea_lower: return "comparison"
    if "what is" in idea_lower or "explaining" in idea_lower or "understanding" in idea_lower: return "explainer"
    if "review" in idea_lower: return "review"
    if "news" in idea_lower or "update" in idea_lower or "latest" in idea_lower: return "news_update"
    return "general_article"

def generate_llm_content(prompt_text, api_key):
    try:
        genai.configure(api_key=api_key)
        model_name = "gemini-1.0-pro"
        model = genai.GenerativeModel(model_name)
        print(f"\nAttempting LLM generation (model: {model_name})...")
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = model.generate_content(prompt_text, safety_settings=safety_settings)

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            return f"Error: Prompt blocked by API ({response.prompt_feedback.block_reason}). Review prompt or safety settings."
        if not response.candidates: # Check if candidates list is empty
             return f"Error: No candidates from LLM. Prompt may be too restrictive or issue with API. Response details: {response}"

        candidate = response.candidates[0]
        if candidate.finish_reason.name != "STOP":
             finish_reason_message = f"Warning: LLM generation finished with reason: {candidate.finish_reason.name}."
             if candidate.finish_reason.name == "SAFETY":
                  safety_info = " Safety details: "
                  if candidate.safety_ratings:
                      for rating in candidate.safety_ratings:
                          if rating.probability.name != "NEGLIGIBLE":
                              safety_info += f" {rating.category.name} - {rating.probability.name};"
                  return f"Error: Generation stopped by safety filter.{safety_info if safety_info != ' Safety details: ' else ''}"

             if candidate.content and candidate.content.parts:
                 print(finish_reason_message + " Partial content might be returned.")
                 return "".join(part.text for part in candidate.content.parts)
             return f"Error: Generation finished with reason '{candidate.finish_reason.name}' but no content. {finish_reason_message}"

        if candidate.content and candidate.content.parts:
            print("LLM content generated successfully.")
            return "".join(part.text for part in candidate.content.parts)

        return "Error: No valid content parts in LLM response despite 'STOP' reason."
    except Exception as e: # Catch more general exceptions from API call
        return f"Error during LLM call: {e}"

def construct_prompt_v3(idea, content_type, persona, config, kb_features_summary, kb_ethics_summary, kb_programs_summary):
    target_keywords_list = config.get('target_keywords', [])
    default_primary_keyword = random.choice(target_keywords_list) if target_keywords_list else "Bybit trading"

    if persona and persona.get('keywords'): # Check if persona and its keywords exist
        primary_keyword = random.choice(persona['keywords'])
    else:
        primary_keyword = default_primary_keyword

    affiliate_link = config.get('bybit_affiliate_link', 'YOUR_BYBIT_LINK')
    blog_disclosure = config.get('compliance', {}).get('disclosure_texts', {}).get('blog', '#Ad #BybitAffiliate')
    risk_disclaimer = config.get('compliance', {}).get('risk_disclaimer', 'Cryptocurrency investment is subject to high market risk.')

    persona_name = persona['name'] if persona else "General User"
    persona_desc = persona['description'] if persona else "A crypto enthusiast."
    persona_tone = persona['preferred_tone'] if persona and 'preferred_tone' in persona else "clear, informative, and engaging"

    prompt = f'''
You are an AI Marketing Assistant creating a blog post for Bybit, a cryptocurrency exchange.
Your target audience is '{persona_name}': {persona_desc}.
The tone of the article should be: {persona_tone}.

**Blog Post Title/Idea:** {idea}
**Content Type to Generate:** {content_type}
**Incorporate this Primary Keyword naturally:** {primary_keyword}

**Task:** Write a compelling and informative blog post of approximately 400-700 words. Use Markdown for formatting.

**Detailed Instructions based on Content Type '{content_type}':**
'''
    if content_type == "how-to":
        prompt += "- Provide clear, actionable, step-by-step instructions. Simplify complex steps for the target persona.\n"
        prompt += "- Focus on specific Bybit features or tools that make this 'how-to' easy or effective for the user.\n"
    elif content_type == "comparison":
        competitor_match = re.search(r"vs\.?\s*([\w\s]+)", idea, re.IGNORECASE)
        competitor_name = competitor_match.group(1).strip() if competitor_match else "another platform"
        prompt += f"- Objectively compare Bybit with '{competitor_name}' concerning aspects of '{idea}'.\n"
        prompt += f"- Highlight Bybit's advantages, tailoring points to what '{persona_name}' would value most.\n"
        prompt += f"- If specific, verifiable data for '{competitor_name}' isn't available, state this and focus on Bybit's offerings.\n"
    elif content_type == "explainer":
        prompt += f"- Explain the core concepts of '{idea}' in a way that is easily understandable for '{persona_name}'.\n"
        prompt += f"- Clearly connect the explanation to practical applications or benefits on the Bybit platform.\n"
    elif content_type == "review":
        prompt += f"- Write a balanced and honest review of the subject matter in '{idea}'.\n"
        prompt += f"- Discuss both pros and cons from the perspective of '{persona_name}'.\n"
    else: # general_article, news_update
        prompt += f"- Discuss the topic '{idea}' and its current relevance to '{persona_name}' in the crypto space.\n"
        prompt += f"- Naturally integrate Bybit's role, related platform features, or services where appropriate.\n"

    prompt += f'''
**Knowledge Base Context (Summaries - use these to inform your writing):**
*   Key Bybit Features (for reference): ...{kb_features_summary}...
*   Ethical Marketing Rules (Strictly Follow): ...{kb_ethics_summary}... (Crucial: No profit guarantees, be truthful, avoid hype)
*   Bybit Programs Overview (for background context): ...{kb_programs_summary}...

**Mandatory Compliance Requirements:**
1.  **Disclosure First:** The VERY FIRST line of the blog post MUST be: {blog_disclosure}
2.  **Risk Disclaimer Last:** The VERY LAST line of the blog post MUST be: {risk_disclaimer}
3.  **Call to Action:** Before the final risk disclaimer, include a relevant call to action. Examples: "Explore these features on Bybit: {affiliate_link}", "Ready to get started? Sign up at Bybit: {affiliate_link}"

Output ONLY the Markdown content for the blog post. Do not add any other text, commentary, or preambles before or after the Markdown content.
'''
    return prompt

def save_generated_content(idea, content_type, persona_name, content_body):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    persona_tag = persona_name.replace(" ", "_").lower() if persona_name else "general"
    sanitized_idea = re.sub(r'[^a-zA-Z0-9_\-]', '_', idea[:30])
    filename = f"llm_draft_{content_type}_{persona_tag}_{sanitized_idea}_{timestamp}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    header = f"--- Generated Content (LLM) ---\n"
    header += f"Type: {content_type.capitalize()}\n"
    header += f"Idea: {idea}\n"
    header += f"Persona: {persona_name if persona_name else 'N/A'}\n"
    header += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"--- \n\n"

    try:
        with open(filepath, 'w') as f: f.write(header + content_body)
        print(f"Successfully saved LLM-generated content to {filepath}")
    except IOError as e: print(f"Error saving content to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting Enhanced LLM Content Generator (V3 - With Personas & Strategy Input)...")
    config_data = load_config()
    if not config_data:
        print("Exiting due to config load failure.")
        exit(1)

    gemini_api_key_name = config_data.get('gemini_api_key_env_var', "GEMINI_API_KEY")
    api_key = os.environ.get(gemini_api_key_name)

    if not api_key:
        print(f"Error: API Key '{gemini_api_key_name}' not found in environment variables.")
        print(f"Please run 'python ai_marketing_agent/scripts/setup_env.py' or set the variable manually.")
    else:
        print(f"API Key '{gemini_api_key_name}' found in environment.")

        selected_idea = load_next_idea()
        if not selected_idea or "Error:" in selected_idea:
            print(f"No valid strategic idea from '{NEXT_IDEA_FILE}' (Content: '{selected_idea}'). Choosing randomly from general ideas list.")
            content_ideas = load_content_ideas()
            if not content_ideas:
                print("No content ideas available at all (from content_ideas.txt). Exiting.");
                exit(1)
            selected_idea = random.choice(content_ideas)
            if not selected_idea:
                 print("CRITICAL: No idea could be selected even from fallback. Exiting."); exit(1)

        content_type = get_content_type(selected_idea)

        personas = config_data.get('audience_personas', {})
        chosen_persona_key = random.choice(list(personas.keys())) if personas else None
        chosen_persona = personas.get(chosen_persona_key) if chosen_persona_key else None
        persona_name_for_log = chosen_persona['name'] if chosen_persona else "General"

        print(f"Selected idea: '{selected_idea}' (Type: {content_type}, Persona: {persona_name_for_log})")

        kb_features_full = load_knowledge_base_file("kb_bybit_features.txt")
        kb_ethics_full = load_knowledge_base_file("kb_ethical_guidelines.txt")
        kb_programs_full = load_knowledge_base_file("kb_bybit_programs.txt")

        features_summary = "\n".join(kb_features_full.split('\n')[:20])
        ethics_summary = "\n".join(kb_ethics_full.split('\n')[:25])
        programs_summary = "\n".join(kb_programs_full.split('\n')[:15])

        prompt = construct_prompt_v3(selected_idea, content_type, chosen_persona, config_data,
                                     features_summary, ethics_summary, programs_summary)

        # print(f"\nDEBUG PROMPT V3 (first 1000 chars):\n{prompt[:1000]}...\n")

        generated_text_raw = generate_llm_content(prompt, api_key)

        if "Error:" not in generated_text_raw:
            final_text = generated_text_raw.strip()

            blog_disclosure = config_data.get('compliance', {}).get('disclosure_texts', {}).get('blog', '#Ad')
            risk_disclaimer = config_data.get('compliance', {}).get('risk_disclaimer', 'Trade crypto responsibly.')

            current_first_line = final_text.split('\n')[0].strip()
            if not current_first_line.startswith(blog_disclosure):
                print(f"Warning: Disclosure '{blog_disclosure}' not at the very start. Prepending.")
                final_text = re.sub(r"^(#Ad|#BybitAffiliate|Disclosure:.*?)\s*\n*", "", final_text, flags=re.IGNORECASE | re.MULTILINE).strip()
                final_text = f"{blog_disclosure}\n\n{final_text}"

            if not final_text.strip().endswith(risk_disclaimer):
                 print(f"Warning: Risk disclaimer '{risk_disclaimer}' not at the very end. Appending.")
                 final_text = final_text.strip()
                 if final_text.endswith("---"): final_text = final_text[:-3].strip()
                 final_text = f"{final_text}\n\n---\n{risk_disclaimer}"

            save_generated_content(selected_idea, content_type, persona_name_for_log, final_text)
        else:
            print(f"Content generation failed. LLM Output/Error: {generated_text_raw}")
            debug_filename = f"failed_prompt_and_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            debug_filepath = os.path.join(OUTPUT_DIR, debug_filename)
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            try:
                with open(debug_filepath, 'w') as df:
                    df.write("--- FAILED PROMPT ---\n")
                    df.write(prompt)
                    df.write("\n\n--- LLM ERROR/OUTPUT ---\n")
                    df.write(generated_text_raw)
                print(f"Saved failed prompt and error to {debug_filepath}")
            except Exception as e_debug:
                print(f"Error saving debug file: {e_debug}")

    print("\nEnhanced Content Generator script (V3 with personas) finished.")
