import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from fpdf import FPDF

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


# ===========================
#  LLM CONFIG
# ===========================
llm = ChatGroq(
    temperature=0.7,
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant"
)


# ===========================
#  JSON OUTPUT PARSER
# ===========================
parser = JsonOutputParser()

prompt_mcq = PromptTemplate(
    template="""
Generate exactly {num_ques} MCQs on the topic "{topic}" with difficulty "{difficulty}".

STRICT RULES:
1. You MUST output exactly {num_ques} MCQs — not less, not more.
2. Output MUST follow this JSON structure exactly:

{{
  "mcqs": [
    {{
      "question": "text?",
      "options": ["A ...", "B ...", "C ...", "D ..."],
      "answer": "A"
    }}
  ]
}}

3. Each question must have:
   - 1 clear question
   - Exactly 4 options labeled A, B, C, D
   - One correct answer ("A", "B", "C", or "D")

4. DO NOT include explanations.
5. DO NOT include any extra text outside JSON.
6. DO NOT add comments or markdown formatting.
7. The JSON must be valid, machine-readable, and must contain exactly {num_ques} items in the "mcqs" list.

If you do not follow the rules, the output will break.  
Return ONLY the final JSON.
""",
    input_variables=["topic", "num_ques", "difficulty"],
)



mcq_chain = prompt_mcq | llm | parser


# ===========================
# GENERATE MCQs
# ===========================
def generate_mcqs(topic: str, num_ques: int, difficulty: str):
    try:
        result = mcq_chain.invoke({
            "topic": topic,
            "num_ques": num_ques,
            "difficulty": difficulty
        })
        
        print(f"[DEBUG] LLM Response: {result}")  # Debug output
        
        # Handle both direct list and nested dict response
        if isinstance(result, dict) and "mcqs" in result:
            return result["mcqs"]
        elif isinstance(result, list):
            return result
        else:
            print(f"[ERROR] Unexpected response format: {type(result)}")
            return []
            
    except Exception as e:
        print(f"[ERROR] generate_mcqs failed: {str(e)}")
        return []




from fpdf import FPDF

def generate_styled_mcq_pdf(mcqs: list, title: str) -> bytes:
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"{title} - MCQs", ln=True, align="C")
        pdf.ln(8)

        # MCQs
        for idx, mcq in enumerate(mcqs, start=1):
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(0, 8, f"Q{idx}. {mcq['question']}")

            pdf.set_font("Helvetica", size=11)
            for opt in mcq["options"]:
                pdf.multi_cell(0, 7, f"  {opt}")
            pdf.ln(3)

        # Answer Key
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Answer Key", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Helvetica", size=12)
        for idx, mcq in enumerate(mcqs, start=1):
            pdf.multi_cell(0, 8, f"Q{idx}: {mcq['answer']}")

        # ✅ IN-MEMORY PDF (NO FILE SYSTEM)
        pdf_str = pdf.output(dest="S")
        return pdf_str.encode("latin-1")

    except Exception as e:
        print(f"[ERROR] PDF generation failed: {str(e)}")
        raise
