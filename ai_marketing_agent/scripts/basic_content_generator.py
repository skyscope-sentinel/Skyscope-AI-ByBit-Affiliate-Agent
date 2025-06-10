
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
feat/ai-marketing-agent-foundation
CHECKLIST_FILE = os.path.join(KB_DIR, "kb_content_checklist.txt") # New
OUTPUT_DIR = "ai_marketing_agent/generated_content"

def load_config():
    '''Loads configuration from YAML file.'''
    try:
        with open(CONFIG_PATH, 'r') as f: config = yaml.safe_load(f)
        if not config:
=======
OUTPUT_DIR = "ai_marketing_agent/generated_content"

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f: config = yaml.safe_load(f)
        if not config: # Check if config is None or empty
main
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
feat/ai-marketing-agent-foundation
    '''Loads a specific knowledge base file.'''
=======
main
    filepath = os.path.join(KB_DIR, filename)
    try:
        with open(filepath, 'r') as f: return f.read()
    except FileNotFoundError:
feat/ai-marketing-agent-foundation
        print(f"Warning: KB file {filepath} not found.")
        return ""
=======
        print(f"Warning: KB file {filepath} not found. Proceeding with empty content for this KB.")
        return "" # Return empty string if KB file not found, script can handle this
main
    except Exception as e:
        print(f"Error loading KB file {filepath}: {e}")
        return ""

def load_content_ideas(): # Fallback
feat/ai-marketing-agent-foundation
    '''Loads content ideas from the general ideas file (fallback).'''
=======
main
    try:
        with open(IDEAS_FILE, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("=") and not "Content Ideas Generated on" in line]
            lines = [line for line in lines if line]
            return [line[2:] if line.startswith("- ") else line for line in lines if line.strip()]
feat/ai-marketing-agent-foundation
    except FileNotFoundError:
=======
    except FileNotFoundError: # Explicitly handle FileNotFoundError
main
        print(f"Warning: Fallback ideas file {IDEAS_FILE} not found.")
        return []
    except Exception as e:
        print(f"Error loading fallback ideas from {IDEAS_FILE}: {e}")
        return []

def load_next_idea():
feat/ai-marketing-agent-foundation
    '''Loads the strategically chosen next idea.'''
    try:
        os.makedirs(os.path.dirname(NEXT_IDEA_FILE), exist_ok=True)
        if not os.path.exists(NEXT_IDEA_FILE):
            print(f"Info: Strategic choice file {NEXT_IDEA_FILE} not found.")
            return None
        with open(NEXT_IDEA_FILE, 'r') as f:
            chosen_idea = f.read().strip()
=======
    try:
        # Ensure directory for NEXT_IDEA_FILE exists before trying to read from it
        os.makedirs(os.path.dirname(NEXT_IDEA_FILE), exist_ok=True)
        if not os.path.exists(NEXT_IDEA_FILE):
             print(f"Info: Strategic choice file {NEXT_IDEA_FILE} not found. Will use fallback ideas list.")
             return None
        with open(NEXT_IDEA_FILE, 'r') as f:
            chosen_idea = f.read().strip()
            # Return None if file is empty, so fallback can be triggered
main
            return chosen_idea if chosen_idea else None
    except Exception as e:
        print(f"Error loading next idea from {NEXT_IDEA_FILE}: {e}")
        return None

feat/ai-marketing-agent-foundation
def get_content_type(idea_text): # Kept from V3
    '''Determines content type from idea text.'''
    if not idea_text: return "general_article"
=======
def get_content_type(idea_text):
    if not idea_text: return "general_article" # Handle None or empty idea_text
main
    idea_lower = idea_text.lower()
    if "how to" in idea_lower or "guide" in idea_lower or "getting started" in idea_lower: return "how-to"
    if "vs" in idea_lower or "versus" in idea_lower or "compare" in idea_lower: return "comparison"
    if "what is" in idea_lower or "explaining" in idea_lower or "understanding" in idea_lower: return "explainer"
    if "review" in idea_lower: return "review"
    if "news" in idea_lower or "update" in idea_lower or "latest" in idea_lower: return "news_update"
    return "general_article"

feat/ai-marketing-agent-foundation
def generate_llm_content(prompt_text, api_key, content_description="content"):
    '''Generates content using LLM, includes basic error handling & safety checks.'''
=======
def generate_llm_content(prompt_text, api_key):
main
    try:
        genai.configure(api_key=api_key)
        model_name = "gemini-1.0-pro"
        model = genai.GenerativeModel(model_name)
feat/ai-marketing-agent-foundation
        print(f"\nAttempting LLM generation for {content_description} (model: {model_name})...")
=======
        print(f"\nAttempting LLM generation (model: {model_name})...")
main
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = model.generate_content(prompt_text, safety_settings=safety_settings)

        if response.prompt_feedback and response.prompt_feedback.block_reason:
feat/ai-marketing-agent-foundation
            return f"Error: Prompt for {content_description} blocked by API ({response.prompt_feedback.block_reason})."
        if not response.candidates:
             return f"Error: No candidates from LLM for {content_description}. Response: {response}"

        candidate = response.candidates[0]
        if candidate.finish_reason.name != "STOP":
             print(f"Warning: LLM generation for {content_description} finished with reason: {candidate.finish_reason.name}.")
=======
            return f"Error: Prompt blocked by API ({response.prompt_feedback.block_reason}). Review prompt or safety settings."
        if not response.candidates: # Check if candidates list is empty
             return f"Error: No candidates from LLM. Prompt may be too restrictive or issue with API. Response details: {response}"

        candidate = response.candidates[0]
        if candidate.finish_reason.name != "STOP":
             finish_reason_message = f"Warning: LLM generation finished with reason: {candidate.finish_reason.name}."
main
             if candidate.finish_reason.name == "SAFETY":
                  safety_info = " Safety details: "
                  if candidate.safety_ratings:
                      for rating in candidate.safety_ratings:
                          if rating.probability.name != "NEGLIGIBLE":
                              safety_info += f" {rating.category.name} - {rating.probability.name};"
feat/ai-marketing-agent-foundation
                  return f"Error: Generation of {content_description} stopped by safety filter.{safety_info if safety_info != ' Safety details: ' else ''}"

             if candidate.content and candidate.content.parts:
                 return "".join(part.text for part in candidate.content.parts)
             return f"Error: Generation of {content_description} finished with reason '{candidate.finish_reason.name}' but no content."

        if candidate.content and candidate.content.parts:
            print(f"LLM generation for {content_description} successful.")
            return "".join(part.text for part in candidate.content.parts)

        return f"Error: No valid content parts in LLM response for {content_description} despite 'STOP' reason."
    except Exception as e:
        return f"Error during LLM call for {content_description}: {e}"

def construct_blog_prompt_v4(idea, content_type, persona, config, kb_features_summary, kb_ethics_summary, kb_programs_summary):
    '''Constructs the prompt for blog post generation (V4).'''
    target_keywords_list = config.get('target_keywords', [])
    default_primary_keyword = random.choice(target_keywords_list) if target_keywords_list else "Bybit trading"
    primary_keyword = persona.get('keywords', [default_primary_keyword])[0] if persona and persona.get('keywords') else default_primary_keyword
=======
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
 main

    affiliate_link = config.get('bybit_affiliate_link', 'YOUR_BYBIT_LINK')
    blog_disclosure = config.get('compliance', {}).get('disclosure_texts', {}).get('blog', '#Ad #BybitAffiliate')
    risk_disclaimer = config.get('compliance', {}).get('risk_disclaimer', 'Cryptocurrency investment is subject to high market risk.')

    persona_name = persona['name'] if persona else "General User"
    persona_desc = persona['description'] if persona else "A crypto enthusiast."
feat/ai-marketing-agent-foundation
    persona_tone = persona.get('preferred_tone', "clear, informative, and engaging") if persona else "clear, informative, and engaging"
=======
    persona_tone = persona['preferred_tone'] if persona and 'preferred_tone' in persona else "clear, informative, and engaging"
main

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
feat/ai-marketing-agent-foundation
        competitor_match = re.search(r"vs\.?.\s*([\w\s]+)", idea, re.IGNORECASE) # Escaped dot for regex
        competitor_name = competitor_match.group(1).strip() if competitor_match else "another platform"
        prompt += f"- Objectively compare Bybit with '{competitor_name}' concerning aspects of '{idea}'.\n"
        prompt += f"- Highlight Bybit's advantages, tailoring points to what '{persona_name}' would value most.\n"
        prompt += f"- If specific data for '{competitor_name}' isn't available, state this. Focus on Bybit's offerings.\n"
    elif content_type == "explainer":
        prompt += f"- Explain '{idea}' clearly, using analogies if helpful for '{persona_name}'.\n"
        prompt += f"- Connect the explanation to practical uses on Bybit.\n"
    else:
=======
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
main
        prompt += f"- Discuss the topic '{idea}' and its current relevance to '{persona_name}' in the crypto space.\n"
        prompt += f"- Naturally integrate Bybit's role, related platform features, or services where appropriate.\n"

    prompt += f'''
**Knowledge Base Context (Summaries - use these to inform your writing):**
*   Key Bybit Features (for reference): ...{kb_features_summary}...
feat/ai-marketing-agent-foundation
*   Ethical Marketing Rules (Strictly Follow): ...{kb_ethics_summary}... (No profit guarantees, be truthful)
*   Bybit Programs Overview (background context): ...{kb_programs_summary}...
=======
*   Ethical Marketing Rules (Strictly Follow): ...{kb_ethics_summary}... (Crucial: No profit guarantees, be truthful, avoid hype)
*   Bybit Programs Overview (for background context): ...{kb_programs_summary}...
main

**Mandatory Compliance Requirements:**
1.  **Disclosure First:** The VERY FIRST line of the blog post MUST be: {blog_disclosure}
2.  **Risk Disclaimer Last:** The VERY LAST line of the blog post MUST be: {risk_disclaimer}
feat/ai-marketing-agent-foundation
3.  **Call to Action:** Before the final risk disclaimer, include a relevant call to action. E.g., "Explore Bybit: {affiliate_link}"

Output ONLY the Markdown content for the blog post. Do not add any other text, commentary, or preambles.
'''
    return prompt

def construct_social_media_prompt_v1(blog_post_summary, idea, persona, config):
    '''Constructs a prompt for generating related social media snippets.'''
    affiliate_link = config.get('bybit_affiliate_link', 'YOUR_BYBIT_LINK')
    social_disclosure = config.get('compliance', {}).get('disclosure_texts', {}).get('social', '#Ad')

    persona_name = persona['name'] if persona else "crypto enthusiasts"
    persona_tone = persona.get('preferred_tone', "engaging and concise") if persona else "engaging and concise"

    prompt = f'''
You are an AI Social Media Marketer for Bybit.
Based on the following blog post idea and summary, generate 2-3 distinct social media posts (e.g., for Twitter/X).

**Original Blog Post Idea:** {idea}
**Summary of Blog Post Content (or Key Takeaways):**
{blog_post_summary[:1000]} ...

**Target Audience:** {persona_name}
**Desired Tone:** {persona_tone}

**Requirements for Social Media Posts:**
1.  Each post should be short and engaging (e.g., Twitter: under 280 characters).
2.  Include relevant hashtags (e.g., #Bybit, #Crypto, #{idea.split(" ")[0].capitalize()}).
3.  Include the link: {affiliate_link}
4.  Include disclosure: {social_disclosure}
5.  Encourage clicks/engagement.
6.  Do NOT use prohibited phrases like 'guaranteed profit'.

**Output Format:**
Provide each social media post clearly separated, for example:
Tweet 1: [Text of tweet 1]
Tweet 2: [Text of tweet 2]
Tweet 3: [Text of tweet 3]

Start directly with "Tweet 1:". Do not add any other preamble.
'''
    return prompt

def simulate_content_review(generated_content, content_type, checklist_text):
    '''Simulates a review against the content checklist.'''
    print(f"\n--- Simulating Content Review for {content_type} ---")
    if not checklist_text:
        print("Content checklist not found. Skipping simulated review.")
        return

    checklist_items = [line.strip() for line in checklist_text.split('\n') if line.strip().startswith("-")]
    if not checklist_items:
        print("No actionable items found in checklist. Skipping review.")
        return

    num_items_to_check = min(len(checklist_items), random.randint(2,3)) # Check 2 or 3 items
    items_to_show = random.sample(checklist_items, num_items_to_check)

    print("Checking against selected items from kb_content_checklist.txt:")
    needs_attention_count = 0
    for item in items_to_show:
        is_ok = random.choice([True, True, False])
        print(f"  {item} ... {'OK' if is_ok else 'NEEDS ATTENTION (Simulated)'}")
        if not is_ok: needs_attention_count +=1

    if needs_attention_count > 0:
         print(f"Simulated review: {needs_attention_count} item(s) might need attention.")
    else:
         print("Simulated review passed for selected items.")
    print("--- End of Simulated Review ---")

def save_generated_content(idea, content_type_tag, persona_name, content_body, is_social=False):
    '''Saves the generated content to a timestamped file.'''
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    persona_tag = persona_name.replace(" ", "_").lower() if persona_name else "general"
    sanitized_idea = re.sub(r'[^a-zA-Z0-9_\-]', '_', idea[:20])

    file_prefix = "llm_draft_social_" if is_social else f"llm_draft_{content_type_tag}_"
    file_extension = ".txt" if is_social else ".md"
    filename = f"{file_prefix}{persona_tag}_{sanitized_idea}_{timestamp}{file_extension}"
    filepath = os.path.join(OUTPUT_DIR, filename)

    content_desc = "Social Media Snippets" if is_social else f"{content_type_tag.capitalize()} Blog Post"

    header = f"--- Generated Content (LLM) ---\n"
    header += f"Type: {content_desc}\n"
    header += f"Original Idea: {idea}\n"
=======
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
main
    header += f"Persona: {persona_name if persona_name else 'N/A'}\n"
    header += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"--- \n\n"

    try:
        with open(filepath, 'w') as f: f.write(header + content_body)
feat/ai-marketing-agent-foundation
        print(f"Successfully saved LLM-generated {content_desc.lower()} to {filepath}")
    except IOError as e: print(f"Error saving {content_desc.lower()} to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting Enhanced LLM Content Generator (V4 - Multi-Format & Review)...")
    config_data = load_config()
    if not config_data: exit(1)
=======
        print(f"Successfully saved LLM-generated content to {filepath}")
    except IOError as e: print(f"Error saving content to {filepath}: {e}")

if __name__ == "__main__":
    print("Starting Enhanced LLM Content Generator (V3 - With Personas & Strategy Input)...")
    config_data = load_config()
    if not config_data:
        print("Exiting due to config load failure.")
        exit(1)
main

    gemini_api_key_name = config_data.get('gemini_api_key_env_var', "GEMINI_API_KEY")
    api_key = os.environ.get(gemini_api_key_name)

    if not api_key:
feat/ai-marketing-agent-foundation
        print(f"Error: API Key '{gemini_api_key_name}' not found. Run setup_env.py or set manually.")
    else:
        print(f"API Key '{gemini_api_key_name}' found.")
        selected_idea = load_next_idea()
        if not selected_idea or "Error:" in selected_idea:
            print(f"No valid strategic idea found (Content: '{selected_idea}'). Choosing randomly.")
            content_ideas = load_content_ideas()
            if not content_ideas: print("No content ideas available. Exiting."); exit(1)
            selected_idea = random.choice(content_ideas)
            if not selected_idea: print("CRITICAL: No idea selected. Exiting."); exit(1)

        blog_content_type = get_content_type(selected_idea)
=======
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
main

        personas = config_data.get('audience_personas', {})
        chosen_persona_key = random.choice(list(personas.keys())) if personas else None
        chosen_persona = personas.get(chosen_persona_key) if chosen_persona_key else None
        persona_name_for_log = chosen_persona['name'] if chosen_persona else "General"

feat/ai-marketing-agent-foundation
        print(f"Selected idea: '{selected_idea}' (Blog Type: {blog_content_type}, Persona: {persona_name_for_log})")
=======
        print(f"Selected idea: '{selected_idea}' (Type: {content_type}, Persona: {persona_name_for_log})")
main

        kb_features_full = load_knowledge_base_file("kb_bybit_features.txt")
        kb_ethics_full = load_knowledge_base_file("kb_ethical_guidelines.txt")
        kb_programs_full = load_knowledge_base_file("kb_bybit_programs.txt")
feat/ai-marketing-agent-foundation
        checklist_full_text = load_knowledge_base_file("kb_content_checklist.txt")
=======
main

        features_summary = "\n".join(kb_features_full.split('\n')[:20])
        ethics_summary = "\n".join(kb_ethics_full.split('\n')[:25])
        programs_summary = "\n".join(kb_programs_full.split('\n')[:15])

feat/ai-marketing-agent-foundation
        blog_prompt = construct_blog_prompt_v4(selected_idea, blog_content_type, chosen_persona, config_data,
                                             features_summary, ethics_summary, programs_summary)

        generated_blog_text_raw = generate_llm_content(blog_prompt, api_key, "blog post")

        if "Error:" not in generated_blog_text_raw:
            final_blog_text = generated_blog_text_raw.strip()
            blog_disclosure = config_data.get('compliance', {}).get('disclosure_texts', {}).get('blog', '#Ad')
            risk_disclaimer = config_data.get('compliance', {}).get('risk_disclaimer', 'Trade crypto responsibly.')

            if not final_blog_text.split('\n')[0].strip().startswith(blog_disclosure):
                final_blog_text = re.sub(r"^(#Ad|#BybitAffiliate|Disclosure:.*?)\s*\n*", "", final_blog_text, flags=re.IGNORECASE | re.MULTILINE).strip()
                final_blog_text = f"{blog_disclosure}\n\n{final_blog_text}"

            if not final_blog_text.strip().endswith(risk_disclaimer):
                 final_blog_text = re.sub(r"(\n*---\n*Cryptocurrency investment is subject to high market risk.*?|Trade crypto responsibly.*?)$", "", final_blog_text.strip(), flags=re.DOTALL | re.IGNORECASE)
                 final_blog_text = f"{final_blog_text.strip()}\n\n---\n{risk_disclaimer}"

            save_generated_content(selected_idea, blog_content_type, persona_name_for_log, final_blog_text, is_social=False)
            simulate_content_review(final_blog_text, blog_content_type, checklist_full_text)

            print(f"\nNow attempting to generate social media snippets for '{selected_idea}'...")
            social_prompt = construct_social_media_prompt_v1(final_blog_text, selected_idea, chosen_persona, config_data)
            generated_social_text_raw = generate_llm_content(social_prompt, api_key, "social media snippets")

            if "Error:" not in generated_social_text_raw:
                save_generated_content(selected_idea, "social_media", persona_name_for_log, generated_social_text_raw.strip(), is_social=True)
                simulate_content_review(generated_social_text_raw, "social_media", checklist_full_text)
            else:
                print(f"Social media snippet generation failed: {generated_social_text_raw}")
                debug_filename_social = f"failed_social_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                debug_filepath_social = os.path.join(OUTPUT_DIR, debug_filename_social)
                try:
                    with open(debug_filepath_social, 'w') as df:
                        df.write("--- FAILED SOCIAL MEDIA PROMPT ---\n"); df.write(social_prompt)
                        df.write("\n\n--- LLM ERROR/OUTPUT ---\n"); df.write(generated_social_text_raw)
                    print(f"Saved failed social prompt to {debug_filepath_social}")
                except Exception as e_debug_s: print(f"Error saving social debug file: {e_debug_s}")
        else:
            print(f"Blog content generation failed. LLM Output/Error: {generated_blog_text_raw}")
            debug_filename_blog = f"failed_blog_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            debug_filepath_blog = os.path.join(OUTPUT_DIR, debug_filename_blog)
            try:
                with open(debug_filepath_blog, 'w') as df:
                    df.write("--- FAILED BLOG PROMPT ---\n"); df.write(blog_prompt)
                    df.write("\n\n--- LLM ERROR/OUTPUT ---\n"); df.write(generated_blog_text_raw)
                print(f"Saved failed blog prompt to {debug_filepath_blog}")
            except Exception as e_debug_b: print(f"Error saving blog debug file: {e_debug_b}")

    print("\nEnhanced Content Generator script (V4 - Multi-Format) finished.")
=======
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
main
