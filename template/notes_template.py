# -*- coding: utf-8 -*-
"""
PaperAlchemy Notes Template v4
Generates a detailed, read-only review-notes HTML file.
Features: sidebar navigation, knowledge cards, 3-5 sample questions per KP,
essay section, common-mistake summary, quick-review checklist, search.
"""
import json
import os
from shared_utils import (
    load_questions, match_questions, compact_q, compact_kps, escape, option_label
)

# ============ Config ============
KNOWLEDGE_POINTS = []
ESSAY_QUESTIONS = []
LECTURE_TITLES = {}
QUESTIONS_JSON_PATH = r"questions.json"
OUTPUT_PATH = r"notes.html"
COURSE_NAME = "期末复习笔记"
MAX_SAMPLE_QUESTIONS = 5  # per knowledge point
# =================================


# ==================== CSS ====================
CSS = r"""
:root{--bg:#f8f9fa;--card:#fff;--text:#212529;--muted:#6c757d;--primary:#2563eb;
       --primary-light:#dbeafe;--primary-dark:#1d4ed8;--border:#dee2e6;--shadow:0 2px 8px rgba(0,0,0,.08);
       --radius:10px;--green:#10b981;--amber:#f59e0b;--red:#ef4444;--purple:#8b5cf6}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
     "Hiragino Sans GB","Microsoft YaHei",sans-serif;background:var(--bg);
     color:var(--text);line-height:1.7}
/* topbar */
.topbar{position:fixed;top:0;left:0;right:0;min-height:56px;background:var(--card);
        border-bottom:1px solid var(--border);display:flex;flex-wrap:wrap;
        align-items:center;justify-content:space-between;padding:8px 12px;
        z-index:100;box-shadow:var(--shadow);gap:8px}
.topbar-title{font-weight:700;font-size:15px;white-space:nowrap}
.topbar-actions{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.search-box{padding:5px 10px;border:1px solid var(--border);border-radius:16px;font-size:13px;width:160px;outline:none}
.search-box:focus{border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-light)}
.btn{padding:5px 12px;border:1px solid var(--border);background:var(--card);border-radius:16px;cursor:pointer;font-size:12px;color:var(--text);white-space:nowrap;transition:all .15s}
.btn:hover{background:var(--primary-light);color:var(--primary);border-color:var(--primary)}
.btn-primary{background:var(--primary);color:#fff;border-color:var(--primary)}
.btn-primary:hover{background:var(--primary-dark)}
/* sidebar */
.sidebar{position:fixed;top:56px;left:0;bottom:0;width:240px;background:var(--card);
         border-right:1px solid var(--border);overflow-y:auto;padding:14px;z-index:90;
         transition:transform .2s;box-shadow:2px 0 8px rgba(0,0,0,.04)}
.sidebar.hidden{transform:translateX(-100%)}
.sidebar h3{margin:14px 0 6px;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.sidebar .lec-title{font-weight:700;font-size:12px;padding:5px 8px;background:var(--bg);border-radius:4px;margin:8px 0 3px;color:var(--text)}
.sidebar .nav-kp{display:block;padding:5px 8px 5px 14px;font-size:12px;color:var(--text);
                  text-decoration:none;border-radius:5px;cursor:pointer;margin:1px 0;transition:all .1s}
.sidebar .nav-kp:hover{background:var(--primary-light);color:var(--primary)}
.sidebar .nav-kp .kp-badge{float:right;font-size:10px;color:var(--muted);
                             background:var(--bg);padding:1px 5px;border-radius:8px}
.sidebar .nav-kp.hidden-by-search{display:none}
.main{margin-left:240px;margin-top:56px;padding:16px;max-width:900px}
/* lecture */
.lecture-section{background:var(--card);border-radius:var(--radius);padding:20px;margin-bottom:16px;box-shadow:var(--shadow)}
.lecture-header{font-size:20px;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid var(--primary-light);display:flex;align-items:center;gap:8px}
.lecture-badge{background:var(--primary-light);color:var(--primary);font-size:12px;padding:2px 8px;border-radius:12px}
/* kp card */
.kp-card{border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:14px;scroll-margin-top:70px}
.kp-title{font-size:18px;font-weight:700;color:var(--primary);margin-bottom:10px;display:flex;align-items:center;gap:8px}
.kp-num{background:var(--primary);color:#fff;font-size:11px;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;border-radius:50%}
.kp-section{margin-bottom:12px}
.kp-section-title{font-weight:600;font-size:13px;color:var(--muted);margin-bottom:5px;display:flex;align-items:center;gap:4px}
.kp-section ul{margin:0;padding-left:18px}
.kp-section li{margin-bottom:4px;font-size:14px}
.memory-hook{background:#fff7ed;border-left:4px solid var(--amber);padding:10px 12px;border-radius:0 6px 6px 0;font-size:14px;color:#78350f}
.common-mistakes{background:#fef2f2;border-left:4px solid var(--red);padding:10px 12px;border-radius:0 6px 6px 0;font-size:14px;color:#7f1d1d}
.exam-tip{background:#f0fdf4;border-left:4px solid var(--green);padding:10px 12px;border-radius:0 6px 6px 0;font-size:14px;color:#14532d}
/* questions */
.sample-header{font-weight:700;font-size:14px;margin:14px 0 8px;display:flex;align-items:center;justify-content:space-between}
.question{border:1px solid var(--border);border-radius:8px;padding:10px;margin-bottom:8px;background:var(--bg)}
.question-text{font-weight:500;margin-bottom:6px;font-size:14px}
.question-meta{display:flex;gap:6px;margin-bottom:6px}
.badge{font-size:11px;padding:2px 6px;border-radius:20px;font-weight:600}
.badge-single{background:#dbeafe;color:#1e40af}
.badge-multi{background:#fce7f3;color:#9d174d}
.badge-judge{background:#d1fae5;color:#065f46}
.badge-fill{background:#fef3c7;color:#92400e}
.options{margin:0;padding-left:16px;list-style:none}
.options li{margin-bottom:3px;font-size:13px}
.options li.correct{background:#d1fae5;border-radius:4px;padding:1px 4px;color:#065f46;font-weight:600}
.answer-box{margin-top:8px;padding:8px 10px;background:#ecfdf5;border-radius:6px;font-weight:600;color:#065f46;font-size:13px}
.expand-note{font-size:12px;color:var(--muted);margin-top:6px}
/* essay */
.essay-section{background:var(--card);border-radius:var(--radius);padding:20px;margin-bottom:16px;box-shadow:var(--shadow)}
.essay-card{border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:10px}
.essay-ans{background:#eff6ff;color:#1e40af;padding:8px 10px;border-radius:6px;margin-top:6px;font-size:14px}
/* summary sections */
.summary-section{background:var(--card);border-radius:var(--radius);padding:20px;margin-bottom:16px;box-shadow:var(--shadow)}
.summary-title{font-size:18px;font-weight:800;margin-bottom:14px}
.mistake-item{padding:10px;border-bottom:1px solid var(--border)}
.mistake-item:last-child{border-bottom:none}
.mistake-kp{font-weight:700;color:var(--primary);font-size:13px}
.mistake-text{font-size:13px;color:var(--muted)}
.checklist{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}
.check-item{display:flex;align-items:flex-start;gap:8px;padding:8px;background:var(--bg);border-radius:6px;font-size:13px;cursor:pointer;user-select:none}
.check-item input{margin-top:2px}
.empty-state{text-align:center;color:var(--muted);padding:40px}
.notice{font-size:12px;color:var(--muted);background:var(--bg);padding:8px 12px;border-radius:6px;margin-bottom:12px}
/* mobile */
@media(max-width:768px){
    .sidebar{width:200px;top:80px}
    .main{margin-left:0;margin-top:80px;padding:8px}
    .topbar-title{font-size:12px}
    .search-box{width:120px}
    .lecture-section{padding:12px}
    .lecture-header{font-size:17px}
    .kp-card{padding:12px}
    .checklist{grid-template-columns:1fr}
}
"""

# ==================== JS ====================
JS = r"""
const K=window.K||[];const L=window.L||{};
function e(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}

document.addEventListener('click',function(ev){
    const t=ev.target;
    if(t.closest('#btn-sidebar')){ev.preventDefault();document.getElementById('sidebar').classList.toggle('hidden');return;}
    if(t.closest('.nav-kp')){ev.preventDefault();
        const id=t.closest('.nav-kp').dataset.kp;
        const el=document.getElementById('kp-'+id);
        if(el){el.scrollIntoView({behavior:'smooth',block:'start'});
               if(window.innerWidth<=768)document.getElementById('sidebar').classList.add('hidden');}
        return;
    }
    if(t.closest('#btn-toggle-answers')){ev.preventDefault();toggleAllAnswers();return;}
    if(t.closest('.check-item')){const cb=t.closest('.check-item').querySelector('input');if(cb&&ev.target.tagName!=='INPUT'){cb.checked=!cb.checked;saveChecklist();}}
});

document.getElementById('search-box')?.addEventListener('input',function(ev){
    const q=ev.target.value.trim().toLowerCase();
    filterContent(q);
});

function toggleAllAnswers(){
    window._showAns=!window._showAns;
    document.querySelectorAll('.answer-box').forEach(el=>el.style.display=window._showAns?'block':'none');
    document.querySelectorAll('.options li').forEach(li=>li.classList.toggle('correct',window._showAns));
    const btn=document.getElementById('btn-toggle-answers');
    if(btn){btn.textContent=window._showAns?'隐藏答案':'显示答案';btn.classList.toggle('btn-primary',window._showAns);}
}

function filterContent(q){
    if(!q){document.querySelectorAll('.kp-card').forEach(c=>c.style.display='');document.querySelectorAll('.lecture-section').forEach(s=>s.style.display='');document.querySelectorAll('.nav-kp').forEach(n=>n.classList.remove('hidden-by-search'));return;}
    const ids=[];
    document.querySelectorAll('.kp-card').forEach(c=>{
        const txt=(c.textContent||c.innerText||'').toLowerCase();
        const show=txt.includes(q);
        c.style.display=show?'':'none';
        if(show)ids.push(c.id.replace('kp-',''));
    });
    document.querySelectorAll('.lecture-section').forEach(s=>{
        const has=s.querySelector('.kp-card:not([style*="display: none"])');
        s.style.display=has?'':'none';
    });
    document.querySelectorAll('.nav-kp').forEach(n=>{
        n.classList.toggle('hidden-by-search',!ids.includes(n.dataset.kp));
    });
}

function buildSidebar(){
    const sb=document.getElementById('sidebar');if(!sb)return;
    let h='<h3>知识点导航</h3>';
    Object.keys(L).sort((a,b)=>a-b).forEach(lec=>{
        h+=`<div class="lec-title">第${lec}讲 · ${e(L[lec])}</div>`;
        K.filter(k=>k.lec===parseInt(lec)).forEach(kp=>{
            h+=`<span class="nav-kp" data-kp="${kp.id}">${e(kp.t)}<span class="kp-badge">${kp.qs?kp.qs.length:0}</span></span>`;
        });
    });
    h+='<h3 style="margin-top:14px;">快捷入口</h3>';
    if(document.getElementById('exam-tips')){
        h+='<span class="nav-kp" onclick="document.getElementById(\'exam-tips\').scrollIntoView({behavior:\'smooth\'})">考场答题提醒</span>';
    }
    if(document.getElementById('essay-section')){
        h+='<span class="nav-kp" onclick="document.getElementById(\'essay-section\').scrollIntoView({behavior:\'smooth\'})">简答题专区（25题）</span>';
    }
    if(document.getElementById('common-mistakes')){
        h+='<span class="nav-kp" onclick="document.getElementById(\'common-mistakes\').scrollIntoView({behavior:\'smooth\'})">常见错误汇总</span>';
    }
    if(document.getElementById('checklist')){
        h+='<span class="nav-kp" onclick="document.getElementById(\'checklist\').scrollIntoView({behavior:\'smooth\'})">考前检查清单</span>';
    }
    sb.innerHTML=h;
}

function saveChecklist(){
    const checked=[];
    document.querySelectorAll('.check-item input').forEach(cb=>{if(cb.checked)checked.push(cb.dataset.id);});
    localStorage.setItem('pa_notes_checklist',JSON.stringify(checked));
}
function restoreChecklist(){
    try{const checked=JSON.parse(localStorage.getItem('pa_notes_checklist')||'[]');
    document.querySelectorAll('.check-item input').forEach(cb=>{cb.checked=checked.includes(cb.dataset.id);});}catch(e){}
}

document.addEventListener('DOMContentLoaded',function(){
    buildSidebar();
    restoreChecklist();
    document.querySelectorAll('.check-item input').forEach(cb=>cb.addEventListener('change',saveChecklist));
});
"""


def build_html(questions, kps, matches, essays, lecture_titles):
    id2idx = {q["id"]: i for i, q in enumerate(questions)}
    q_compact = [compact_q(q) for q in questions]
    k_compact = compact_kps(kps, matches, id2idx)
    e_compact = [{"q": e["question"], "a": e["answer"]} for e in essays]

    qjson = json.dumps(q_compact, ensure_ascii=False, separators=(',', ':'))
    kjson = json.dumps(k_compact, ensure_ascii=False, separators=(',', ':'))
    ejson = json.dumps(e_compact, ensure_ascii=False, separators=(',', ':'))
    ljson = json.dumps({str(k): v for k, v in lecture_titles.items()},
                       ensure_ascii=False, separators=(',', ':'))

    cn = escape(COURSE_NAME)
    body = render_body(k_compact, q_compact, lecture_titles, essays)

    return f"""<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{cn}</title><style>{CSS}</style></head><body>
<div class="topbar">
  <div style="display:flex;align-items:center;gap:8px;">
    <button class="btn" id="btn-sidebar">☰</button>
    <div class="topbar-title">{cn}</div>
  </div>
  <div class="topbar-actions">
    <input type="text" class="search-box" id="search-box" placeholder="搜索知识点...">
    <button class="btn btn-primary" id="btn-toggle-answers">显示答案</button>
  </div>
</div>
<div class="sidebar" id="sidebar"></div>
<div class="main">
  <div class="notice">这是「复习笔记」文件：左侧导航，每个知识点配 3-5 道例题，答案默认隐藏。需要刷题请打开「刷题考试」HTML。</div>
  {body}
</div>
<script>window.Q={qjson};window.K={kjson};window.E={ejson};window.L={ljson};{JS}</script>
</body></html>"""


def render_body(k_compact, q_compact, lecture_titles, essays):
    html_parts = []

    lecs = sorted([int(k) for k in lecture_titles.keys()])
    for lec in lecs:
        kps = [k for k in k_compact if k["lec"] == lec]
        tq = sum(len(k.get("qs", [])) for k in kps)
        html_parts.append(f'<div class="lecture-section" id="lecture-{lec}">')
        html_parts.append(
            f'<div class="lecture-header"><span class="lecture-badge">第{lec}讲</span>'
            f'{escape(lecture_titles[lec])} <span style="font-size:13px;color:var(--muted);font-weight:500;">（{tq}题）</span></div>'
        )
        for idx, kp in enumerate(kps, 1):
            html_parts.append(render_kp(kp, idx, q_compact))
        html_parts.append('</div>')

    # Exam tips
    html_parts.append('<div class="summary-section" id="exam-tips"><div class="summary-title">考场答题提醒</div>')
    html_parts.append('<div class="exam-tip" style="margin-bottom:8px;"><strong>单选题：</strong>先排除明显错误项，注意题目问的是「正确」还是「错误」。</div>')
    html_parts.append('<div class="exam-tip" style="margin-bottom:8px;"><strong>多选题：</strong>宁缺毋滥，不确定的选项不要选。</div>')
    html_parts.append('<div class="exam-tip" style="margin-bottom:8px;"><strong>判断题：</strong>警惕绝对化词语（「只能」「必须」「一定」），课本原话优先按教材判断。</div>')
    html_parts.append('<div class="exam-tip" style="margin-bottom:8px;"><strong>填空题：</strong>关键词要准确，不写错别字。</div>')
    html_parts.append('<div class="exam-tip"><strong>简答题：</strong>分点作答，先写核心概念，再展开要点；字数不够时用例子补充。</div>')
    html_parts.append('</div>')

    # Essay section
    if essays:
        html_parts.append('<div class="essay-section" id="essay-section"><div class="lecture-header">简答题专区</div>')
        html_parts.append('<p style="color:var(--muted);font-size:13px;margin-bottom:12px;">以下 25 道题为根据课件重点和题库高频考点整理，建议考前通读并尝试自己口述答案。</p>')
        for eq in essays:
            html_parts.append(
                f'<div class="essay-card"><div class="question-text">{escape(eq["question"])}</div>'
                f'<div class="essay-ans">{escape(eq["answer"])}</div></div>'
            )
        html_parts.append('</div>')

    # Common mistakes summary
    html_parts.append('<div class="summary-section" id="common-mistakes"><div class="summary-title">常见错误汇总</div>')
    html_parts.append('<p style="color:var(--muted);font-size:13px;margin-bottom:12px;">以下错误来自各知识点卡片的「常见错误」，考前重点扫一遍，避免掉坑。</p>')
    any_mistake = False
    for kp in k_compact:
        for m in kp.get("cm", []):
            any_mistake = True
            html_parts.append(
                f'<div class="mistake-item"><div class="mistake-kp">{escape(kp["t"])}</div>'
                f'<div class="mistake-text">{escape(m)}</div></div>'
            )
    if not any_mistake:
        html_parts.append('<div class="empty-state">暂无常见错误数据</div>')
    html_parts.append('</div>')

    # Quick checklist
    html_parts.append('<div class="summary-section" id="checklist"><div class="summary-title">考前快速检查清单</div>')
    html_parts.append('<p style="color:var(--muted);font-size:13px;margin-bottom:12px;">按讲次勾选，不确定的项回到对应知识点卡片再看一遍。</p>')
    html_parts.append('<div class="checklist">')
    for lec in lecs:
        kps = [k for k in k_compact if k["lec"] == lec]
        for kp in kps:
            html_parts.append(
                f'<label class="check-item"><input type="checkbox" data-id="{escape(kp["id"])}-def"><span>第{lec}讲 · 能说清「{escape(kp["t"])}」的定义和{len(kp.get("kp", []))}个要点</span></label>'
            )
            if kp.get("mh"):
                html_parts.append(
                    f'<label class="check-item"><input type="checkbox" data-id="{escape(kp["id"])}-hook"><span>能复述「{escape(kp["t"])}」的钩子：{escape(kp["mh"])}</span></label>'
                )
    html_parts.append('</div></div>')

    return '\n'.join(html_parts)


def render_kp(kp, idx, q_compact):
    parts = []
    parts.append(f'<div class="kp-card" id="kp-{kp["id"]}">')
    parts.append(f'<div class="kp-title"><span class="kp-num">{idx}</span>{escape(kp["t"])}</div>')

    parts.append('<div class="kp-section"><div class="kp-section-title">概念定义</div>')
    parts.append(f'<div style="font-size:14px;">{escape(kp["d"])}</div></div>')

    parts.append('<div class="kp-section"><div class="kp-section-title">关键要点</div><ul>')
    for p in kp.get("kp", []):
        parts.append(f'<li>{escape(p)}</li>')
    parts.append('</ul></div>')

    if kp.get("mh"):
        parts.append(f'<div class="kp-section"><div class="kp-section-title">记忆钩子</div><div class="memory-hook">{escape(kp["mh"])}</div></div>')

    if kp.get("cm"):
        parts.append('<div class="kp-section"><div class="kp-section-title">常见错误</div><div class="common-mistakes"><ul>')
        for m in kp.get("cm", []):
            parts.append(f'<li>{escape(m)}</li>')
        parts.append('</ul></div></div>')

    if kp.get("cases"):
        parts.append('<div class="kp-section"><div class="kp-section-title">典型案例</div>')
        for case in kp.get("cases", []):
            parts.append(f'<div class="exam-tip" style="margin-bottom:6px;"><strong>{escape(case.get("title","案例"))}</strong>：{escape(case.get("content",""))}</div>')
        parts.append('</div>')

    # Sample questions
    sample_indices = kp.get("qs", [])[:MAX_SAMPLE_QUESTIONS]
    total = len(kp.get("qs", []))
    if sample_indices:
        parts.append(f'<div class="sample-header"><span>例题精选（{min(total, MAX_SAMPLE_QUESTIONS)}/{total}道）</span></div>')
        for i in sample_indices:
            parts.append(render_question(q_compact[i]))
        if total > MAX_SAMPLE_QUESTIONS:
            parts.append(f'<div class="expand-note">该知识点共 {total} 道题，完整刷题请打开「刷题考试」文件。</div>')

    parts.append('</div>')
    return '\n'.join(parts)


def render_question(qarr):
    qid, tn, text, opts, ans = qarr
    type_names = ["单选题", "多选题", "判断题", "填空题"]
    badges = ["badge-single", "badge-multi", "badge-judge", "badge-fill"]

    opts_html = ''
    correct_letters = set(str(ans).replace(' ', '').replace(',', ''))
    if opts:
        opts_html = '<ol class="options">'
        for i, o in enumerate(opts):
            label = option_label(i)
            cls = 'correct' if label in correct_letters else ''
            opts_html += f'<li class="{cls}">{escape(o)}</li>'
        opts_html += '</ol>'

    if tn == 2:
        ans_text = '正确' if ans == 'A' else '错误'
    else:
        ans_text = str(ans)

    return (
        f'<div class="question"><div class="question-meta"><span class="badge {badges[tn]}">{type_names[tn]}</span></div>'
        f'<div class="question-text">{escape(text)}</div>{opts_html}'
        f'<div class="answer-box" style="display:none;">答案：{escape(ans_text)}</div></div>'
    )


def main():
    questions = load_questions(QUESTIONS_JSON_PATH)
    matches = match_questions(questions, KNOWLEDGE_POINTS)
    html = build_html(questions, KNOWLEDGE_POINTS, matches, ESSAY_QUESTIONS, LECTURE_TITLES)
    os.makedirs(os.path.dirname(OUTPUT_PATH) if os.path.dirname(OUTPUT_PATH) else '.', exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated notes: {OUTPUT_PATH} ({len(html)} bytes)")


if __name__ == "__main__":
    main()
