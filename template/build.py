# -*- coding: utf-8 -*-
"""
PaperAlchemy two-file build orchestrator.
Usage:
    from template.build import build_all
    build_all(knowledge_points, essay_questions, lecture_titles,
              questions_json_path, output_dir, course_name,
              notes_filename=None, quiz_filename=None)
"""
import os
import sys
import json

# Ensure this directory is on path for imports of sibling modules
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import shared_utils
import notes_template
import quiz_template


def build_all(knowledge_points, essay_questions, lecture_titles,
              questions_json_path, output_dir, course_name,
              notes_filename=None, quiz_filename=None,
              max_sample_questions=5):
    """Generate both notes HTML and quiz HTML."""
    os.makedirs(output_dir, exist_ok=True)

    notes_path = os.path.join(output_dir, notes_filename or f"{course_name}-复习笔记.html")
    quiz_path = os.path.join(output_dir, quiz_filename or f"{course_name}-刷题考试.html")

    questions = shared_utils.load_questions(questions_json_path)
    matches = shared_utils.match_questions(questions, knowledge_points)

    # Notes
    notes_template.COURSE_NAME = f"{course_name} · 复习笔记"
    notes_template.OUTPUT_PATH = notes_path
    notes_template.MAX_SAMPLE_QUESTIONS = max_sample_questions
    notes_html = notes_template.build_html(
        questions, knowledge_points, matches, essay_questions, lecture_titles
    )
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(notes_html)
    print(f"[Notes] {notes_path} ({len(notes_html)} bytes)")

    # Quiz
    quiz_template.COURSE_NAME = f"{course_name} · 刷题考试"
    quiz_template.OUTPUT_PATH = quiz_path
    quiz_html = quiz_template.build_html(
        questions, knowledge_points, matches, essay_questions, lecture_titles
    )
    with open(quiz_path, "w", encoding="utf-8") as f:
        f.write(quiz_html)
    print(f"[Quiz ] {quiz_path} ({len(quiz_html)} bytes)")

    # Print matching stats
    for kp in knowledge_points:
        print(f"  {kp['title']}: {len(matches[kp['id']])} questions")

    return notes_path, quiz_path


if __name__ == "__main__":
    # Example run when executed directly with JSON config
    config_path = os.path.join(_THIS_DIR, "build_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        build_all(
            cfg["knowledge_points"],
            cfg.get("essay_questions", []),
            cfg.get("lecture_titles", {}),
            cfg["questions_json_path"],
            cfg["output_dir"],
            cfg["course_name"],
            cfg.get("notes_filename"),
            cfg.get("quiz_filename"),
            cfg.get("max_sample_questions", 5),
        )
    else:
        print("Create build_config.json or import build_all() from your course script.")
