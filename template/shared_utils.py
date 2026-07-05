# -*- coding: utf-8 -*-
"""
PaperAlchemy shared utilities for notes_template and quiz_template.
"""
import json
import re
import html as html_module

TYPE_MAP = {"单选题": 0, "多选题": 1, "判断题": 2, "填空题": 3}
TYPE_NAMES = ["单选题", "多选题", "判断题", "填空题"]
TYPE_ORDER = {2: 0, 0: 1, 3: 2, 1: 3}  # judgment → single → fill → multi


def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_questions(questions, kps):
    """Match every question to the best knowledge point by keyword scoring."""
    matches = {kp["id"]: [] for kp in kps}
    unmatched = []
    for q in questions:
        text = (q.get("question", "") + " " + " ".join(q.get("options", []))).lower()
        scores = []
        for kp in kps:
            s = 0
            for kw in kp.get("keywords", []):
                kwl = kw.lower()
                if re.search(r'\b' + re.escape(kwl) + r'\b', text):
                    s += 3
                elif kwl in text:
                    s += 1
            scores.append((kp["id"], s))
        scores.sort(key=lambda x: x[1], reverse=True)
        best, bs = scores[0]
        if bs > 0:
            matches[best].append(q)
        else:
            unmatched.append(q)
    if unmatched and kps:
        matches[kps[0]["id"]].extend(unmatched)
    return matches


def compact_q(q):
    """Convert question dict to compact list."""
    return [q["id"], TYPE_MAP.get(q["type"], 0), q["question"],
            q.get("options", []), q["answer"]]


def compact_kps(kps, matches, q_map):
    """Convert KPs to JS-friendly dicts with matched question indices."""
    out = []
    for kp in kps:
        k = {
            "id": kp["id"],
            "lec": kp["lecture"],
            "t": kp["title"],
            "d": kp["definition"],
            "kp": kp.get("key_points", []),
            "mh": kp.get("memory_hook", ""),
            "cm": kp.get("common_mistakes", []),
            "qs": sorted([q_map[q["id"]] for q in matches.get(kp["id"], [])],
                         key=lambda i: TYPE_ORDER.get(i, 99))
        }
        if kp.get("cases"):
            k["cases"] = kp["cases"]
        out.append(k)
    return out


def escape(s):
    return html_module.escape(str(s))


def option_label(idx):
    return chr(ord('A') + idx)
