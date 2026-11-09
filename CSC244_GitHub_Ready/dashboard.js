'use strict';
let selectedId = 'F-001';
let state = null;
const el = id => document.getElementById(id);
const escapeHtml = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmtMoney = n => '$'+Number(n).toLocaleString('en-US', {minimumFractionDigits:2,maximumFractionDigits:2});
const riskClass = s => (s || '').toLowerCase();
const textOr = (s, fallback) => s == null ? fallback : String(s);
const names = {'F-001':'High-risk payment','L-001':'Ordinary purchase','M-001':'Receipt missing','S-001':'Split purchase A','S-002':'Split purchase B','V-001':'New vendor'};
function toast(msg){const t=el('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3200)}
async function api(path, opts){const response=await fetch(path,opts);const data=await response.json();if(!response.ok)throw Error(data.error||'Request failed');return data}
async function load(txId=selectedId){
  selectedId=txId;
  try{state=await api('/api/dashboard?transaction_id='+encodeURIComponent(selectedId));render(state)}
  catch(err){toast('Unable to load database: '+err.message)}
}
function render(d){
  const count=d.transactions.length;
  el('sidebar-count').textContent=count;
  el('case-list').innerHTML=d.transactions.map(t=>`<button class="case-item ${selectedId===t.id?'selected':''}" data-case="${escapeHtml(t.id)}"><div><div class="case-id">${escapeHtml(t.id)}</div><div class="case-type">${escapeHtml(names[t.id]||'Transaction')}</div></div><span class="small-risk ${riskClass(t.current_risk)}">${escapeHtml(t.current_risk||'NEW')}</span></button>`).join('');
  document.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>{el('human-notes').value='';load(b.dataset.case)});
  const m=d.metrics;
  el('metrics').innerHTML=[
    {name:'TRANSACTIONS REVIEWED',value:m.transactions,foot:'Synthetic records loaded',cl:'',icon:'⛁'},
    {name:'HIGH-PRIORITY FLAGS',value:m.HIGH,foot:'Escalate to accountant',cl:'high',icon:'⚑'},
    {name:'MEDIUM-RISK FLAGS',value:m.MEDIUM,foot:'Additional review needed',cl:'medium',icon:'◇'},
    {name:'LOW-RISK CASES',value:m.LOW,foot:`${m.total_runs} audited runs · ${m.agent_assessments} votes`,cl:'low',icon:'✓'}
  ].map(a=>`<div class="metric ${a.cl}"><div class="metric-top">${a.name}<span class="metric-icon">${a.icon}</span></div><div class="metric-value">${a.value}</div><div class="metric-bottom">${escapeHtml(a.foot)}</div></div>`).join('');
  const t=d.selected, c=d.active;
  el('tx-id').textContent=t.id;
  const items=[['TRANSACTION ID',t.id],['AMOUNT',fmtMoney(t.amount)],['DEPARTMENT',t.department],['VENDOR',t.vendor_name],['EMPLOYEE ID',t.employee_id],['TIME',t.transaction_time.slice(0,16).replace('T','  ')]];
  el('transaction-detail').innerHTML=items.map(([key,value])=>`<div class="kv"><div class="kv-key">${escapeHtml(key)}</div><div class="kv-value ${key==='AMOUNT'?'amount':''}">${escapeHtml(value)}</div></div>`).join('');
  const signals=[
    [!!t.receipt_present,'Receipt available', 'Receipt missing'],
    [!!t.manager_approved,'Manager approved', 'Manager approval absent'],
    [!t.invoice_mismatch,'Invoice matches', 'Invoice mismatch'],
    [!!t.is_established,'Established vendor', 'New vendor'],
    [!t.split_suspected,'No split threshold signal', `Split-group total ${fmtMoney(t.split_total)}`],
    [!t.outside_hours,'Normal business hours', 'Outside business hours']
  ];
  el('signals').innerHTML=signals.map(([ok,yes,no])=>`<span class="signal ${ok?'good':'danger'}">${ok?'✓ ':'! '}${escapeHtml(ok?yes:no)}</span>`).join('');
  if(!c){el('consensus-detail').textContent='No review run yet.';return;}
  const nHigh=c.assessments.filter(a=>a.risk==='HIGH').length;
  el('consensus-detail').innerHTML=`<div class="risk-large"><div class="risk-circle ${riskClass(c.risk)}">${c.risk==='HIGH'?'!':c.risk==='LOW'?'✓':'?'}</div><div><div class="risk-title">${escapeHtml(c.risk)} RISK</div><div class="risk-subtitle">${escapeHtml(c.recommendation)}</div></div></div><div class="consensus-stats"><div class="consensus-stat"><div class="k">AGENT AGREEMENT</div><div class="v">${Math.round(c.agreement*100)}%</div></div><div class="consensus-stat"><div class="k">HIGH-RISK VOTES</div><div class="v">${nHigh} / 4</div></div></div><div class="recommendation"><strong>Rule:</strong> At least 3 HIGH votes trigger priority review. Other non-LOW or disputed votes trigger human review. All-LOW votes are recorded for monitoring.</div><div class="run-id" title="${escapeHtml(c.run_id)}">Audit run ID: ${escapeHtml(c.run_id)}</div>`;
  const initials={'Employee':'EM','Manager':'MG','CFO':'CF','Fraud Analysis':'FA'};
  el('agent-grid').innerHTML=c.assessments.map(a=>`<article class="agent-card"><div class="agent-top"><div style="display:flex;align-items:center;gap:7px"><div class="agent-avatar">${initials[a.role]||'AG'}</div><div class="agent-role">${escapeHtml(a.role)}</div></div><span class="agent-risk ${riskClass(a.risk)}">${escapeHtml(a.risk)}</span></div><div class="agent-meta"><span>Evidence support (heuristic)</span><strong>${Math.round(a.support_score*100)}%</strong></div><div class="score-track"><div class="score-fill" style="width:${Math.min(100,a.support_score*100)}%"></div></div><div class="agent-evidence"><b>Evidence:</b><div>${a.evidence.map(e=>escapeHtml(e)).join('<div style="margin-top:3px"></div>')}</div></div></article>`).join('');
  el('audit-log').innerHTML=c.messages.map((a,i)=>`<div class="audit-item"><div class="audit-icon">${i+1}</div><div><div class="audit-sender">${escapeHtml(a.sender_role)} → Coordinator</div><div class="audit-text">${escapeHtml(a.message)}</div><div class="audit-time">Persisted · ${escapeHtml(a.created_at.replace('T',' ').slice(0,19))} UTC</div></div></div>`).join('');
  const h=c.human_review;
  el('saved-review').innerHTML=h?`<div class="saved-review"><strong>✓ Stored accountant decision:</strong> ${escapeHtml(h.decision.replaceAll('_',' '))}<br>${escapeHtml(h.reviewer_notes||'No notes provided')}<br><small>${escapeHtml(h.reviewed_at)}</small></div>`:'<div class="muted" style="font-size:11px;margin-top:13px">No human disposition recorded for this run.</div>';
}
el('rerun-btn').addEventListener('click',async()=>{
  const btn=el('rerun-btn');btn.disabled=true;btn.textContent='Running review…';
  try{await api('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({transaction_id:selectedId})});await load();toast('New independent assessments stored in SQLite')}
  catch(err){toast('Review failed: '+err.message)}finally{btn.disabled=false;btn.textContent='↻   Run agent review'}
});
el('review-form').addEventListener('submit',async e=>{
  e.preventDefault();if(!state?.active){toast('Run an assessment first');return;}
  try{await api('/api/accountant-review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run_id:state.active.run_id,decision:el('human-decision').value,notes:el('human-notes').value})});await load();toast('Accountant decision saved to audit database')}
  catch(err){toast('Could not save: '+err.message)}
});
load();
