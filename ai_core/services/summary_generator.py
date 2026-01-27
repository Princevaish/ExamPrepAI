import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from fpdf import FPDF
from .llm_config import llm, llm2,llm3



# -------------------------------
#  1) EXPLANATION PROMPT
# -------------------------------

prompt_explanation = PromptTemplate(
    template=(
        "You are an expert educational assistant that provides accurate, detailed, and well-structured explanations.\n"
        "Write a comprehensive explanation on the following topic:\n\n"
        "Topic: {topic}\n\n"
        "Your explanation should include:\n"
        "1. An introduction to the topic.\n"
        "2. Key concepts and definitions.\n"
        "3. Important subtopics or components.\n"
        "4. Use cases or applications (if any).\n"
        "5. A conclusion summarizing the topic."
    ),
    input_variables=["topic"]
)

# -------------------------------
#  2) DYNAMIC SUMMARY PROMPT
# -------------------------------

prompt_summary = PromptTemplate(
    input_variables=["sum_content", "summary_type", "tone_style"],
    template=(
        "You are an expert summarization assistant specializing in PDF-ready document formatting.\n"
        "Your task is to create high-quality '{summary_type}' style notes.\n"
        "Tone/style required: {tone_style}\n\n"
        
        "Content to summarize:\n"
        "{sum_content}\n\n"
        
        "====================================================\n"
        "CRITICAL FORMATTING RULES (MUST FOLLOW EXACTLY)\n"
        "====================================================\n"
        "1. NO MARKDOWN SYMBOLS ALLOWED:\n"
        "   - NO underscores (_)\n"
        "   - NO asterisks (*)\n"
        "   - NO backticks\n"
        "   - NO hashtags (#)\n"
        "   - NO dashes for bullets\n\n"
        
        "2. SECTION HEADINGS FORMAT:\n"
        "   - Must be in ALL CAPS\n"
        "   - Must end with colon (:)\n"
        "   - Example: KEY CONCEPTS:\n\n"
        
        "3. SUBHEADINGS FORMAT:\n"
        "   - First letter capitalized\n"
        "   - Must end with colon (:)\n"
        "   - Example: Important Points:\n\n"
        
        "4. CONTENT FORMATTING:\n"
        "   - Use numbered lists: 1. 2. 3.\n"
        "   - Never use dashes (-) or asterisks (*)\n"
        "   - Keep lines short and scannable\n"
        "   - Use plain text only\n\n"
        
        "====================================================\n"
        "MANDATORY SECTION STRUCTURE (DO NOT CHANGE ORDER)\n"
        "====================================================\n"
        "You MUST include ALL of these sections in this exact order:\n\n"
        
        "KEY CONCEPTS:\n"
        "IMPORTANT SUBTOPICS:\n"
        "USE CASES:\n"
        "ADDITIONAL DETAILS:\n"
        "KEY TAKEAWAYS:\n\n"
        
        "====================================================\n"
        "SUMMARY TYPE SPECIFICATIONS\n"
        "====================================================\n"
        
        "SHORT SUMMARY:\n"
        "- 1-2 concise lines per section\n"
        "- Ultra-brief, essential information only\n"
        "- Numbered format: 1. 2. 3.\n\n"
        
        "BULLET POINTS:\n"
        "- 3-5 key points per section\n"
        "- Medium detail level\n"
        "- Numbered format: 1. 2. 3.\n"
        "- Each point should be 1 sentence\n\n"
        
        "DETAILED SUMMARY:\n"
        "- 5-8 comprehensive points per section\n"
        "- Full explanations with context\n"
        "- Numbered format: 1. 2. 3.\n"
        "- Each point can be 2-3 sentences\n"
        "- Still structured, NOT long paragraphs\n\n"
        
        "====================================================\n"
        "TONE STYLE GUIDELINES\n"
        "====================================================\n"
        
        "SIMPLE:\n"
        "- Clear, beginner-friendly language\n"
        "- Avoid jargon\n"
        "- Short sentences\n\n"
        
        "PROFESSIONAL:\n"
        "- Industry-standard terminology\n"
        "- Concise and confident\n"
        "- Business-appropriate\n\n"
        
        "ACADEMIC:\n"
        "- Formal, precise language\n"
        "- Neutral, objective tone\n"
        "- Technical accuracy\n\n"
        
        "====================================================\n"
        "CONTENT REQUIREMENTS\n"
        "====================================================\n"
        "1. Cover essential points: definitions, formulas, facts, components, steps, examples\n"
        "2. Present information in short, crisp lines ideal for quick revision\n"
        "3. Include code syntax references if relevant (Python/C++/Java) - use plain text format\n"
        "4. Every line must deliver value\n"
        "5. Maintain visual consistency across all sections\n\n"
        
        "====================================================\n"
        "QUALITY CHECKLIST (VERIFY BEFORE SUBMITTING)\n"
        "====================================================\n"
        "Before finishing, verify:\n"
        "- NO underscores, asterisks, or markdown symbols anywhere\n"
        "- All section headings are in ALL CAPS with colon\n"
        "- All content uses numbered format (1. 2. 3.)\n"
        "- Sections appear in the correct order\n"
        "- Content depth matches the selected summary type\n"
        "- Tone matches the selected style\n"
        "- Output is ready for direct PDF conversion\n\n"
        
        "Output format: Clean text notes ready for PDF. No extra headers or metadata.\n"
        "Begin the summary now.\n"
    ),
)

# -------------------------------
#  3) CHAINS
# -------------------------------
parser = StrOutputParser()
explanation_chain = prompt_explanation | llm | parser
summary_chain = prompt_summary | llm3 | parser

from io import BytesIO
from fpdf import FPDF
import re


def strip_markdown(text: str) -> str:
    """
    Remove all markdown symbols from text.
    """
    text = re.sub(r'^###\s*', '', text)
    text = re.sub(r'^##\s*', '', text)
    text = re.sub(r'^#\s*', '', text)
    text = text.replace('**', '')
    text = text.replace('__', '')
    text = text.replace('*', '')
    text = text.replace('_', '')
    return text.strip()


def sanitize_text(text: str) -> str:
    """
    Convert Unicode text to FPDF-safe latin-1.
    """
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\xa0": " ",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.encode("latin-1", "ignore").decode("latin-1")


class CustomPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.topic_title = ""
        self.first_page = True

    def header(self):
        if self.page_no() == 1 and self.first_page:
            self.set_fill_color(255, 153, 51)
            self.set_text_color(255, 255, 255)
            self.set_font("helvetica", "B", 11)
            self.cell(0, 12, "EXAMPREP DOST", ln=True, align="C", fill=True)
            self.ln(2)
            self.first_page = False
        elif self.page_no() > 1:
            self.set_font("helvetica", "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, sanitize_text(self.topic_title), ln=True, align="L")
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def draw_title_block(self, topic: str):
        self.set_font("helvetica", "B", 22)
        self.set_text_color(30, 30, 30)
        self.cell(0, 14, sanitize_text(topic.upper()), ln=True, align="C")
        
        self.set_font("helvetica", "", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Quick Revision Notes", ln=True, align="C")
        
        self.set_draw_color(255, 153, 51)
        self.set_line_width(0.6)
        self.line(50, self.get_y() + 2, 160, self.get_y() + 2)
        self.ln(10)

    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
        if style == 'F':
            op = 'f'
        elif style == 'FD' or style == 'DF':
            op = 'B'
        else:
            op = 'S'
        
        my_arc = 4/3 * (2**0.5 - 1)
        self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} m')
        
        xc = x + w - r
        yc = y + r
        self._out(f'{xc*k:.2f} {(hp-y)*k:.2f} l')
        self._arc(xc + r * my_arc, yc - r, xc + r, yc - r * my_arc, xc + r, yc)
        
        xc = x + w - r
        yc = y + h - r
        self._out(f'{(x+w)*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc + r, yc + r * my_arc, xc + r * my_arc, yc + r, xc, yc + r)
        
        xc = x + r
        yc = y + h - r
        self._out(f'{xc*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._arc(xc - r * my_arc, yc + r, xc - r, yc + r * my_arc, xc - r, yc)
        
        xc = x + r
        yc = y + r
        self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        self._arc(xc - r, yc - r * my_arc, xc - r * my_arc, yc - r, xc, yc - r)
        
        self._out(op)
    
    def _arc(self, x1, y1, x2, y2, x3, y3):
        h = self.h
        self._out(f'{x1*self.k:.2f} {(h-y1)*self.k:.2f} {x2*self.k:.2f} {(h-y2)*self.k:.2f} {x3*self.k:.2f} {(h-y3)*self.k:.2f} c')

    def draw_section_header(self, section_title: str):
        if self.get_y() > 250:
            self.add_page()
        
        self.ln(4)
        
        x = self.get_x()
        y = self.get_y()
        
        self.set_fill_color(255, 153, 51)
        self.rounded_rect(x, y, self.w - 2*x, 10, 2, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, sanitize_text(f"  {section_title}  "), ln=True, align="L")
        self.ln(3)

    def draw_subheading(self, subheading: str):
        self.ln(2)
        
        sanitized = sanitize_text(strip_markdown(subheading))
        self.set_font("helvetica", "B", 11)
        
        nb_lines = len(self.multi_cell(0, 8, f"  {sanitized}", split_only=True))
        cell_height = 8 * nb_lines
        
        x = self.get_x()
        y = self.get_y()
        
        self.set_fill_color(245, 245, 245)
        self.rounded_rect(x, y, self.w - 2*x, cell_height, 1.5, 'F')
        
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 8, f"  {sanitized}")
        self.ln(2)

    def write_content_line(self, text: str, indent: int = 0, is_numbered: bool = False):
        self.set_font("helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        
        clean_text = sanitize_text(strip_markdown(text))
        
        left_margin = 10 + indent
        self.set_left_margin(left_margin)
        self.multi_cell(0, 6, clean_text)
        self.set_left_margin(10)
        self.ln(0.5)


def generate_summary_pdf(summary_text: str, topic: str) -> bytes:
    try:
        pdf = CustomPDF()
        pdf.topic_title = topic
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        pdf.draw_title_block(topic)

        lines = summary_text.strip().split("\n")
        current_section = None
        point_counter = 0
        in_numbered_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            line_clean = strip_markdown(line)

            if line_clean.endswith(":") and len(line_clean) > 3:
                cleaned_title = line_clean[:-1].strip()
                
                if cleaned_title.replace(" ", "").isupper() and len(cleaned_title) > 8:
                    current_section = cleaned_title
                    pdf.draw_section_header(current_section)
                    point_counter = 0
                    
                    in_numbered_section = any(keyword in current_section.lower() for keyword in 
                        ["step", "stage", "phase", "process", "principle", "rule", "law", "type"])
                    continue
                
                elif cleaned_title[0].isupper():
                    pdf.draw_subheading(cleaned_title)
                    continue

            clean_line = line_clean.lstrip("-").lstrip("*").strip()
            if not clean_line:
                continue

            if clean_line[0].isdigit() and len(clean_line) > 2 and clean_line[1:3] in ['. ', ') ']:
                pdf.write_content_line(clean_line, indent=8, is_numbered=True)
                continue

            if in_numbered_section:
                point_counter += 1
                formatted_line = f"{point_counter}. {clean_line}"
                pdf.write_content_line(formatted_line, indent=8, is_numbered=True)
            else:
                if ":" in clean_line and clean_line.index(":") < 40:
                    pdf.write_content_line(f"• {clean_line}", indent=8)
                else:
                    pdf.write_content_line(f"• {clean_line}", indent=8)

        return pdf.output(dest="S").encode("latin-1")

    except Exception as e:
        print(f"[ERROR] Summary PDF generation failed: {e}")
        raise