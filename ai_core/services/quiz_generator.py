from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict
from .llm_config import llm,llm3
import re

# === Prompt Template ===
quiz_prompt_template = PromptTemplate(
    input_variables=["topic", "num_questions", "difficulty"],
    template="""
You are an expert technical quiz generator.

Generate a quiz of {num_questions} multiple-choice questions (MCQs) on the topic: "{topic}".

The difficulty level selected by the user is: {difficulty}.
Interpret it EXACTLY as:
easy → Easy (basic conceptual and beginner-friendly)
medium → Medium (interview-level conceptual + small logical reasoning)
hard → Hard (deep technical, multi-step reasoning, advanced interview level)

CRITICAL: Each question MUST include ALL THREE fields below in EXACTLY this format:

Q: <Question>
A. <Option A>
B. <Option B>
C. <Option C>
D. <Option D>
Answer: <Correct Option Letter>
Explanation: <Short, clear explanation of why this answer is correct>
Area of Improvement:
- Concept: <exact technical concept name>
- What to practice: <specific action or subtopic>


MANDATORY REQUIREMENTS FOR "Area of Improvement":
- MUST be specific to the question's topic
- MUST mention the exact concept/skill to practice
- Examples of GOOD Area of Improvement:
  * "Study list comprehensions in Python"
  * "Review the difference between JOIN types in SQL"
  * "Practice binary tree traversal algorithms"
  * "Understand the difference between var, let, and const in JavaScript"
  * "Review the OSI model layers"
  
- Examples of BAD Area of Improvement (DO NOT USE):
  * "Review the topic" ❌
  * "Study more" ❌
  * "Practice" ❌

Guidelines:
- Only ONE correct answer per question
- No numbering (NO Q1, Q2... only "Q:")
- Do NOT repeat questions
- Keep explanations concise but helpful
- EVERY question MUST have a specific "Area of Improvement"
- The quiz difficulty MUST strictly match the selected level

REMEMBER: The "Area of Improvement" field is MANDATORY and must be SPECIFIC, not generic!

ABSOLUTE RULE:
The "Area of Improvement" MUST be written in TWO bullet points:
1. Concept:
2. What to practice:

If you output a generic phrase like "review the topic", "study more", or similar,
the response will be considered INVALID.

"""
)

parser = StrOutputParser()
quiz_chain = quiz_prompt_template | llm | parser


# === Response Parser ===
def parse_quiz_response(response: str) -> List[Dict]:
    """Parse LLM response into structured quiz data"""
    quiz = []
    blocks = response.strip().split("Q:")
    
    for block_idx, block in enumerate(blocks[1:], 1):  # Skip first empty block
        try:
            lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
            if not lines:
                continue
                
            print(f"\n[PARSE BLOCK {block_idx}] Processing block with {len(lines)} lines")
            
            question = lines[0].strip()
            options = {}

            # Extract options A–D
            for line in lines[1:]:
                match = re.match(r"^([ABCD])[\.\):\s]+(.+)", line)
                if match:
                    key, val = match.groups()
                    options[key] = val.strip()

            answer = ""
            explanation = ""
            improvement = ""

            # More robust extraction using full text parsing
            full_text = "\n".join(lines)
            
            # Extract Answer
            answer_match = re.search(r"answer\s*[:.\-]?\s*([ABCD])", full_text, re.IGNORECASE)
            if answer_match:
                answer = answer_match.group(1).upper()
            
            # Extract Explanation (everything between "Explanation:" and "Area of Improvement:")
            explanation_match = re.search(
                r"explanation\s*[:.\-]?\s*(.+?)(?=area of improvement|$)",
                full_text,
                re.IGNORECASE | re.DOTALL
            )
            if explanation_match:
                explanation = explanation_match.group(1).strip()
                # Clean up any newlines
                explanation = " ".join(explanation.split())
            
            # Extract Area of Improvement (everything after "Area of Improvement:")
            improvement_match = re.search(
                r"area of improvement\s*[:.\-]?\s*(.+?)$",
                full_text,
                re.IGNORECASE | re.DOTALL
            )
            if improvement_match:
                improvement = improvement_match.group(1).strip()
                # Clean up any newlines
                improvement = " ".join(improvement.split())
                
                # FIXED: Only reject if the improvement is TOO GENERIC or TOO SHORT
                # Check if improvement is EXACTLY a generic phrase (not just containing the words)
                exact_generic_phrases = [
                    "review the topic",
                    "review the topic thoroughly",
                    "study more",
                    "practice more",
                    "read more",
                    "learn more",
                    "review this topic",
                    "study this topic",
                    "practice this"
                ]
                
                improvement_lower = improvement.lower().strip()
                
                # Reject if:
                # 1. It's exactly a generic phrase, OR
                # 2. It's too short (less than 15 characters), OR
                # 3. It's just "review" or "study" or "practice" alone
                is_too_generic = (
                    improvement_lower in exact_generic_phrases or
                    len(improvement) < 15 or
                    improvement_lower in ["review", "study", "practice", "learn", "read"]
                )
                
                if is_too_generic:
                    print(f"[WARNING] Generic/short improvement detected: '{improvement}'")
                    improvement = ""  # Reset to trigger fallback
                else:
                    print(f"[VALID] Accepted improvement: '{improvement}'")

            # Debug print
            print(f"[PARSE] Question: {question[:60]}...")
            print(f"[PARSE] Options: {list(options.keys())}")
            print(f"[PARSE] Answer: '{answer}'")
            print(f"[PARSE] Explanation: '{explanation[:80]}...'" if explanation else "[PARSE] Explanation: NOT FOUND")
            print(f"[PARSE] Improvement: '{improvement[:80]}...'" if improvement else "[PARSE] Improvement: NOT FOUND")

            # Generate fallback improvement based on question content if not found
            if not improvement:
                # Try to extract topic from question
                question_lower = question.lower()
                topic_lower = "{topic}".lower() if "{topic}" else ""
                
                if "python" in question_lower or "python" in topic_lower:
                    improvement = "Review Python fundamentals and syntax"
                elif "sql" in question_lower or "database" in question_lower:
                    improvement = "Study database concepts and SQL queries"
                elif "javascript" in question_lower or "js" in question_lower:
                    improvement = "Review JavaScript core concepts"
                elif "algorithm" in question_lower:
                    improvement = "Practice algorithm design and analysis"
                elif "data structure" in question_lower:
                    improvement = "Study data structures implementation"
                elif "network" in question_lower or "osi" in question_lower:
                    improvement = "Review networking fundamentals"
                elif "java" in question_lower:
                    improvement = "Study Java programming concepts"
                else:
                    # Last resort fallback
                    improvement = "Study the fundamental concepts related to this question"
                
                print(f"[FALLBACK] Generated improvement: '{improvement}'")

            # Only add if we have all required fields
            if question and len(options) == 4 and answer:
                quiz_item = {
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation if explanation else "The correct answer provides the most accurate solution.",
                    "improvement": improvement
                }
                quiz.append(quiz_item)
                print(f"[PARSE] ✓ Added question {block_idx}")
            else:
                print(f"[PARSE] ✗ Skipped question {block_idx} - Missing fields")

        except Exception as e:
            print(f"[ERROR] Failed to parse quiz block {block_idx}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    return quiz


# === Quiz Generator ===
def generate_quiz(topic: str, num_questions: int, difficulty: str) -> List[Dict]:
    """
    Generate quiz questions using LLM.
    
    Args:
        topic: Quiz topic
        num_questions: Number of questions
        difficulty: 'easy', 'medium', or 'hard'
    
    Returns:
        List of quiz question dictionaries
    """
    try:
        print(f"\n[QUIZ GEN] Starting quiz generation")
        print(f"[QUIZ GEN] Topic: {topic}")
        print(f"[QUIZ GEN] Questions: {num_questions}")
        print(f"[QUIZ GEN] Difficulty: {difficulty}")
        
        response = quiz_chain.invoke({
            "topic": topic,
            "num_questions": num_questions,
            "difficulty": difficulty
        })
        
        print(f"\n[QUIZ GEN] LLM response received - length: {len(response)} chars")
        print(f"[QUIZ GEN] First 1000 chars of response:\n{response[:1000]}\n")
        
        quiz = parse_quiz_response(response)
        print(f"\n[QUIZ GEN] ✓ Successfully parsed {len(quiz)} questions")
        
        # Print final structure
        for idx, q in enumerate(quiz, 1):
            print(f"\n[FINAL Q{idx}]")
            print(f"  - Question: {q['question'][:50]}...")
            print(f"  - Answer: {q['answer']}")
            print(f"  - Explanation: {q['explanation'][:50]}...")
            print(f"  - Improvement: {q['improvement']}")
        
        return quiz
        
    except Exception as e:
        print(f"\n[ERROR] Quiz generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return []