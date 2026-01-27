from django.shortcuts import render, HttpResponse
from ai_core.services.mcq_generator import generate_mcqs, generate_styled_mcq_pdf
from ai_core.services.summary_generator import explanation_chain, summary_chain, generate_summary_pdf
from ai_core.services.tutorial_generator import tutorial_chain, generate_tutorial_pdf
from ai_core.services.quiz_generator import generate_quiz
import json

from celery.result import AsyncResult
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

from ai_core.tasks import (
    mcq_generation_task,
    tutorial_generation_task,
    summary_generation_task,
    quiz_generation_task,
)



# ========================= MCQ VIEWS (UNCHANGED) =========================
def mcq_view(request):
    print("🔥 SYNC MCQ VIEW HIT")
    context = {}

    if request.method == "POST":
        print("[DEBUG] POST request received")
        
        topic = request.POST.get("topic", "").strip()
        count = request.POST.get("count", "").strip()
        difficulty = request.POST.get("difficulty", "medium")

        print(f"[DEBUG] Topic: {topic}, Count: {count}, Difficulty: {difficulty}")

        # Validation
        if not topic or not count:
            context["error"] = "Please enter topic and number of MCQs."
            return render(request, "mcq.html", context)

        try:
            count = int(count)
            if count <= 0 or count > 50:
                context["error"] = "Please enter a number between 1 and 50."
                return render(request, "mcq.html", context)
        except ValueError:
            context["error"] = "Invalid number format."
            return render(request, "mcq.html", context)

        # Generate MCQs
        try:
            result = generate_mcqs(topic, count, difficulty)
            print(f"[DEBUG] LLM Response Type: {type(result)}")
            print(f"[DEBUG] LLM Response: {result}")
            
            # Extract MCQs from response
            if isinstance(result, dict) and "mcqs" in result:
                mcqs = result["mcqs"]
            elif isinstance(result, list):
                mcqs = result
            else:
                print(f"[ERROR] Unexpected response format: {result}")
                context["error"] = "Failed to generate MCQs. Unexpected format."
                return render(request, "mcq.html", context)
            
            print(f"[DEBUG] Generated {len(mcqs)} MCQs")
            
            if not mcqs or len(mcqs) == 0:
                context["error"] = "No MCQs were generated. Please try again."
                return render(request, "mcq.html", context)

            # Store in context for display
            context["mcqs"] = mcqs
            context["topic"] = topic
            context["count"] = count
            context["difficulty"] = difficulty

            # Store MCQs in session for PDF download
            request.session["mcqs_for_pdf"] = {
                "mcqs": mcqs,
                "title": topic,
            }
            
            print(f"[SUCCESS] Context contains {len(mcqs)} MCQs")
            print(f"[DEBUG] First MCQ: {mcqs[0] if mcqs else 'None'}")
            
        except Exception as e:
            print(f"[ERROR] Exception in mcq_view: {str(e)}")
            import traceback
            traceback.print_exc()
            context["error"] = f"Error generating MCQs: {str(e)}"
            return render(request, "mcq.html", context)

    return render(request, "mcq.html", context)


def download_mcq_pdf(request):
    """Generate and download PDF of MCQs"""
    mcq_session_data = request.session.get("mcqs_for_pdf")

    if not mcq_session_data:
        return HttpResponse("No MCQs generated yet. Please generate MCQs first.", status=400)

    try:
        mcqs = mcq_session_data["mcqs"]
        title = mcq_session_data["title"]

        print(f"[DEBUG] Generating PDF for {len(mcqs)} MCQs")

        pdf_bytes = generate_styled_mcq_pdf(mcqs, title)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{title}_MCQs.pdf"'
        return response
        
    except Exception as e:
        print(f"[ERROR] PDF download failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


# ========================= SUMMARY VIEWS (UNCHANGED) =========================
def summary_view(request):
    """Generate AI summary from text input"""
    context = {}

    if request.method == "POST":
        print("[DEBUG] Summary POST request received")
        
        text_content = request.POST.get("text", "").strip()
        summary_type = request.POST.get("type", "short")
        tone_style = request.POST.get("tone", "simple")

        print(f"[DEBUG] Content length: {len(text_content)}, Type: {summary_type}, Tone: {tone_style}")

        # Validation
        if not text_content:
            context["error"] = "Please enter some text to summarize."
            return render(request, "summarizer.html", context)

        if len(text_content) < 50:
            context["error"] = "Please enter at least 50 characters to generate a meaningful summary."
            return render(request, "summarizer.html", context)

        # Generate Summary
        try:
            print("[DEBUG] Calling summary chain...")
            
            summary_result = summary_chain.invoke({
                "sum_content": text_content,
                "summary_type": summary_type,
                "tone_style": tone_style
            })
            
            print(f"[DEBUG] Summary generated, length: {len(summary_result)}")
            
            if not summary_result or len(summary_result.strip()) == 0:
                context["error"] = "Failed to generate summary. Please try again."
                return render(request, "summarizer.html", context)

            # Store in context for display
            context["output"] = summary_result
            context["text"] = text_content
            context["type"] = summary_type
            context["tone"] = tone_style

            # Store summary in session for PDF download
            request.session["summary_for_pdf"] = {
                "summary_text": summary_result,
                "topic": f"{summary_type.title()} Summary ({tone_style})",
            }
            
            print(f"[SUCCESS] Summary generated and stored in session")
            
        except Exception as e:
            print(f"[ERROR] Exception in summary_view: {str(e)}")
            import traceback
            traceback.print_exc()
            context["error"] = f"Error generating summary: {str(e)}"
            return render(request, "summarizer.html", context)

    return render(request, "summarizer.html", context)


def download_summary_pdf(request):
    """Generate and download PDF of summary"""
    summary_session_data = request.session.get("summary_for_pdf")

    if not summary_session_data:
        return HttpResponse("No summary generated yet. Please generate a summary first.", status=400)

    try:
        summary_text = summary_session_data["summary_text"]
        topic = summary_session_data["topic"]

        print(f"[DEBUG] Generating Summary PDF: {topic}")

        pdf_bytes = generate_summary_pdf(summary_text, topic)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{topic}_Summary.pdf"'
        return response
        
    except Exception as e:
        print(f"[ERROR] Summary PDF download failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


# ========================= TUTORIAL VIEWS (UNCHANGED) =========================
def tutorial_view(request):
    """Generate AI tutorial from topic"""
    context = {}

    if request.method == "POST":
        print("[DEBUG] Tutorial POST request received")
        
        topic = request.POST.get("topic", "").strip()
        depth = request.POST.get("depth", "medium")

        print(f"[DEBUG] Topic: {topic}, Depth: {depth}")

        # Validation
        if not topic:
            context["error"] = "Please enter a topic for tutorial generation."
            return render(request, "tutorials.html", context)

        if len(topic) < 3:
            context["error"] = "Please enter a valid topic (at least 3 characters)."
            return render(request, "tutorials.html", context)

        # Map depth selection to numeric values
        depth_mapping = {
            "short": "1",
            "medium": "2",
            "full": "3"
        }
        depth_value = depth_mapping.get(depth, "2")

        # Generate Tutorial
        try:
            print(f"[DEBUG] Calling tutorial chain with depth={depth_value}...")
            
            tutorial_result = tutorial_chain.invoke({
                "topic": topic,
                "depth": depth_value
            })
            
            print(f"[DEBUG] Tutorial generated, length: {len(tutorial_result)}")
            
            if not tutorial_result or len(tutorial_result.strip()) == 0:
                context["error"] = "Failed to generate tutorial. Please try again."
                return render(request, "tutorials.html", context)

            # Store in context for display
            context["output"] = tutorial_result
            context["topic"] = topic
            context["depth"] = depth

            # Store tutorial in session for PDF download
            request.session["tutorial_for_pdf"] = {
                "tutorial_text": tutorial_result,
                "topic": topic,
            }
            
            print(f"[SUCCESS] Tutorial generated and stored in session")
            
        except Exception as e:
            print(f"[ERROR] Exception in tutorial_view: {str(e)}")
            import traceback
            traceback.print_exc()
            context["error"] = f"Error generating tutorial: {str(e)}"
            return render(request, "tutorials.html", context)

    return render(request, "tutorials.html", context)


def download_tutorial_pdf(request):
    """Generate and download PDF of tutorial"""
    tutorial_session_data = request.session.get("tutorial_for_pdf")

    if not tutorial_session_data:
        return HttpResponse("No tutorial generated yet. Please generate a tutorial first.", status=400)

    try:
        tutorial_text = tutorial_session_data["tutorial_text"]
        topic = tutorial_session_data["topic"]

        print(f"[DEBUG] Generating Tutorial PDF: {topic}")

        # Generate PDF bytes
        pdf_bytes = generate_tutorial_pdf(tutorial_text, topic)

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{topic}_Tutorial.pdf"'
        return response
        
    except Exception as e:
        print(f"[ERROR] Tutorial PDF download failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


# ========================= QUIZ VIEWS (SYNC) =========================
def quiz_view(request):
    """Generate interactive quiz (sync version for fallback)"""
    context = {}

    if request.method == "POST":
        print("[DEBUG] Quiz POST request received")
        
        topic = request.POST.get("topic", "").strip()
        count = request.POST.get("count", "10").strip()
        difficulty = request.POST.get("difficulty", "medium")

        print(f"[DEBUG] Topic: {topic}, Count: {count}, Difficulty: {difficulty}")

        # Validation
        if not topic:
            context["error"] = "Please enter a topic for quiz generation."
            return render(request, "quiz.html", context)

        if len(topic) < 3:
            context["error"] = "Please enter a valid topic (at least 3 characters)."
            return render(request, "quiz.html", context)

        try:
            count = int(count)
            if count <= 0 or count > 100:
                context["error"] = "Please enter a number between 1 and 100."
                return render(request, "quiz.html", context)
        except ValueError:
            context["error"] = "Invalid number format."
            return render(request, "quiz.html", context)

        # Generate Quiz
        try:
            print(f"[DEBUG] Calling quiz generator...")
            
            quiz_questions = generate_quiz(topic, count, difficulty)
            
            print(f"[DEBUG] Quiz generated with {len(quiz_questions)} questions")
            
            if not quiz_questions or len(quiz_questions) == 0:
                context["error"] = "Failed to generate quiz. Please try again."
                return render(request, "quiz.html", context)

            # Convert to JSON format for JavaScript
            questions_json = json.dumps(quiz_questions)
            
            # Store in context for display
            context["questions_json"] = questions_json
            context["topic"] = topic
            context["count"] = count
            context["difficulty"] = difficulty
            
            print(f"[SUCCESS] Quiz ready with {len(quiz_questions)} questions")
            
        except Exception as e:
            print(f"[ERROR] Exception in quiz_view: {str(e)}")
            import traceback
            traceback.print_exc()
            context["error"] = f"Error generating quiz: {str(e)}"
            return render(request, "quiz.html", context)

    return render(request, "quiz.html", context)

from django.shortcuts import redirect
#==============MCQ ASYNC VIEW (UPDATED) ==================
def mcq_view_async(request):
    print("🚀 ASYNC MCQ VIEW HIT")

    if request.method == "POST":
        topic = request.POST.get("topic", "").strip()
        count = request.POST.get("count", "").strip()
        difficulty = request.POST.get("difficulty", "medium")

        if not topic or not count:
            return render(request, "mcq.html", {"error": "Missing inputs"})

        count = int(count)

        # 🔒 PREVENT DUPLICATE TASK ON REFRESH
        existing_task_id = request.session.get("mcq_task_id")
        if existing_task_id:
            return redirect("mcq_async")  # name of your mcq url

        task = mcq_generation_task.delay(topic, count, difficulty)

        # ✅ Store task info in session
        request.session["mcq_task_id"] = task.id
        request.session["mcq_topic"] = topic

        return redirect("mcq_async")

    # 👇 GET request (refresh safe)
    context = {
        "task_id": request.session.get("mcq_task_id"),
        "topic": request.session.get("mcq_topic"),
    }

    return render(request, "mcq.html", context)


# ===== ASYNC TUTORIAL VIEW (REFRESH SAFE) =====
def tutorial_view_async(request):
    """
    Asynchronous tutorial generation using Celery
    """
    print("🚀 ASYNC TUTORIAL VIEW HIT")

    if request.method == "POST":
        topic = request.POST.get("topic", "").strip()
        depth = request.POST.get("depth", "medium")

        print(f"[DEBUG] Tutorial Async - Topic: {topic}, Depth: {depth}")

        # Validation
        if not topic:
            return render(request, "tutorials.html", {
                "error": "Please enter a topic for tutorial generation."
            })

        if len(topic) < 3:
            return render(request, "tutorials.html", {
                "error": "Please enter a valid topic (at least 3 characters)."
            })

        # 🔒 PREVENT DUPLICATE TASK ON REFRESH
        existing_task_id = request.session.get("tutorial_task_id")
        if existing_task_id:
            return redirect("tutorial_async")  # ✅ make sure URL name exists

        depth_mapping = {
            "short": "1",
            "medium": "2",
            "full": "3"
        }
        depth_value = depth_mapping.get(depth, "2")

        # Trigger Celery task
        task = tutorial_generation_task.delay(topic, depth_value)

        print(f"[DEBUG] Tutorial task triggered: {task.id}")

        # ✅ STORE TASK INFO IN SESSION
        request.session["tutorial_task_id"] = task.id
        request.session["tutorial_topic"] = topic
        request.session["tutorial_depth"] = depth

        return redirect("tutorial_async")

    # 👇 SAFE GET REQUEST (REFRESH SAFE)
    context = {
        "task_id": request.session.get("tutorial_task_id"),
        "topic": request.session.get("tutorial_topic"),
        "depth": request.session.get("tutorial_depth"),
    }

    return render(request, "tutorials.html", context)


# ===== ASYNC SUMMARY VIEW (UPDATED) =====
def summary_view_async(request):
    """
    Asynchronous summary generation using Celery
    """
    print("🚀 ASYNC SUMMARY VIEW HIT")

    if request.method == "POST":
        text_content = request.POST.get("text", "").strip()
        summary_type = request.POST.get("type", "short")
        tone_style = request.POST.get("tone", "simple")

        print(f"[DEBUG] Summary Async - Text length: {len(text_content)}, Type: {summary_type}, Tone: {tone_style}")

        # Validation
        if not text_content:
            return render(request, "summarizer.html", {"error": "Please enter some text to summarize."})

        if len(text_content) < 50:
            return render(request, "summarizer.html", {"error": "Please enter at least 50 characters."})

        # 🔒 PREVENT DUPLICATE TASK ON REFRESH
        existing_task_id = request.session.get("summary_task_id")
        if existing_task_id:
            return redirect("summary_async")  # make sure URL name exists

        # Trigger Celery task
        task = summary_generation_task.delay(
            text_content,
            summary_type,
            tone_style
        )

        print(f"[DEBUG] Summary task triggered: {task.id}")

        # ✅ STORE TASK INFO IN SESSION
        request.session["summary_task_id"] = task.id
        request.session["summary_type"] = summary_type
        request.session["summary_tone"] = tone_style

        return redirect("summary_async")

    # 👇 SAFE GET REQUEST (REFRESH SAFE)
    context = {
        "task_id": request.session.get("summary_task_id"),
        "type": request.session.get("summary_type"),
        "tone": request.session.get("summary_tone"),
    }

    return render(request, "summarizer.html", context)


# ===== ASYNC QUIZ VIEW (REFRESH SAFE) =====
@csrf_exempt
def quiz_view_async(request):
    """
    Asynchronous quiz generation using Celery (refresh-safe)
    """
    print("🚀 ASYNC QUIZ VIEW HIT")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            topic = data.get("topic", "").strip()
            count = int(data.get("count", 10))
            difficulty = data.get("difficulty", "medium")

            # Validation
            if not topic:
                return JsonResponse({"error": "Topic required"}, status=400)

            if len(topic) < 3:
                return JsonResponse({"error": "Topic too short"}, status=400)

            if count <= 0 or count > 100:
                return JsonResponse({"error": "Invalid question count"}, status=400)

            # 🔒 PREVENT DUPLICATE TASK ON REFRESH
            existing_task_id = request.session.get("quiz_task_id")
            if existing_task_id:
                return JsonResponse({
                    "task_id": existing_task_id,
                    "message": "Quiz already generating"
                })

            # 🚀 Trigger Celery task
            task = quiz_generation_task.delay(topic, count, difficulty)

            # ✅ STORE IN SESSION
            request.session["quiz_task_id"] = task.id
            request.session["quiz_topic"] = topic
            request.session["quiz_count"] = count
            request.session["quiz_difficulty"] = difficulty

            print(f"[DEBUG] Quiz task triggered: {task.id}")

            return JsonResponse({
                "task_id": task.id,
                "message": "Quiz generation started"
            })

        except Exception as e:
            print(f"[ERROR] Quiz async error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    # GET → refresh safe
    return JsonResponse({
        "task_id": request.session.get("quiz_task_id"),
        "topic": request.session.get("quiz_topic"),
    })


# ===== TASK STATUS VIEW (FIXED FOR FRONTEND COMPATIBILITY) =====
def task_status_view(request, task_id):
    """
    Check Celery task status and return JSON matching frontend expectations
    """
    try:
        result = AsyncResult(task_id)
        
        print(f"[TASK STATUS] Task ID: {task_id}, State: {result.state}")
        
        if result.state == "SUCCESS":
            request.session.pop("mcq_task_id", None)
            request.session.pop("mcq_topic", None)
            request.session.pop("summary_task_id", None)
            request.session.pop("summary_type", None)
            request.session.pop("summary_tone", None)
            request.session.pop("tutorial_task_id", None)
            request.session.pop("tutorial_topic", None)
            request.session.pop("tutorial_depth", None)
            request.session.pop("quiz_task_id", None)
            request.session.pop("quiz_topic", None)
            request.session.pop("quiz_count", None)
            request.session.pop("quiz_difficulty", None)
            

            data = {
                "ready": True,
                "successful": True,
                "result": result.result,
                "status": result.state
            }

            print(f"[TASK STATUS] SUCCESS - Result type: {type(result.result)}")
            
        elif result.state == "FAILURE":
            data = {
                "ready": True,
                "successful": False,
                "error": str(result.info),
                "status": result.state
            }
            print(f"[TASK STATUS] FAILURE - Error: {str(result.info)}")
            
        else:
            data = {
                "ready": False,
                "successful": False,
                "status": result.state
            }
            print(f"[TASK STATUS] PENDING/PROCESSING - State: {result.state}")

        return JsonResponse(data)
        
    except Exception as e:
        print(f"[TASK STATUS ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "ready": True,
            "successful": False,
            "error": str(e)
        }, status=500)

# ===== STORE MCQs IN SESSION FOR PDF DOWNLOAD (ADDED) =====
@csrf_exempt
@require_POST
def store_mcqs_view(request):
    """
    Store MCQs in session for PDF download
    """
    try:
        data = json.loads(request.body)
        mcqs = data.get("mcqs", [])
        title = data.get("title", "Generated MCQs")
        
        request.session["mcqs_for_pdf"] = {
            "mcqs": mcqs,
            "title": title
        }
        
        print(f"[SESSION] Stored {len(mcqs)} MCQs for PDF download")
        
        return JsonResponse({"success": True})
        
    except Exception as e:
        print(f"[SESSION ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)

# ===== STORE SUMMARY IN SESSION FOR PDF DOWNLOAD (ADDED) =====
@csrf_exempt
@require_POST
def store_summary_view(request):
    """
    Store summary in session for PDF download
    """
    try:
        data = json.loads(request.body)
        summary_text = data.get("summary_text", "")
        summary_type = data.get("summary_type", "short")
        tone_style = data.get("tone_style", "simple")
        
        request.session["summary_for_pdf"] = {
            "summary_text": summary_text,
            "topic": f"{summary_type.title()} Summary ({tone_style})"
        }
        
        print(f"[SESSION] Stored summary for PDF download (length: {len(summary_text)})")
        
        return JsonResponse({"success": True})
        
    except Exception as e:
        print(f"[SESSION ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)

# ===== STORE TUTORIAL IN SESSION FOR PDF DOWNLOAD (ADDED) =====
@csrf_exempt
@require_POST
def store_tutorial_view(request):
    """
    Store tutorial in session for PDF download
    """
    try:
        data = json.loads(request.body)
        tutorial_text = data.get("tutorial_text", "")
        topic = data.get("topic", "Generated Tutorial")
        
        request.session["tutorial_for_pdf"] = {
            "tutorial_text": tutorial_text,
            "topic": topic
        }
        
        print(f"[SESSION] Stored tutorial for PDF download (length: {len(tutorial_text)})")
        
        return JsonResponse({"success": True})
        
    except Exception as e:
        print(f"[SESSION ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)