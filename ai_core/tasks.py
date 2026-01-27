# ai_core/tasks.py

from celery import shared_task

# ============================
# MCQ TASK
# ============================
from .services.mcq_generator import generate_mcqs


@shared_task(bind=True)
def mcq_generation_task(self, topic: str, num_ques: int, difficulty: str):
    """
    Heavy MCQ generation using LLM
    Returns: List[Dict]
    """
    return generate_mcqs(topic, num_ques, difficulty)


# ============================
# TUTORIAL TASK (TEXT ONLY)
# ============================
from .services.tutorial_generator import tutorial_chain


@shared_task(bind=True)
def tutorial_generation_task(self, topic: str, depth: int):
    """
    Heavy tutorial text generation using LLM
    Returns: str
    """
    return tutorial_chain.invoke({
        "topic": topic,
        "depth": depth
    })


# ============================
# SUMMARY TASK (EXPLANATION + SUMMARY)
# ============================
from .services.summary_generator import explanation_chain, summary_chain


@shared_task(bind=True)
def summary_generation_task(
    self,
    topic: str,
    summary_type: str,
    tone_style: str
):
    """
    Heavy summary generation:
    1) Explanation
    2) Condensed summary
    Returns: str
    """
    explanation_text = explanation_chain.invoke({
        "topic": topic
    })

    summary_text = summary_chain.invoke({
        "sum_content": explanation_text,
        "summary_type": summary_type,
        "tone_style": tone_style
    })

    return summary_text


# ============================
# QUIZ TASK
# ============================
from .services.quiz_generator import generate_quiz


@shared_task(bind=True)
def quiz_generation_task(
    self,
    topic: str,
    num_questions: int,
    difficulty: str
):
    """
    Heavy quiz generation using LLM
    Returns: List[Dict]
    """
    return generate_quiz(topic, num_questions, difficulty)