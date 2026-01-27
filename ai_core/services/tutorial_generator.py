from datetime import datetime
from fpdf import FPDF
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .llm_config import llm
import re


prompt_tutorial = PromptTemplate(
    input_variables=["topic", "depth"],
    template=(
        "ROLE & CONTEXT\n"
        "You are a senior computer science professor, textbook author, and academic content architect.\n"
        "You specialize in writing LONG-FORM, EXAM-ORIENTED, PDF-READY tutorials used as\n"
        "chapter material in university textbooks and professional exam guides.\n\n"

        "Generate a COMPLETE, SELF-CONTAINED, and PAGE-CONTROLLED tutorial on:\n"
        "'{topic}'.\n\n"

        "====================================================\n"
        "STRICT PAGE LENGTH & CONTENT VOLUME CONTROL\n"
        "====================================================\n"
        "The selected depth level is = {depth}.\n\n"

        "You MUST meet the following MINIMUM LENGTH REQUIREMENTS:\n"
        "Depth 1 (Short Overview) → 2,200–2,800 words (≈ 5–7 A4 PDF pages)\n"
        "Depth 2 (Detailed Explanation) → 4,200–5,200 words (≈ 10–12 A4 PDF pages)\n"
        "Depth 3 (Full-Length Chapter) → 6,500–8,000+ words (≈ 15–20+ A4 PDF pages)\n\n"

        "HARD CONSTRAINTS:\n"
        "- Word count targets are MINIMUMS, not suggestions.\n"
        "- Do NOT compress explanations to save space.\n"
        "- Expand explanations using intuition, examples, edge cases, and comparisons.\n"
        "- NEVER summarize a concept in fewer than 2 paragraphs.\n"
        "- Be CODE-HEAVY with detailed line-by-line explanations.\n\n"

        "====================================================\n"
        "CRITICAL FORMATTING RULES (MUST FOLLOW)\n"
        "====================================================\n"
        "- NEVER use markdown headings (###, ##, #)\n"
        "- NEVER use bullet points with dashes (-)\n"
        "- Use ONLY:\n"
        "  1. Plain section titles ending with colon (:)\n"
        "  2. Numbered subdivisions (2.1, 2.2, 3.1, etc.)\n"
        "  3. Numbered lists (1., 2., 3.)\n"
        "  4. Clean paragraphs\n"
        "- All code MUST be inside triple backticks with language specified\n"
        "- Default programming language is C++\n\n"

        "====================================================\n"
        "SECTION-LEVEL EXPANSION RULES (MANDATORY)\n"
        "====================================================\n\n"

        "1. INTRODUCTION AND IMPORTANCE:\n"
        "- Minimum 5–7 full paragraphs\n"
        "- Include: definition, historical context, academic relevance, industry usage\n"
        "- Explain why this topic matters for exams and interviews\n\n"

        "2. CORE CONCEPTS AND THEORY:\n"
        "- 5–7 major subtopics (use numbering: 2.1, 2.2, 2.3, etc.)\n"
        "- EACH subtopic MUST contain:\n"
        "  - Formal definition (1 paragraph)\n"
        "  - Intuitive explanation (2 paragraphs)\n"
        "  - Step-by-step working explanation (2 paragraphs)\n"
        "  - Real-world analogy (1 paragraph)\n"
        "  - Code example in C++ with full walkthrough (3–4 paragraphs)\n"
        "  - Time and space complexity analysis\n"
        "  - Edge cases and common mistakes (1 paragraph)\n\n"

        "3. ADVANCED CONCEPTS AND OPTIMIZATIONS:\n"
        "- 3–5 advanced topics\n"
        "- EACH must include:\n"
        "  - Deep theoretical explanation (3 paragraphs)\n"
        "  - Performance and complexity discussion\n"
        "  - Optimized code with detailed explanation\n"
        "  - Real-world system-level usage\n\n"

        "4. PRACTICE QUESTIONS (MEDIUM LEVEL):\n"
        "- At least 5 questions\n"
        "- EACH question MUST include:\n"
        "  - Problem statement (2 paragraphs)\n"
        "  - Approach breakdown (2 paragraphs)\n"
        "  - Step-by-step solution walkthrough\n"
        "  - Complete C++ code with line-by-line explanation\n"
        "  - Complexity analysis\n\n"

        "5. ADVANCED PRACTICE QUESTIONS:\n"
        "- At least 5 questions\n"
        "- EACH must include:\n"
        "  - Detailed problem context\n"
        "  - Multiple approaches comparison\n"
        "  - Optimized final solution with full code\n"
        "  - Trade-offs and limitations discussion\n\n"

        "6. INTERVIEW QUESTIONS AND ANSWERS:\n"
        "- Depth 1 (Short Overview): EXACTLY 5 questions (Section title: TOP 5 INTERVIEW QUESTIONS AND ANSWERS)\n"
        "- Depth 2 (Detailed Explanation): EXACTLY 10 questions (Section title: TOP 10 INTERVIEW QUESTIONS AND ANSWERS)\n"
        "- Depth 3 (Full-Length Chapter): EXACTLY 20 questions (Section title: TOP 20 INTERVIEW QUESTIONS AND ANSWERS)\n"
        "- Format: Question 1:, Question 2:, etc. (NOT 6.1, 6.2)\n"
        "- EACH answer must be 150–250 words minimum\n"
        "- Include: conceptual explanation, code snippets where relevant, interview tips\n\n"

        "7. DIAGRAMS AND VISUAL EXPLANATIONS:\n"
        "- For concepts that benefit from visualization, describe the diagram in text format\n"
        "- Use ASCII art or textual representation where applicable\n"
        "- Example format:\n"
        "  Diagram Description:\n"
        "  [Describe what the diagram would show]\n"
        "  \n"
        "  ASCII Representation:\n"
        "  ```\n"
        "  [Simple ASCII art or text-based visualization]\n"
        "  ```\n"
        "- Each diagram description must be followed by a detailed textual explanation (2-3 paragraphs)\n\n"

        "8. KEY EXAM POINTS:\n"
        "- Highlight 8–10 critical exam concepts\n"
        "- Each with detailed explanation\n"
        "- Include formulas, theorems, and proofs where applicable\n\n"

        "9. SUMMARY AND NEXT STEPS:\n"
        "- Minimum 5–6 paragraphs\n"
        "- Include: comprehensive recap, best practices, common pitfalls\n"
        "- Learning roadmap and related topics\n"
        "- Interview preparation tips\n\n"

        "====================================================\n"
        "CODE REQUIREMENTS (CRITICAL)\n"
        "====================================================\n"
        "- Every major concept MUST have code examples\n"
        "- Code format:\n"
        "```cpp\n"
        "// Your code here\n"
        "```\n"
        "- After EVERY code block, provide:\n"
        "  1. Line-by-line explanation (2–3 paragraphs)\n"
        "  2. Time complexity analysis\n"
        "  3. Space complexity analysis\n"
        "  4. Optimization possibilities\n\n"

        "====================================================\n"
        "SELF-VERIFICATION (MANDATORY)\n"
        "====================================================\n"
        "Before finishing, internally verify:\n"
        "- NO markdown symbols (###, ##, #, -) anywhere\n"
        "- Interview questions count matches the depth level (5 for Depth 1, 10 for Depth 2, 20 for Depth 3)\n"
        "- Interview section title matches the count (TOP 5 / TOP 10 / TOP 20 INTERVIEW QUESTIONS AND ANSWERS)\n"
        "- Interview questions use format: Question 1:, Question 2:, etc.\n"
        "- Minimum word count for selected depth is satisfied\n"
        "- All sections are fully expanded with code examples\n"
        "- Every code block has detailed explanation\n"
        "- Diagrams are described in text format with ASCII representation where possible\n\n"

        "DO NOT mention word counts or verification steps in the final output.\n"
        "Begin the tutorial now.\n"
    )
)


parser = StrOutputParser()
tutorial_chain = prompt_tutorial | llm | parser


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


class TutorialPDF(FPDF):
    def __init__(self, title, author):
        super().__init__()
        self.title = title
        self.author = author
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
            self.cell(0, 8, sanitize_text(self.title), ln=True, align="L")
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

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

    def draw_title_block(self, topic: str):
        self.set_font("helvetica", "B", 22)
        self.set_text_color(30, 30, 30)
        self.cell(0, 14, sanitize_text(topic.upper()), ln=True, align="C")
        
        self.set_font("helvetica", "", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Complete Tutorial", ln=True, align="C")
        
        self.set_draw_color(255, 153, 51)
        self.set_line_width(0.6)
        self.line(50, self.get_y() + 2, 160, self.get_y() + 2)
        self.ln(8)
        
        self.set_font("helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"Author: {self.author} | Date: {datetime.now().strftime('%B %d, %Y')}", ln=True, align="C")
        self.ln(6)

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
        if self.get_y() > 260:
            self.add_page()
            
        self.ln(2)
        
        sanitized = sanitize_text(subheading)
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

    def exam_highlight_box(self, text: str):
        if self.get_y() > 250:
            self.add_page()
            
        self.ln(2)
        
        sanitized = sanitize_text(text)
        self.set_font("helvetica", "B", 10)
        
        nb_lines = len(self.multi_cell(0, 7, f"  EXAM POINT: {sanitized}", split_only=True))
        cell_height = 7 * nb_lines + 2
        
        x = self.get_x()
        y = self.get_y()
        
        self.set_fill_color(255, 245, 230)
        self.set_draw_color(255, 153, 51)
        self.set_line_width(0.5)
        self.rounded_rect(x, y, self.w - 2*x, cell_height, 2, 'FD')
        
        self.set_text_color(102, 51, 0)
        self.set_font("helvetica", "", 9)
        self.multi_cell(0, 7, f"  EXAM POINT: {sanitized}")
        self.ln(2)

    def code_block(self, code: str):
        if self.get_y() > 240:
            self.add_page()
            
        self.ln(2)
        self.set_font("Courier", "", 9)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(33, 37, 41)
        
        for line in code.strip().split("\n"):
            sanitized_line = sanitize_text(line)
            self.multi_cell(0, 5, f"  {sanitized_line}", border=0, fill=True)
        self.ln(2)

    def normal_text(self, text: str):
        clean_text = sanitize_text(strip_markdown(text).strip())
        if not clean_text:
            return
            
        self.set_font("helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, clean_text)
        self.ln(1)


def generate_tutorial_pdf(tutorial_text: str, topic: str, author: str = "ExamPrep AI") -> bytes:
    """
    Generate PDF from tutorial text with markdown formatting.
    
    Args:
        tutorial_text: The tutorial content in markdown format
        topic: PDF title
        author: Author name for metadata
        
    Returns:
        PDF file as bytes
    """
    try:
        pdf = TutorialPDF(title=topic.upper(), author=author)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        pdf.draw_title_block(topic)

        in_code_block = False
        code_buffer = []

        for line in tutorial_text.split("\n"):
            line_stripped = line.strip()
            
            if line_stripped.startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block and code_buffer:
                    pdf.code_block("\n".join(code_buffer))
                    code_buffer = []
                continue
            
            if in_code_block:
                code_buffer.append(line)
                continue
            
            if not line_stripped:
                continue
            
            if line_stripped.startswith("-----"):
                continue
            
            line_clean = strip_markdown(line_stripped)
            
            if line_clean.upper().startswith("EXAM POINT:") or line_clean.upper().startswith("KEY EXAM POINT:"):
                exam_text = re.sub(r'^(EXAM POINT:|KEY EXAM POINT:)\s*', '', line_clean, flags=re.IGNORECASE)
                pdf.exam_highlight_box(exam_text)
                continue
            
            if line_clean.endswith(":") and len(line_clean) > 3:
                title_text = line_clean[:-1].strip()
                
                if re.match(r'^Question\s+\d+$', title_text, re.IGNORECASE):
                    pdf.draw_subheading(title_text)
                    continue
                
                if title_text.replace(" ", "").isupper() and len(title_text) > 8:
                    pdf.draw_section_header(title_text)
                    continue
                
                if re.match(r'^\d+\.\d+\s+', title_text):
                    pdf.draw_subheading(title_text)
                    continue
                
                if title_text[0].isupper() and len(title_text) < 80:
                    pdf.draw_subheading(title_text)
                    continue
            
            clean_line = line_clean.lstrip("-").lstrip("*").strip()
            if not clean_line:
                continue
            
            if clean_line[0].isdigit() and len(clean_line) > 2 and clean_line[1:3] in ['. ', ') ']:
                pdf.normal_text(clean_line)
            else:
                pdf.normal_text(clean_line)
        
        return pdf.output(dest="S").encode("latin-1")
            
    except Exception as e:
        print(f"[ERROR] Tutorial PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise