# -*- coding: utf-8 -*-
"""
PaperAlchemy Quiz Template v4
Generates an interactive quiz/practice HTML file.
Features: clickable answers, instant feedback, explanations, localStorage tracking,
wrong-answer retry, weakness dashboard, one-click weak-point drill, mock exam.
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
OUTPUT_PATH = r"quiz.html"
COURSE_NAME = "期末刷题"
# =================================

# ==================== CSS ====================
CSS = r"""
:root{--bg:#f8f9fa;--card:#fff;--text:#212529;--muted:#6c757d;--primary:#2563eb;
       --primary-light:#dbeafe;--primary-dark:#1d4ed8;--border:#dee2e6;--shadow:0 2px 8px rgba(0,0,0,.08);
       --radius:10px;--green:#10b981;--green-light:#d1fae5;--red:#ef4444;--red-light:#fee2e2;
       --amber:#f59e0b;--purple:#8b5cf6;--orange:#f97316}
*{box-sizing:border-box}
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
.btn{padding:5px 12px;border:1px solid var(--border);background:var(--card);border-radius:16px;cursor:pointer;font-size:12px;color:var(--text);white-space:nowrap;transition:all .15s}
.btn:hover{background:var(--primary-light);color:var(--primary);border-color:var(--primary)}
.btn.active{background:var(--primary-light);border-color:var(--primary);color:var(--primary)}
.btn-primary{background:var(--primary);color:#fff;border-color:var(--primary)}
.btn-primary:hover{background:var(--primary-dark)}
.btn-danger{background:var(--red);color:#fff;border-color:var(--red)}
.btn-danger:hover{background:#dc2626}
/* layout */
.main{margin-top:56px;padding:16px;max-width:900px;margin-left:auto;margin-right:auto}
/* dashboard */
.dashboard{background:var(--card);border-radius:var(--radius);padding:16px;margin-bottom:16px;box-shadow:var(--shadow)}
.dashboard-title{font-size:16px;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-bottom:14px}
.stat-box{background:var(--bg);border-radius:8px;padding:10px;text-align:center}
.stat-num{font-size:22px;font-weight:800;color:var(--primary)}
.stat-label{font-size:12px;color:var(--muted)}
.progress-wrap{height:6px;background:var(--border);border-radius:3px;overflow:hidden;margin-bottom:6px}
.progress-fill{height:100%;background:var(--primary);border-radius:3px;width:0;transition:width .3s}
.progress-label{font-size:12px;color:var(--muted)}
.weakness-title{font-size:14px;font-weight:700;margin:14px 0 8px}
.weakness-list{display:flex;flex-wrap:wrap;gap:6px}
.weakness-chip{padding:5px 10px;background:#fff;border:1px solid var(--border);border-radius:16px;font-size:12px;cursor:pointer;transition:all .15s}
.weakness-chip:hover{background:var(--primary-light);border-color:var(--primary)}
.weakness-chip .rate{color:var(--red);font-weight:700}
/* filter bar */
.filter-bar{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px;align-items:center;background:var(--card);padding:12px;border-radius:var(--radius);box-shadow:var(--shadow)}
.filter-bar select{padding:5px 8px;border:1px solid var(--border);border-radius:6px;font-size:13px;background:var(--card)}
.mode-tabs{display:flex;gap:4px;flex-wrap:wrap}
/* question */
.question{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:12px;box-shadow:var(--shadow)}
.question-header{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-bottom:8px}
.question-meta{display:flex;gap:6px;flex-wrap:wrap}
.badge{font-size:11px;padding:2px 6px;border-radius:20px;font-weight:600}
.badge-single{background:#dbeafe;color:#1e40af}
.badge-multi{background:#fce7f3;color:#9d174d}
.badge-judge{background:#d1fae5;color:#065f46}
.badge-fill{background:#fef3c7;color:#92400e}
.question-id{font-size:11px;color:var(--muted)}
.question-text{font-weight:500;margin-bottom:10px;font-size:15px}
.option-list{display:flex;flex-direction:column;gap:6px}
.option{display:flex;align-items:center;gap:8px;padding:8px 10px;border:1px solid var(--border);border-radius:8px;cursor:pointer;transition:all .15s;background:#fff;font-size:14px}
.option:hover{border-color:var(--primary);background:var(--primary-light)}
.option.correct{background:var(--green-light);border-color:var(--green);color:#065f46;font-weight:600}
.option.wrong{background:var(--red-light);border-color:var(--red);color:#7f1d1d}
.option input[type="checkbox"],.option input[type="radio"]{margin:0}
.option.disabled{cursor:default;pointer-events:none}
.fill-input{width:100%;padding:8px;border:1px solid var(--border);border-radius:6px;font-size:14px;margin-bottom:6px}
.feedback{margin-top:10px;padding:10px;border-radius:6px;display:none;font-size:14px}
.feedback.show{display:block}
.feedback.correct{background:var(--green-light);color:#065f46}
.feedback.wrong{background:var(--red-light);color:#7f1d1d}
.q-actions{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
/* mock */
.mock-settings{background:var(--card);border-radius:var(--radius);padding:14px;margin-bottom:14px;box-shadow:var(--shadow)}
.mock-settings label{font-size:13px}
.mock-settings input{width:50px;padding:4px;border:1px solid var(--border);border-radius:4px}
.empty-state{text-align:center;color:var(--muted);padding:40px}
.result-banner{background:var(--primary-light);padding:12px;border-radius:8px;margin-bottom:14px;font-weight:600}
/* section titles */
.section-title{font-size:18px;font-weight:800;margin:20px 0 12px}
.notice{font-size:12px;color:var(--muted);background:var(--bg);padding:8px 12px;border-radius:6px;margin-bottom:12px}
/* mobile */
@media(max-width:768px){
    .main{margin-top:80px;padding:8px}
    .topbar-title{font-size:12px}
    .stats-grid{grid-template-columns:repeat(2,1fr)}
}
"""

# ==================== JS ====================
JS = r"""
const Q=window.Q||[];const K=window.K||[];const L=window.L||{};
const LS='pa_quiz_v4';
const TYPES=['单选题','多选题','判断题','填空题'];
const BADGES=['badge-single','badge-multi','badge-judge','badge-fill'];

let currentMode='all'; // all | wrong | weak | mock
let currentKp='';
let currentType='';
let mockQuestions=[];

function e(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function gs(){try{return JSON.parse(localStorage.getItem(LS)||'{}')}catch(err){return{}}}
function ss(data){localStorage.setItem(LS,JSON.stringify(data))}

function getStats(){
    const d=gs();let total=0,correct=0,wrong=0;
    Q.forEach(q=>{if(!q)return;total++;const id=q[0];if(d['c'+id])correct++;if(d['w'+id])wrong++;});
    return{total,correct,wrong,answered:correct+wrong};
}
function getKpStats(){
    const d=gs();
    return K.map(kp=>{
        const qs=kp.qs||[];let total=0,correct=0,wrong=0;
        qs.forEach(i=>{const q=Q[i];if(!q)return;total++;const id=q[0];if(d['c'+id])correct++;if(d['w'+id])wrong++;});
        return{id:kp.id,title:kp.t,total,correct,wrong,rate:total?Math.round(correct/total*100):-1};
    }).filter(x=>x.total>0);
}

// --- event delegation ---
document.addEventListener('click',function(ev){
    const t=ev.target.closest('[data-action]');if(!t)return;
    const action=t.dataset.action;
    if(action==='mode'){setMode(t.dataset.mode);return;}
    if(action==='kp-filter'){currentKp=t.dataset.value||'';renderQuiz();return;}
    if(action==='type-filter'){currentType=t.dataset.value||'';renderQuiz();return;}
    if(action==='answer'){answerQuestion(parseInt(t.dataset.qid),t.dataset.val);return;}
    if(action==='multi-check'){return;} // handled on change
    if(action==='multi-submit'){submitMulti(parseInt(t.dataset.qid));return;}
    if(action==='fill-show'){showFillAnswer(parseInt(t.dataset.qid));return;}
    if(action==='fill-mark'){markFill(parseInt(t.dataset.qid),t.dataset.val==='1');return;}
    if(action==='weak-drill'){drillWeak(t.dataset.kp);return;}
    if(action==='gen-mock'){genMock();return;}
    if(action==='sub-mock'){subMock();return;}
    if(action==='clear-record'){if(confirm('确定清空所有答题记录？')){localStorage.removeItem(LS);renderAll();}return;}
});

function setMode(mode){
    currentMode=mode;
    if(mode==='wrong'){currentKp='';currentType='';} // wrong mode reviews all mistakes
    document.querySelectorAll('[data-action="mode"]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
    if(mode==='mock'){renderMockSetup();}
    else{renderQuiz();}
    updateDashboard();
}

function bindSelects(){
    const kpSel=document.getElementById('sel-kp');
    const typeSel=document.getElementById('sel-type');
    if(kpSel)kpSel.addEventListener('change',()=>{currentKp=kpSel.value;renderQuiz();});
    if(typeSel)typeSel.addEventListener('change',()=>{currentType=typeSel.value;renderQuiz();});
}

function getFilteredIndices(){
    const d=gs();
    let list=[];
    if(currentMode==='wrong'){
        Q.forEach((q,i)=>{if(q&&d['w'+q[0]])list.push(i);});
    }else if(currentMode==='weak' && currentKp){
        const kp=K.find(k=>k.id===currentKp);if(kp)(kp.qs||[]).forEach(i=>{if(Q[i])list.push(i);});
    }else{
        Q.forEach((q,i)=>{if(q)list.push(i);});
    }
    if(currentKp && currentMode!=='weak'){
        const kp=K.find(k=>k.id===currentKp);if(kp){const s=new Set(kp.qs||[]);list=list.filter(i=>s.has(i));}
    }
    if(currentType!==''){const tn=parseInt(currentType);list=list.filter(i=>Q[i][1]===tn);}
    // sort by type
    list.sort((a,b)=>{const o={2:0,0:1,3:2,1:3};return o[Q[a][1]]-o[Q[b][1]];});
    return list;
}

function renderAll(){
    updateDashboard();
    renderQuiz();
}

function renderQuiz(){
    const container=document.getElementById('quiz-container');
    if(!container)return;
    if(currentMode==='mock'){renderMockSetup();return;}
    const indices=getFilteredIndices();
    let h=renderFilterBar();
    h+=`<div class="notice">共 ${indices.length} 题。点击选项作答，答对/答错会自动记录到本地。</div>`;
    if(indices.length===0){h+='<div class="empty-state">没有匹配的题目</div>';container.innerHTML=h;bindSelects();return;}
    indices.forEach(i=>{h+=renderInteractiveQuestion(Q[i]);});
    container.innerHTML=h;
    bindSelects();
}

function renderFilterBar(){
    let h='<div class="filter-bar">';
    h+='<div class="mode-tabs">';
    h+='<button class="btn '+(currentMode==='all'?'active':'')+'" data-action="mode" data-mode="all">全部刷题</button>';
    h+='<button class="btn '+(currentMode==='wrong'?'active':'')+'" data-action="mode" data-mode="wrong">错题重练</button>';
    h+='<button class="btn '+(currentMode==='weak'?'active':'')+'" data-action="mode" data-mode="weak">弱项突击</button>';
    h+='<button class="btn '+(currentMode==='mock'?'active':'')+'" data-action="mode" data-mode="mock">模拟考试</button>';
    h+='</div>';
    h+='<select id="sel-kp">';
    h+='<option value="">全部知识点</option>';
    K.forEach(k=>{h+=`<option value="${k.id}" ${currentKp===k.id?'selected':''}>${e(k.t)}</option>`;});
    h+='</select>';
    h+='<select id="sel-type">';
    const typeLabels=['单选题','多选题','判断题','填空题'];
    h+='<option value="">全部题型</option>';
    typeLabels.forEach((lab,idx)=>{h+=`<option value="${idx}" ${currentType===''+idx?'selected':''}>${lab}</option>`;});
    h+='</select>';
    h+='<button class="btn btn-danger" data-action="clear-record">清空记录</button>';
    h+='</div>';
    return h;
}

function renderInteractiveQuestion(qarr){
    const [id,tn,text,opts,ans]=qarr;
    const d=gs();
    // In wrong mode, questions are re-practice: do not show previous answer state
    const isWrongMode=currentMode==='wrong';
    const answered=!isWrongMode && (d['c'+id]||d['w'+id]);
    const isWrong=!isWrongMode && d['w'+id];
    const ansSet=new Set(String(ans).replace(/\s/g,'').toUpperCase());
    function optCls(i){
        const cls=['option'];
        if(answered)cls.push('disabled');
        const val=(tn===2)?(i===0?'A':'B'):optionLabel(i);
        if(answered && ansSet.has(val))cls.push('correct');
        return cls.join(' ');
    }
    let body='';
    if(tn===0){
        body='<div class="option-list">';
        opts.forEach((o,i)=>{
            const val=optionLabel(i);
            body+=`<label class="${optCls(i)}" data-action="answer" data-qid="${id}" data-val="${val}"><input type="radio" name="q${id}" ${answered?'disabled':''}> ${e(o)}</label>`;
        });
        body+='</div>';
    }else if(tn===2){
        body='<div class="option-list">';
        body+=`<label class="${optCls(0)}" data-action="answer" data-qid="${id}" data-val="A"><input type="radio" name="q${id}" ${answered?'disabled':''}> 正确</label>`;
        body+=`<label class="${optCls(1)}" data-action="answer" data-qid="${id}" data-val="B"><input type="radio" name="q${id}" ${answered?'disabled':''}> 错误</label>`;
        body+='</div>';
    }else if(tn===1){
        body='<div class="option-list">';
        opts.forEach((o,i)=>{
            const val=optionLabel(i);
            body+=`<label class="${optCls(i)}"><input type="checkbox" data-action="multi-check" data-qid="${id}" data-val="${val}" ${answered?'disabled':''}> ${e(o)}</label>`;
        });
        body+='</div>';
        if(!answered)body+=`<button class="btn btn-primary" data-action="multi-submit" data-qid="${id}">确认答案</button>`;
    }else if(tn===3){
        body=`<input type="text" class="fill-input" id="fill-${id}" placeholder="输入答案（或直接查看答案）" ${answered?'disabled':''}>`;
        if(!answered){
            body+=`<div class="q-actions"><button class="btn" data-action="fill-show" data-qid="${id}">查看答案</button></div>`;
        }
    }
    const fbCls=isWrong?'wrong':'correct';
    let ansText=String(ans);
    if(tn===2)ansText=ansText==='A'?'正确':'错误';
    const fbText=isWrong?`❌ 答错了。正确答案：${e(ansText)}`:`✅ 答对了！答案：${e(ansText)}`;
    return (
        `<div class="question" id="q-${id}"><div class="question-header"><div class="question-meta">`+
        `<span class="badge ${BADGES[tn]}">${TYPES[tn]}</span>`+
        `</div><span class="question-id">#${id}</span></div>`+
        `<div class="question-text">${e(text)}</div>${body}`+
        `<div class="feedback ${fbCls} ${answered?'show':''}" id="fb-${id}">${fbText}</div>`+
        `<div class="q-actions" id="act-${id}" style="display:${(answered && tn===3)?'flex':'none'};">`+
        `<button class="btn" onclick="markQ(${id},'correct')">标记为会</button>`+
        `<button class="btn btn-danger" onclick="markQ(${id},'wrong')">标记为不会</button>`+
        `</div></div>`
    );
}

function optionLabel(i){return String.fromCharCode(65+i);}

function answerQuestion(qid,val){
    const idx=Q.findIndex(q=>q[0]===qid);if(idx<0)return;
    const q=Q[idx];const ans=String(q[4]).replace(/\s/g,'').toUpperCase();
    const correct=ans===val;
    const d=gs();
    if(correct){d['c'+qid]=true;delete d['w'+qid];}
    else{d['w'+qid]=true;delete d['c'+qid];}
    ss(d);
    showFeedback(qid,correct,q);
    updateDashboard();
}

function submitMulti(qid){
    const idx=Q.findIndex(q=>q[0]===qid);if(idx<0)return;
    const checked=[];
    document.querySelectorAll(`input[data-qid="${qid}"]:checked`).forEach(cb=>checked.push(cb.dataset.val));
    if(checked.length===0){alert('请至少选择一个选项');return;}
    const ans=String(Q[idx][4]).replace(/\s/g,'').toUpperCase();
    const user=checked.sort().join('');
    const correct=user===ans;
    const d=gs();
    if(correct){d['c'+qid]=true;delete d['w'+qid];}
    else{d['w'+qid]=true;delete d['c'+qid];}
    ss(d);
    showFeedback(qid,correct,Q[idx]);
    updateDashboard();
}

function showFillAnswer(qid){
    const idx=Q.findIndex(q=>q[0]===qid);if(idx<0)return;
    const q=Q[idx];
    showFeedback(qid,null,q,true);
    const act=document.getElementById('act-'+qid);if(act)act.style.display='flex';
}

function markFill(qid,correct){
    const d=gs();
    if(correct){d['c'+qid]=true;delete d['w'+qid];}
    else{d['w'+qid]=true;delete d['c'+qid];}
    ss(d);renderQuiz();updateDashboard();
}

function showFeedback(qid,correct,q,fillMode=false){
    const fb=document.getElementById('fb-'+qid);if(!fb)return;
    fb.style.display='block';fb.classList.add('show');
    let ansText=String(q[4]);
    if(q[1]===2)ansText=ansText==='A'?'正确':'错误';
    if(fillMode){
        fb.className='feedback show correct';
        fb.innerHTML='答案：'+e(ansText)+'<br><span style="font-size:12px;">请根据掌握情况点击下方按钮</span>';
        return;
    }
    if(correct){fb.className='feedback show correct';fb.textContent='✅ 答对了！答案：'+ansText;}
    else{fb.className='feedback show wrong';fb.textContent='❌ 答错了。正确答案：'+ansText;}
    // disable options
    const el=document.getElementById('q-'+qid);if(el){
        el.querySelectorAll('.option').forEach(o=>{o.classList.add('disabled');o.style.pointerEvents='none';});
        el.querySelectorAll('input').forEach(i=>i.disabled=true);
        // highlight options
        const ans=String(q[4]).replace(/\s/g,'').toUpperCase();
        el.querySelectorAll('.option').forEach((o,i)=>{
            let val;
            if(q[1]===2){val=i===0?'A':'B';}
            else if(q[1]===0 || q[1]===1){val=optionLabel(i);}
            else{return;}
            const checked=o.querySelector('input:checked')!==null;
            if(ans.includes(val))o.classList.add('correct');
            else if(checked)o.classList.add('wrong');
        });
    }
    const act=document.getElementById('act-'+qid);if(act && fillMode)act.style.display='flex';
}

function markQ(qid,status){
    const d=gs();
    if(status==='correct'){d['c'+qid]=true;delete d['w'+qid];}
    else{d['w'+qid]=true;delete d['c'+qid];}
    ss(d);renderQuiz();updateDashboard();
}

function updateDashboard(){
    const stats=getStats();
    const totalEl=document.getElementById('stat-total');if(totalEl)totalEl.textContent=stats.total;
    const ansEl=document.getElementById('stat-answered');if(ansEl)ansEl.textContent=stats.answered;
    const corEl=document.getElementById('stat-correct');if(corEl)corEl.textContent=stats.correct;
    const wrEl=document.getElementById('stat-wrong');if(wrEl)wrEl.textContent=stats.wrong;
    const pct=stats.total?Math.round(stats.answered/stats.total*100):0;
    const fill=document.getElementById('progress-fill');if(fill)fill.style.width=pct+'%';
    const pl=document.getElementById('progress-label');if(pl)pl.textContent=pct+'% 已作答';
    renderWeakness();
}

function renderWeakness(){
    const box=document.getElementById('weakness-list');if(!box)return;
    const kps=getKpStats().filter(x=>x.total>=3).sort((a,b)=>a.rate-b.rate).slice(0,8);
    if(kps.length===0){box.innerHTML='<span style="color:var(--muted);font-size:12px;">答题数据不足，多刷几题后自动生成</span>';return;}
    box.innerHTML=kps.map(k=>`<span class="weakness-chip" data-action="weak-drill" data-kp="${k.id}">${e(k.title)} <span class="rate">${k.rate}%</span></span>`).join('');
}

function drillWeak(kpId){
    currentKp=kpId;currentMode='weak';
    document.getElementById('sel-kp').value=kpId;
    document.querySelectorAll('[data-action="mode"]').forEach(b=>b.classList.toggle('active',b.dataset.mode==='weak'));
    renderQuiz();window.scrollTo({top:0,behavior:'smooth'});
}

function renderMockSetup(){
    const container=document.getElementById('quiz-container');if(!container)return;
    container.innerHTML=
        `<div class="filter-bar"><div class="mode-tabs">`+
        `<button class="btn" data-action="mode" data-mode="all">全部刷题</button>`+
        `<button class="btn" data-action="mode" data-mode="wrong">错题重练</button>`+
        `<button class="btn" data-action="mode" data-mode="weak">弱项突击</button>`+
        `<button class="btn active" data-action="mode" data-mode="mock">模拟考试</button>`+
        `</div></div>`+
        `<div class="mock-settings"><label>单选题：<input type="number" id="mock-single" value="40" min="0"></label>`+
        `<label>多选题：<input type="number" id="mock-multi" value="20" min="0"></label>`+
        `<label>判断题：<input type="number" id="mock-judge" value="20" min="0"></label>`+
        `<label>填空题：<input type="number" id="mock-fill" value="10" min="0"></label>`+
        `<button class="btn btn-primary" data-action="gen-mock">生成试卷</button>`+
        `<button class="btn" data-action="sub-mock">查看答案</button></div>`+
        `<div class="result-banner" id="mock-result" style="display:none;"></div>`+
        `<div id="mock-container"><div class="empty-state">点击「生成试卷」开始模拟考试</div></div>`;
}

function genMock(){
    const s=parseInt(document.getElementById('mock-single')?.value)||0;
    const m=parseInt(document.getElementById('mock-multi')?.value)||0;
    const j=parseInt(document.getElementById('mock-judge')?.value)||0;
    const f=parseInt(document.getElementById('mock-fill')?.value)||0;
    const buckets=[[],[],[],[]];
    Q.forEach((q,i)=>{if(q)buckets[q[1]].push(i);});
    const sh=a=>{const r=[...a];for(let i=r.length-1;i>0;i--){const k=Math.floor(Math.random()*(i+1));[r[i],r[k]]=[r[k],r[i]];}return r;};
    mockQuestions=[...sh(buckets[0]).slice(0,s),...sh(buckets[1]).slice(0,m),...sh(buckets[2]).slice(0,j),...sh(buckets[3]).slice(0,f)];
    const cont=document.getElementById('mock-container');
    if(mockQuestions.length===0){cont.innerHTML='<div class="empty-state">请设置题目数量</div>';return;}
    let h='';
    mockQuestions.forEach((i,idx)=>{
        const q=Q[i];
        let oH='';
        if(q[3]&&q[3].length)oH='<ol class="options">'+q[3].map(o=>`<li>${e(o)}</li>`).join('')+'</ol>';
        h+=`<div class="question"><div class="question-header"><div class="question-meta"><span class="badge ${BADGES[q[1]]}">${TYPES[q[1]]}</span></div><span class="question-id">第${idx+1}题</span></div>`+
            `<div class="question-text">${e(q[2])}</div>${oH}<div class="feedback" id="m-ans-${q[0]}"></div></div>`;
    });
    cont.innerHTML=h;
    document.getElementById('mock-result').style.display='none';
}

function subMock(){
    mockQuestions.forEach((i,idx)=>{
        const q=Q[i];const el=document.getElementById('m-ans-'+q[0]);
        if(el){el.style.display='block';el.classList.add('show','correct');
            let ans=q[4];if(q[1]===2)ans=ans==='A'?'正确':'错误';
            el.innerHTML='答案：'+e(ans);
        }
    });
    const res=document.getElementById('mock-result');
    res.style.display='block';
    res.innerHTML='共 '+mockQuestions.length+' 题，请对照答案自行批改。错题可回到「错题重练」模式针对性练习。';
}

document.addEventListener('DOMContentLoaded',function(){
    updateDashboard();
    renderQuiz();
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

    return f"""<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{cn}</title><style>{CSS}</style></head><body>
<div class="topbar">
  <div class="topbar-title">{cn}</div>
  <div class="topbar-actions">
    <button class="btn" onclick="window.location.href='#'">顶部</button>
  </div>
</div>
<div class="main">
  <div class="dashboard">
    <div class="dashboard-title">学习仪表盘</div>
    <div class="stats-grid">
      <div class="stat-box"><div class="stat-num" id="stat-total">0</div><div class="stat-label">总题数</div></div>
      <div class="stat-box"><div class="stat-num" id="stat-answered">0</div><div class="stat-label">已作答</div></div>
      <div class="stat-box"><div class="stat-num" id="stat-correct">0</div><div class="stat-label">正确</div></div>
      <div class="stat-box"><div class="stat-num" id="stat-wrong">0</div><div class="stat-label">错题</div></div>
    </div>
    <div class="progress-wrap"><div class="progress-fill" id="progress-fill"></div></div>
    <div class="progress-label" id="progress-label">0% 已作答</div>
    <div class="weakness-title">弱项 TOP（点击突击）</div>
    <div class="weakness-list" id="weakness-list"></div>
  </div>
  <div id="quiz-container"></div>
</div>
<script>window.Q={qjson};window.K={kjson};window.E={ejson};window.L={ljson};{JS}</script>
</body></html>"""


def main():
    questions = load_questions(QUESTIONS_JSON_PATH)
    matches = match_questions(questions, KNOWLEDGE_POINTS)
    html = build_html(questions, KNOWLEDGE_POINTS, matches, ESSAY_QUESTIONS, LECTURE_TITLES)
    os.makedirs(os.path.dirname(OUTPUT_PATH) if os.path.dirname(OUTPUT_PATH) else '.', exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated quiz: {OUTPUT_PATH} ({len(html)} bytes)")


if __name__ == "__main__":
    main()
