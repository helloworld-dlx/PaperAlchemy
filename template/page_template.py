# -*- coding: utf-8 -*-
"""
exam-review v3: lazy rendering + event delegation + 3-tab layout
Target: single HTML, ~350-400KB, all features.
"""
import json, re, html as html_module, os

# ============ Config (fill in before running) ============
KNOWLEDGE_POINTS = [
    {"id":"kp01","lecture":1,"title":"知识点名称","definition":"定义",
     "key_points":["要点1"],"memory_hook":"钩子","common_mistakes":["错误"],
     "keywords":["关键词"]},
]
ESSAY_QUESTIONS = [{"id":"eq01","question":"简答题","answer":"答案"}]
LECTURE_TITLES = {1:"第1讲"}
QUESTIONS_JSON_PATH = r"questions.json"
OUTPUT_PATH = r"output.html"
USE_KATEX = False
DEFAULT_SHOW = 6
COURSE_NAME = "期末复习笔记"
# ==========================================================

TYPE_MAP = {"单选题":0,"多选题":1,"判断题":2,"填空题":3}
TYPE_NAMES = ["单选题","多选题","判断题","填空题"]
TYPE_ORDER = {2:0,0:1,3:2,1:3}  # judgment→single→fill→multi for sorting

def load_questions(path):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

def match_questions(questions, kps):
    matches = {kp["id"]:[] for kp in kps}
    unmatched = []
    for q in questions:
        text = (q.get("question","")+" "+" ".join(q.get("options",[]))).lower()
        scores = []
        for kp in kps:
            s = 0
            for kw in kp["keywords"]:
                kwl = kw.lower()
                if re.search(r'\b'+re.escape(kwl)+r'\b',text): s+=3
                elif kwl in text: s+=1
            scores.append((kp["id"],s))
        scores.sort(key=lambda x:x[1],reverse=True)
        best,bs = scores[0]
        if bs>0: matches[best].append(q)
        else: unmatched.append(q)
    if unmatched: matches[kps[0]["id"]].extend(unmatched)
    return matches

def compact_q(q):
    return [q["id"],TYPE_MAP[q["type"]],q["question"],
            q.get("options",[]),q["answer"]]

def compact_kps(kps, matches, q_map):
    """Convert KPs to JS-friendly dicts, adding matched question indices"""
    out = []
    for kp in kps:
        k = {"id":kp["id"],"lec":kp["lecture"],"t":kp["title"],
             "d":kp["definition"],"kp":kp["key_points"],
             "mh":kp["memory_hook"],"cm":kp["common_mistakes"],
             "qs":sorted([q_map[q["id"]] for q in matches[kp["id"]]],
                         key=lambda i: TYPE_ORDER.get(i,99))}
        out.append(k)
    return out

# ==================== CSS ====================
CSS = r"""
:root{--bg:#f8f9fa;--card:#fff;--text:#212529;--muted:#6c757d;--primary:#2563eb;
       --primary-light:#dbeafe;--border:#dee2e6;--shadow:0 2px 8px rgba(0,0,0,.08);
       --radius:10px;--red:#ef4444;--green:#10b981}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
     "Hiragino Sans GB","Microsoft YaHei",sans-serif;background:var(--bg);
     color:var(--text);line-height:1.7}
/* topbar */
.topbar{position:fixed;top:0;left:0;right:0;min-height:56px;background:var(--card);
        border-bottom:1px solid var(--border);display:flex;flex-wrap:wrap;
        align-items:center;justify-content:space-between;padding:6px 12px;
        z-index:100;box-shadow:var(--shadow);gap:4px}
.topbar-title{font-weight:700;font-size:15px;white-space:nowrap}
.topbar-stats{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.progress-wrap{height:4px;background:var(--border);border-radius:2px;width:60px;flex-shrink:0}
.progress-fill{height:100%;background:var(--primary);border-radius:2px;width:0;transition:width .3s}
.progress-label{font-size:11px;color:var(--muted);white-space:nowrap}
.wrong-badge{font-size:11px;background:#fee2e2;color:var(--red);padding:1px 6px;
             border-radius:10px;font-weight:600;display:none}
/* tabs */
.tab-nav{display:flex;gap:2px;border-bottom:2px solid var(--border);margin-bottom:20px}
.tab-btn{padding:8px 16px;border:none;background:transparent;cursor:pointer;
         font-size:14px;color:var(--muted);border-bottom:2px solid transparent;
         margin-bottom:-2px;transition:all .15s}
.tab-btn:hover{color:var(--primary)}
.tab-btn.active{color:var(--primary);border-bottom-color:var(--primary);font-weight:600}
.tab-panel{display:none}
.tab-panel.active{display:block}
/* sidebar */
.sidebar{position:fixed;top:56px;left:0;bottom:0;width:240px;background:var(--card);
         border-right:1px solid var(--border);overflow-y:auto;padding:14px;z-index:90;
         transition:transform .2s;box-shadow:2px 0 8px rgba(0,0,0,.04)}
.sidebar.hidden{transform:translateX(-100%)}
.sidebar h3{margin:12px 0 6px;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.sidebar .lec-title{font-weight:700;font-size:12px;padding:4px 8px;background:var(--bg);border-radius:4px;margin:8px 0 3px;color:var(--text)}
.sidebar .nav-kp{display:block;padding:5px 8px 5px 14px;font-size:12px;color:var(--text);
                  text-decoration:none;border-radius:5px;cursor:pointer;margin:1px 0;transition:all .1s}
.sidebar .nav-kp:hover{background:var(--primary-light);color:var(--primary)}
.sidebar .nav-kp .kp-badge{float:right;font-size:10px;color:var(--muted);
                             background:var(--bg);padding:1px 5px;border-radius:8px}
.sidebar .subtitle{font-size:12px;font-weight:600;color:var(--primary);padding:4px 8px;margin-top:10px}
.main{margin-left:240px;margin-top:56px;padding:16px;max-width:860px}
/* cards */
.lecture-section{background:var(--card);border-radius:var(--radius);padding:20px;margin-bottom:16px;box-shadow:var(--shadow)}
.lecture-header{font-size:20px;font-weight:800;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid var(--primary-light)}
.kp-card{border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:14px}
.kp-title{font-size:17px;font-weight:700;color:var(--primary);margin-bottom:8px}
.kp-section{margin-bottom:10px}
.kp-section-title{font-weight:600;font-size:13px;color:var(--muted);margin-bottom:3px}
.kp-section ul{margin:0;padding-left:18px}
.kp-section li{margin-bottom:3px;font-size:14px}
.memory-hook{background:#fff7ed;border-left:4px solid #f59e0b;padding:8px 10px;border-radius:0 6px 6px 0;font-size:13px}
.question{border:1px solid var(--border);border-radius:8px;padding:10px;margin-bottom:8px;background:var(--bg);transition:opacity .2s}
.question.dimmed{opacity:.2}
.question-text{font-weight:500;margin-bottom:6px}
.question-meta{display:flex;gap:6px;margin-bottom:6px}
.badge{font-size:11px;padding:2px 6px;border-radius:20px;font-weight:600}
.badge-single{background:#dbeafe;color:#1e40af}
.badge-multi{background:#fce7f3;color:#9d174d}
.badge-judge{background:#d1fae5;color:#065f46}
.badge-fill{background:#fef3c7;color:#92400e}
.options{margin:0;padding-left:16px;list-style:none}
.options li{margin-bottom:2px}
.answer{margin-top:6px;padding:6px 10px;background:#ecfdf5;border-radius:6px;font-weight:600;color:#065f46;display:none}
.answer.show{display:block}
.answer-toggle{margin-top:6px;font-size:12px;color:var(--primary);cursor:pointer;user-select:none}
.q-actions{display:none;gap:6px;margin-top:6px}
.q-actions.show{display:flex}
.q-btn{padding:2px 8px;border:1px solid var(--border);border-radius:14px;cursor:pointer;font-size:11px;background:#fff;transition:all .15s}
.q-btn-correct{border-color:var(--green);color:var(--green)}
.q-btn-correct.on{background:var(--green);color:#fff}
.q-btn-wrong{border-color:var(--red);color:var(--red)}
.q-btn-wrong.on{background:var(--red);color:#fff}
.expand-btn{display:block;width:100%;padding:6px;border:1px dashed var(--border);border-radius:6px;cursor:pointer;font-size:12px;color:var(--muted);background:transparent;margin-top:8px}
.expand-btn:hover{background:var(--primary-light);color:var(--primary)}
.kp-questions-hidden{display:none}
/* filter bar */
.filter-bar{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px;align-items:center}
.filter-bar select{padding:4px 8px;border:1px solid var(--border);border-radius:6px;font-size:13px;background:var(--card)}
.filter-bar .btn{padding:4px 10px;border:1px solid var(--border);background:var(--card);border-radius:6px;cursor:pointer;font-size:13px;color:var(--text);white-space:nowrap}
.filter-bar .btn.active{background:var(--primary-light);border-color:var(--primary);color:var(--primary)}
/* essay */
.essay-card{border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:10px}
.essay-ans{background:#eff6ff;color:#1e40af;padding:8px 10px;border-radius:6px;margin-top:6px}
/* mock */
.mock-settings{margin-bottom:16px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.mock-settings label{font-size:13px}
.mock-settings input{width:50px;padding:3px;border:1px solid var(--border);border-radius:4px}
.mock-result{background:var(--primary-light);padding:12px;border-radius:8px;margin-bottom:16px;font-size:15px;font-weight:600}
.empty-state{text-align:center;color:var(--muted);padding:40px}
/* flow chart */
/* go-to-quiz button */
.goto-quiz{display:inline-flex;align-items:center;gap:4px;padding:4px 12px;background:var(--primary);color:#fff;border:none;border-radius:20px;cursor:pointer;font-size:12px;font-weight:600;transition:all .15s;text-decoration:none}
.goto-quiz:hover{background:#1d4ed8;transform:translateX(2px)}
.goto-quiz:after{content:' →'}
/* topbar buttons */
.btn-toggle{display:inline-flex;align-items:center;gap:3px;padding:4px 12px;border:1.5px solid var(--primary);background:transparent;border-radius:16px;cursor:pointer;font-size:12px;color:var(--primary);white-space:nowrap;transition:all .15s;font-weight:500}
.btn-toggle:hover{background:var(--primary-light)}
.btn-toggle:before{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--primary);transition:all .15s}
.btn-toggle.on:before{background:var(--green)}
.btn-toggle.on{background:#f0fdf4;border-color:var(--green);color:var(--green)}
/* mobile */
@media(max-width:768px){
    .sidebar{width:200px;top:80px;box-shadow:2px 0 8px rgba(0,0,0,.06)}
    .main{margin-left:0;margin-top:80px;padding:8px}
    .topbar-title{font-size:12px}
    .tab-btn{padding:6px 10px;font-size:12px}
    .lecture-section{padding:12px}
    .lecture-header{font-size:17px}
    .kp-card{padding:10px}
    .kp-title{font-size:15px}
}
"""
if USE_KATEX:
    CSS += """.katex-display{overflow-x:auto;overflow-y:hidden}"""

# ==================== JS ====================
JS = r"""
const Q=window.Q;const K=window.K;const E=window.E||[];const L=window.L||{};
const LS='erv3';const DSP=window.DEFAULT_SHOW||6;
const TYPES=['单选题','多选题','判断题','填空题'];
const BADGES=['badge-single','badge-multi','badge-judge','badge-fill'];

function e(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function gs(){try{return JSON.parse(localStorage.getItem(LS)||'{}')}catch(e){return{}}}
function ss(d){localStorage.setItem(LS,JSON.stringify(d))}

// --- event delegation ---
document.addEventListener('click',function(ev){
    const t=ev.target;
    // answer toggle
    const at=t.closest('[id^="toggle-"]');
    if(at){ev.preventDefault();
        const qid=at.id.replace('toggle-','');
        const ans=document.getElementById('ans-'+qid);
        const act=document.getElementById('act-'+qid);
        if(ans.classList.toggle('show')){at.textContent='隐藏答案';if(act)act.classList.add('show')}
        else{at.textContent='显示答案';if(act)act.classList.remove('show')}
        return;
    }
    // mark correct
    if(t.closest('.q-btn-correct')){ev.preventDefault();
        const qid=parseInt(t.closest('[id^="q-"]').id.replace('q-',''));
        markQ(qid,'correct');return;
    }
    // mark wrong
    if(t.closest('.q-btn-wrong')){ev.preventDefault();
        const qid=parseInt(t.closest('[id^="q-"]').id.replace('q-',''));
        markQ(qid,'wrong');return;
    }
    // expand kp questions
    if(t.closest('.expand-btn')){ev.preventDefault();
        const btn=t.closest('.expand-btn');
        const kpId=btn.id.replace('expand-','');
        const hidden=document.getElementById('qshidden-'+kpId);
        if(hidden.style.display==='block'){hidden.style.display='none';btn.textContent=btn.dataset.label}
        else{hidden.style.display='block';btn.textContent='收起'}
        return;
    }
    // tab switch
    if(t.closest('.tab-btn')){ev.preventDefault();
        switchTab(t.closest('.tab-btn').dataset.tab);return;
    }
    // toggle sidebar
    if(t.closest('#btn-sidebar')){ev.preventDefault();
        document.getElementById('sidebar').classList.toggle('hidden');return;
    }
    // toggle all answers
    if(t.closest('#btn-toggle-all')){ev.preventDefault();
        window._all=!window._all;
        document.querySelectorAll('.answer').forEach(el=>el.classList.toggle('show',window._all));
        document.querySelectorAll('.answer-toggle').forEach(el=>el.textContent=window._all?'隐藏答案':'显示答案');
        document.querySelectorAll('.q-actions').forEach(el=>el.classList.toggle('show',window._all));
        const btn=document.getElementById('btn-toggle-all');
        btn.textContent=window._all?'隐藏答案':'显示答案';
        btn.classList.toggle('on',window._all);
        return;
    }
    // wrong mode toggle
    if(t.closest('#btn-wrong')){ev.preventDefault();
        const btn=t.closest('#btn-wrong');
        const on=btn.classList.toggle('active');
        btn.textContent=on?'显示全部':'只看错题';
        if(document.getElementById('tab-quiz').classList.contains('active'))renderQuiz();
    }
    // generate mock
    if(t.closest('#btn-gen-mock')){ev.preventDefault();genMock();return;}
    // submit mock
    if(t.closest('#btn-sub-mock')){ev.preventDefault();subMock();return;}
    // sidebar nav click -> scroll to kp
    if(t.closest('.nav-kp')){ev.preventDefault();
        const kpId=t.closest('.nav-kp').dataset.kp;
        if(kpId){
            const el=document.getElementById('kp-'+kpId);
            if(el){el.scrollIntoView({behavior:'smooth',block:'start'});
                   if(window.innerWidth<=768)document.getElementById('sidebar').classList.add('hidden')}
        }
        return;
    }
});

// --- mark question (toggle) ---
function markQ(qid,status){
    const d=gs();
    const cKey='c'+qid,wKey='w'+qid;
    if(status==='correct'){
        if(d[cKey]){delete d[cKey]}  // toggle off
        else{d[cKey]=true;delete d[wKey]}  // toggle on, clear wrong
    }else{
        if(d[wKey]){delete d[wKey]}
        else{d[wKey]=true;delete d[cKey]}
    }
    ss(d);updateQBtn(qid);updateStats();
}
function updateQBtn(qid){
    const d=gs();const el=document.getElementById('q-'+qid);if(!el)return;
    const bc=el.querySelector('.q-btn-correct'),bw=el.querySelector('.q-btn-wrong');
    if(bc)bc.classList.toggle('on',!!d['c'+qid]);
    if(bw)bw.classList.toggle('on',!!d['w'+qid]);
}

// --- tab switching ---
let currentKpFilter=null;
function switchTab(tab,kpFilter){
    currentKpFilter=kpFilter||null;
    document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));
    document.querySelectorAll('.tab-panel').forEach(p=>p.classList.toggle('active',false));
    const panel=document.getElementById('tab-'+tab);
    if(panel)panel.classList.add('active');
    if(tab==='quiz')renderQuiz();
    if(tab==='mock')renderMock();
    updateStats();
}
function review2quiz(kpId){switchTab('quiz',kpId);}

// --- render review (flow chart + kp cards) ---
function renderReview(){
    const cont=document.getElementById('tab-review');
    if(!cont||cont.dataset.rendered==='1')return;
    cont.dataset.rendered='1';
    let h='';
    const lecs=Object.keys(L).sort((a,b)=>a-b);
    lecs.forEach(lec=>{
        const kps=K.filter(k=>k.lec===parseInt(lec));
        const tq=kps.reduce((s,k)=>s+(k.qs?k.qs.length:0),0);
        h+=`<div class="lecture-section" id="lecture-${lec}"><div class="lecture-header">第${lec}讲 · ${e(L[lec])}（${tq}题）</div>`;
        kps.forEach(kp=>{
            const qTotal=kp.qs?kp.qs.length:0;
            const visible=kp.qs?kp.qs.slice(0,DSP):[];
            const hidden=kp.qs?kp.qs.slice(DSP):[];
            let qsH='';
            visible.forEach(i=>{if(Q[i])qsH+=rqHtml(Q[i])});
            if(hidden.length>0){
                qsH+=`<div class="kp-questions-hidden" id="qshidden-${kp.id}">`;
                hidden.forEach(i=>{if(Q[i])qsH+=rqHtml(Q[i])});
                qsH+=`</div><button class="expand-btn" id="expand-${kp.id}" data-label="展开全部 ${qTotal} 题">展开全部 ${qTotal} 题</button>`;
            }
            h+=`<div class="kp-card" id="kp-${kp.id}"><div class="kp-title">${e(kp.t)}</div>
<div class="kp-section"><div class="kp-section-title">概念定义</div><div>${e(kp.d)}</div></div>
<div class="kp-section"><div class="kp-section-title">关键要点</div><ul>${kp.kp.map(p=>`<li>${e(p)}</li>`).join('')}</ul></div>
<div class="kp-section"><div class="kp-section-title">记忆钩子</div><div class="memory-hook">${e(kp.mh)}</div></div>
<div class="kp-section"><div class="kp-section-title">常见错误</div><ul>${kp.cm.map(m=>`<li>${e(m)}</li>`).join('')}</ul></div>
<div class="questions-header"><div style="font-weight:600;">相关题目（${qTotal}道）</div><a href="javascript:void(0)" class="goto-quiz" onclick="review2quiz('${kp.id}')">去刷题</a></div>
<div>${qsH}</div></div>`;
        });
        h+='</div>';
    });
    // essay section
    if(E.length>0){
        h+=`<div class="lecture-section" id="essay-section"><div class="lecture-header">简答题专区</div>`;
        h+=`<p style="color:var(--muted);font-size:13px;margin-bottom:12px;">以下为根据课件整理的高频简答题及参考答案要点。</p>`;
        E.forEach(eq=>{
            h+=`<div class="essay-card"><div class="question-text">${e(eq.q)}</div><div class="essay-ans">${e(eq.a)}</div></div>`;
        });
        h+='</div>';
    }
    cont.innerHTML=h;
    // restore button states
    restoreBtns();
    updateStats();
}

// --- render single question from compact data ---
function rqHtml(qarr){
    if(!qarr)return'';
    const [id,tn,text,opts,ans]=qarr;
    const bc=BADGES[tn];
    let oH='';
    if(opts&&opts.length)oH='<ol class="options">'+opts.map(o=>`<li>${e(o)}</li>`).join('')+'</ol>';
    const aText=tn===2?(ans==='A'?'正确':'错误'):ans;
    const d=gs();
    const cOn=d['c'+id]?' on':'',wOn=d['w'+id]?' on':'';
    return `<div class="question" id="q-${id}"><div class="question-meta"><span class="badge ${bc}">${TYPES[tn]}</span></div><div class="question-text">${e(text)}</div>${oH}<div class="answer" id="ans-${id}">答案：${e(aText)}</div><div class="answer-toggle" id="toggle-${id}">显示答案</div><div class="q-actions" id="act-${id}"><button class="q-btn q-btn-correct${cOn}">我会了</button><button class="q-btn q-btn-wrong${wOn}">我不会</button></div></div>`;
}

// --- restore button states for all visible questions ---
function restoreBtns(){
    const d=gs();
    document.querySelectorAll('[id^="q-"]').forEach(el=>{
        const qid=parseInt(el.id.replace('q-',''));
        const bc=el.querySelector('.q-btn-correct'),bw=el.querySelector('.q-btn-wrong');
        if(bc)bc.classList.toggle('on',!!d['c'+qid]);
        if(bw)bw.classList.toggle('on',!!d['w'+qid]);
    });
}

// --- render quiz tab ---
function renderQuiz(){
    const cont=document.getElementById('tab-quiz-content');
    if(!cont)return;
    const d=gs();const wrongOnly=document.getElementById('btn-wrong')?.classList.contains('active');
    let qList=[];
    if(currentKpFilter){
        const kp=K.find(k=>k.id===currentKpFilter);
        if(kp&&kp.qs){kp.qs.forEach(i=>{if(Q[i])qList.push(i)});}
    }else{
        Q.forEach((q,i)=>{if(q)qList.push(i)});
    }
    if(wrongOnly){qList=qList.filter(i=>d['w'+Q[i][0]]);}
    if(qList.length===0){cont.innerHTML='<div class="empty-state">没有匹配的题目</div>';return;}
    // sort by type: judgment→single→fill→multi
    qList.sort((a,b)=>{const o={2:0,0:1,3:2,1:3};return o[Q[a][1]]-o[Q[b][1]];});
    let h=renderFilterBar();
    h+='<div style="margin-bottom:8px;font-size:13px;color:var(--muted);">共 '+qList.length+' 题</div>';
    qList.forEach(i=>{h+=rqHtml(Q[i]);});
    cont.innerHTML=h;
    restoreBtns();
}

function renderFilterBar(){
    let opts='<option value="">全部知识点</option>';
    K.forEach(k=>{opts+=`<option value="${k.id}">${e(k.t)}</option>`;});
    const sel=currentKpFilter||'';
    return `<div class="filter-bar"><select id="filter-kp" onchange="filterQuiz(this.value)">${opts}</select><select id="filter-type" onchange="filterQuizType(this.value)"><option value="">全部题型</option><option value="0">单选题</option><option value="1">多选题</option><option value="2">判断题</option><option value="3">填空题</option></select><button class="btn" id="btn-wrong" onclick="toggleWrongInQuiz()">只看错题</button><span style="font-size:12px;color:var(--muted)">` + (currentKpFilter?e(K.find(k=>k.id===currentKpFilter)?.t||''):'全部知识点') + `</span></div>`;
}
function filterQuiz(kpId){currentKpFilter=kpId||null;renderQuiz();}
function filterQuizType(t){currentTypeFilter=t||null;renderQuiz();}
function toggleWrongInQuiz(){
    const btn=document.getElementById('btn-wrong');
    btn.classList.toggle('active');
    btn.textContent=btn.classList.contains('active')?'显示全部':'只看错题';
    renderQuiz();
}

// --- render mock tab ---
let mockQ=[];
function renderMock(){
    const cont=document.getElementById('tab-mock-content');
    if(!cont)return;
    if(mockQ.length===0){
        cont.innerHTML=`<div class="mock-settings"><label>单选题：<input type="number" id="mock-single" value="40" min="0"></label><label>多选题：<input type="number" id="mock-multi" value="20" min="0"></label><label>判断题：<input type="number" id="mock-judge" value="20" min="0"></label><label>填空题：<input type="number" id="mock-fill" value="10" min="0"></label><button class="filter-bar btn" id="btn-gen-mock" style="background:var(--primary);color:#fff;">生成试卷</button><button class="filter-bar btn" id="btn-sub-mock">查看答案</button></div><div class="mock-result" id="mock-result" style="display:none;"></div><div id="mock-container"><div class="empty-state">点击"生成试卷"开始模拟考试</div></div>`;
    }
}
function genMock(){
    const s=parseInt(document.getElementById('mock-single')?.value)||0;
    const m=parseInt(document.getElementById('mock-multi')?.value)||0;
    const j=parseInt(document.getElementById('mock-judge')?.value)||0;
    const f=parseInt(document.getElementById('mock-fill')?.value)||0;
    const bt={0:[],1:[],2:[],3:[]};
    Q.forEach((q,i)=>{if(q&&bt[q[1]])bt[q[1]].push(i);});
    const sh=a=>{const r=[...a];for(let i=r.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[r[i],r[j]]=[r[j],r[i]];}return r;};
    mockQ=[...sh(bt[0]).slice(0,s),...sh(bt[1]).slice(0,m),...sh(bt[2]).slice(0,j),...sh(bt[3]).slice(0,f)];
    const cont=document.getElementById('mock-container');
    if(mockQ.length===0){cont.innerHTML='<div class="empty-state">请设置题目数量后点击"生成试卷"</div>';return;}
    let h='';
    mockQ.forEach((i,idx)=>{
        const q=Q[i];const bc=BADGES[q[1]];
        let oH=q[3]&&q[3].length?'<ol class="options">'+q[3].map(o=>`<li>${e(o)}</li>`).join('')+'</ol>':'';
        h+=`<div class="question"><div class="question-meta"><span class="badge ${bc}">${TYPES[q[1]]}</span><span class="badge" style="background:#f3f4f6;color:#374151;">第${idx+1}题</span></div><div class="question-text">${e(q[2])}</div>${oH}<div class="answer" id="m-ans-${q[0]}"></div></div>`;
    });
    cont.innerHTML=h;
    document.getElementById('mock-result').style.display='none';
}
function subMock(){
    mockQ.forEach(i=>{const q=Q[i];const el=document.getElementById('m-ans-'+q[0]);if(el){el.style.display='block';el.classList.add('show');el.textContent='答案：'+(q[1]===2?(q[4]==='A'?'正确':'错误'):q[4]);}});
    document.getElementById('mock-result').style.display='block';
    document.getElementById('mock-result').innerHTML='共 '+mockQ.length+' 题，请对照答案自行批改。错题可回到刷题考试标记"我不会"。';
}

// --- stats ---
function updateStats(){
    const d=gs();let wc=0,cc=0,total=0;
    Q.forEach(q=>{if(!q)return;total++;if(d['c'+q[0]])cc++;if(d['w'+q[0]])wc++;});
    const marked=wc+cc;
    const pct=total>0?Math.round(marked/total*100):0;
    const fill=document.getElementById('progress-fill');if(fill)fill.style.width=pct+'%';
    const lbl=document.getElementById('progress-label');if(lbl)lbl.textContent=pct+'%';
    const wEl=document.getElementById('wrong-count');if(wEl){wEl.textContent=wc;wEl.style.display=wc>0?'inline':'none';}
    const cEl=document.getElementById('correct-count');if(cEl)cEl.textContent=cc;
}

// --- sidebar ---
function buildSidebar(){
    const sb=document.getElementById('sidebar');
    if(!sb||sb.dataset.built==='1')return;
    sb.dataset.built='1';
    let h='<h3>知识点导航</h3>';
    Object.keys(L).sort((a,b)=>a-b).forEach(lec=>{
        h+=`<div class="lec-title">第${lec}讲 · ${e(L[lec])}</div>`;
        K.filter(k=>k.lec===parseInt(lec)).forEach(kp=>{
            h+=`<span class="nav-kp" data-kp="${kp.id}">${e(kp.t)}<span class="kp-badge">${kp.qs?kp.qs.length:0}</span></span>`;
        });
    });
    h+='<h3 style="margin-top:14px;">快捷入口</h3>';
    h+='<span class="nav-kp" onclick="document.getElementById(\'essay-section\').scrollIntoView({behavior:\'smooth\'})">简答题专区</span>';
    sb.innerHTML=h;
}

// --- init ---
document.addEventListener('DOMContentLoaded',function(){
    buildSidebar();
    renderReview();
    updateStats();
});
"""

# ==================== HTML Build ====================
def build_html(questions, kps, matches, essays, lecture_titles):
    # Build Q mapping (id->index)
    id2idx = {}
    for i, q in enumerate(questions):
        id2idx[q["id"]] = i

    # Compact questions: [[id,type_num,q,opts,ans],...]
    q_compact = [compact_q(q) for q in questions]

    # Compact KPs with question indices
    k_compact = compact_kps(kps, matches, id2idx)

    # Compact essays
    e_compact = [{"q":e["question"], "a":e["answer"]} for e in essays]

    qjson = json.dumps(q_compact, ensure_ascii=False, separators=(',',':'))
    kjson = json.dumps(k_compact, ensure_ascii=False, separators=(',',':'))
    ejson = json.dumps(e_compact, ensure_ascii=False, separators=(',',':'))
    ljson = json.dumps({str(k):v for k,v in lecture_titles.items()}, ensure_ascii=False, separators=(',',':'))

    dsp = DEFAULT_SHOW
    cn = html_module.escape(COURSE_NAME)

    katex_head = ""
    if USE_KATEX:
        katex_head = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"><\/script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"><\/script>
"""

    return f"""<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{cn}</title>{katex_head}<style>{CSS}</style></head><body>
<div class="topbar"><div style="display:flex;align-items:center;gap:8px;">
<button class="filter-bar btn" id="btn-sidebar">☰</button>
<div class="topbar-title">{cn}</div>
<div class="progress-wrap"><div class="progress-fill" id="progress-fill"></div></div>
<span class="progress-label" id="progress-label">0%</span>
<span class="wrong-badge" id="wrong-count">0</span>
<span style="font-size:11px;color:var(--muted);" id="correct-count">0</span>
</div>
<div style="display:flex;gap:4px;flex-wrap:wrap;">
<button class="btn-toggle" id="btn-toggle-all">显示答案</button></div></div>

<div class="sidebar" id="sidebar"></div>

<div class="main">
<div class="tab-nav">
<button class="tab-btn active" data-tab="review">复习脉络</button>
<button class="tab-btn" data-tab="quiz">刷题考试</button>
<button class="tab-btn" data-tab="mock">模拟考试</button>
</div>

<div class="tab-panel active" id="tab-review"></div>

<div class="tab-panel" id="tab-quiz">
<div id="tab-quiz-content"><div class="empty-state">点击左侧"刷题考试"开始选择性刷题</div></div>
</div>

<div class="tab-panel" id="tab-mock">
<div id="tab-mock-content"><div class="empty-state">点击左侧"模拟考试"开始模拟</div></div>
</div>
</div>

<script>window.Q={qjson};window.K={kjson};window.E={ejson};window.L={ljson};window.DEFAULT_SHOW={dsp};{JS}</script>
</body></html>"""

def main():
    questions = load_questions(QUESTIONS_JSON_PATH)
    matches = match_questions(questions, KNOWLEDGE_POINTS)
    html = build_html(questions, KNOWLEDGE_POINTS, matches, ESSAY_QUESTIONS, LECTURE_TITLES)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated: {OUTPUT_PATH} ({len(html)} bytes)")
    for kp in KNOWLEDGE_POINTS:
        print(f"  {kp['title']}: {len(matches[kp['id']])} questions")

if __name__ == "__main__":
    main()
