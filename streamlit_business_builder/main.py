import streamlit as st
from openai import OpenAI
from datetime import datetime
from prompts import CLARITY_PROMPT, NICHE_PROMPT, ACTION_PROMPT, BUSINESS_STRATEGY_PROMPT
from translations import UI_TRANSLATIONS
from pdf_generator import create_pdf_report

# Initialize OpenAI client with DeepSeek configuration
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

# Agent-specific temperature settings
AGENT_TEMPERATURES = {
    "clarity": 0.7,    # More focused analysis, clear thinking
    "niche": 0.9,      # Balance between research and creative targeting
    "action": 1.0,     # Mix of practical steps and creative strategies
    "strategy": 0.8    # Balanced business planning and innovation
}

def get_agent_response(prompt, user_input, agent_type, lang_code="en"):
    st.write(f"🔄 {UI_TRANSLATIONS[lang_code]['processing']}")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=AGENT_TEMPERATURES[agent_type],
            stream=False
        )
        st.write(f"✅ {UI_TRANSLATIONS[lang_code]['success']}")
        return response.choices[0].message.content
    except Exception as e:
        st.write(f"❌ {UI_TRANSLATIONS[lang_code]['error_occurred']}: {str(e)}")
        raise e

def save_business_analysis(user_input, clarity_response, niche_response, action_response, final_response, language="en"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_base = f"business_analysis_{timestamp}"
    
    # Save TXT file
    txt_filename = f"{filename_base}.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write("=== Business Analysis ===\n\n")
        f.write(f"{UI_TRANSLATIONS[language]['business_idea_label']}\n")
        f.write(user_input + "\n\n")
        f.write(f"{UI_TRANSLATIONS[language]['clarity_analysis']}\n")
        f.write(clarity_response + "\n\n")
        f.write(f"{UI_TRANSLATIONS[language]['niche_strategy']}\n")
        f.write(niche_response + "\n\n")
        f.write(f"{UI_TRANSLATIONS[language]['action_plan']}\n")
        f.write(action_response + "\n\n")
        f.write(f"{UI_TRANSLATIONS[language]['business_strategy']}\n")
        f.write(final_response)
    
    # Generate PDF report
    pdf_filename = create_pdf_report(
        filename_base,
        user_input,
        clarity_response,
        niche_response,
        action_response,
        final_response,
        language
    )
    
    return txt_filename, pdf_filename

def run_business_builder(user_input, lang_code, txt_filename=None, pdf_filename=None):
    """
    Run the business builder analysis
    Args:
        user_input: The business idea text
        lang_code: Language code (en/nl)
        txt_filename: Optional custom filename for txt output
        pdf_filename: Optional custom filename for pdf output
    """
    st.write(f"\n🚀 {UI_TRANSLATIONS[lang_code]['processing']}")
    
    # Run Clarity Agent
    st.write(f"\n1️⃣ {UI_TRANSLATIONS[lang_code]['clarity_analysis']}...")
    clarity_response = get_agent_response(CLARITY_PROMPT, user_input, "clarity", lang_code)
    st.write(f"\n=== {UI_TRANSLATIONS[lang_code]['clarity_analysis']} ===")
    st.write(clarity_response)

    # Run Niche Agent
    st.write(f"\n2️⃣ {UI_TRANSLATIONS[lang_code]['niche_strategy']}...")
    niche_response = get_agent_response(
        NICHE_PROMPT, 
        f"{user_input}\n\n{UI_TRANSLATIONS[lang_code]['clarity_analysis']}: {clarity_response}", 
        "niche",
        lang_code
    )
    st.write(f"\n=== {UI_TRANSLATIONS[lang_code]['niche_strategy']} ===")
    st.write(niche_response)

    # Run Action Agent
    st.write(f"\n3️⃣ {UI_TRANSLATIONS[lang_code]['action_plan']}...")
    action_response = get_agent_response(
        ACTION_PROMPT, 
        f"{user_input}\n\n{UI_TRANSLATIONS[lang_code]['clarity_analysis']}: {clarity_response}\n{UI_TRANSLATIONS[lang_code]['niche_strategy']}: {niche_response}",
        "action",
        lang_code
    )
    st.write(f"\n=== {UI_TRANSLATIONS[lang_code]['action_plan']} ===")
    st.write(action_response)

    # Run Business Strategy Agent
    st.write(f"\n4️⃣ {UI_TRANSLATIONS[lang_code]['business_strategy']}...")
    final_response = get_agent_response(
        BUSINESS_STRATEGY_PROMPT, 
        f"{user_input}\n\n{UI_TRANSLATIONS[lang_code]['clarity_analysis']}: {clarity_response}\n{UI_TRANSLATIONS[lang_code]['niche_strategy']}: {niche_response}\n{UI_TRANSLATIONS[lang_code]['action_plan']}: {action_response}",
        "strategy",
        lang_code
    )
    st.write(f"\n=== {UI_TRANSLATIONS[lang_code]['business_strategy']} ===")
    st.write(final_response)
    
    # Save the analysis to files
    txt_filename, pdf_filename = save_business_analysis(
        user_input,
        clarity_response,
        niche_response,
        action_response,
        final_response,
        lang_code
    )
    
    return txt_filename, pdf_filename 