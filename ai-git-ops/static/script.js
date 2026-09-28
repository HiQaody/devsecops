function addEnvRow(name="", val="", cred=""){
  const c=document.getElementById('envContainer');
  const row=document.createElement('div');
  row.className='env-row';
  row.innerHTML=`<input class="input" placeholder="DB_HOST" value="${name}"><input class="input" placeholder="valeur" value="${val}"><input class="input" placeholder="Credential ID" value="${cred}"><button class="btn-remove" onclick="this.parentElement.remove()">✕</button>`;
  c.appendChild(row);
}
addEnvRow("DB_HOST","postgres.svc","POSTGRES_HOST_ID");
addEnvRow("DB_PORT","5432","POSTGRES_PORT_ID");

let lastAnalyzeData=null;

async function analyze(){
  const github_url=document.getElementById('github_url').value.trim();
  const token=document.getElementById('token').value.trim();
  const port=document.getElementById('port').value.trim()||"3000";
  const result=document.getElementById('analyzeResult');
  const loading=document.getElementById('loading');
  const genSection=document.getElementById('genSection');
  if(!github_url){ result.innerHTML=`<div class="alert alert-err">❌ URL GitHub requise</div>`; return; }
  result.innerHTML=""; genSection.classList.add("hidden");
  loading.classList.add("show");
  document.getElementById('btnAnalyze').disabled=true;
  try{
    const res=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({github_url,token,port})});
    const data=await res.json();
    loading.classList.remove("show");
    document.getElementById('btnAnalyze').disabled=false;
    if(!data.success){ result.innerHTML=`<div class="alert alert-err">❌ ${data.message}</div>`; return; }
    lastAnalyzeData=data.data;
    renderAnalyze(data.data, port);
    genSection.classList.remove("hidden");
    // préremplir app_name
    if(!document.getElementById('app_name').value){
      document.getElementById('app_name').value=data.data.repo.split('/')[1].toLowerCase();
    }
  }catch(e){
    loading.classList.remove("show");
    document.getElementById('btnAnalyze').disabled=false;
    result.innerHTML=`<div class="alert alert-err">❌ Erreur réseau: ${e.message}</div>`;
  }
}

function renderAnalyze(d, port){
  const c=document.getElementById('analyzeResult');
  const docker=d.dockerfile;
  const a=d.analysis;
  let html=`<div class="card"><h4>📦 Repo: ${d.repo} <span style="font-weight:400;color:#6b7280">(${d.branch} • ${d.language||'?'})</span></h4>`;
  html+=`<div style="font-size:.8rem;color:#6b7280">Fichiers racine: ${d.file_list.slice(0,12).join(', ')||'(vide)'} </div></div>`;

  if(docker.found){
    const scoreCls=a.score>=80?'ok':a.score>=50?'warn':'err';
    html+=`<div class="card"><h4>🐳 Dockerfile: <code>${docker.path}</code> — ${a.technology} <span style="margin-left:auto" class="score ${scoreCls}">${a.score}/100</span></h4>`;
    html+=`<div class="alert ${a.compliant?'alert-ok':'alert-warn'}">${a.compliant?'✅ Conforme':'⚠️ '+a.summary} — ${a.critical_failed} erreurs critiques</div>`;
    html+=a.checks.map(ch=>`<div class="check"><div class="dot ${ch.ok?'ok':ch.severity==='critical'?'err':'warn'}"></div><div><b>${ch.rule}</b> — ${ch.detail}</div></div>`).join('');
    html+=`<details style="margin-top:10px"><summary style="cursor:pointer;font-weight:700;font-size:.82rem">Voir Dockerfile (${docker.lines} lignes)</summary><pre class="code">${escapeHtml(docker.content_preview)}${docker.content_preview.length>=2500?'\\n...':''}</pre></details>`;
    html+=`</div>`;
  } else {
    html+=`<div class="alert alert-warn">⚠️ Aucun Dockerfile trouvé à la racine (<code>Dockerfile</code>, <code>docker/Dockerfile</code>). Le générateur va créer un Dockerfile Node par défaut + Jenkinsfile.</div>`;
  }
  c.innerHTML=html;
}

async function generateJenkins(){
  const mode=document.querySelector('input[name="mode"]:checked').value;
  const github_url=document.getElementById('github_url').value.trim();
  const app_name=document.getElementById('app_name').value.trim();
  const port=document.getElementById('port').value.trim()||"3000";
  const node_port=document.getElementById('node_port').value.trim()||"30130";
  const rows=document.querySelectorAll('#envContainer .env-row');
  const envs=[];
  rows.forEach(r=>{
    const inputs=r.querySelectorAll('input');
    const n=inputs[0].value.trim();
    if(n) envs.push({name:n, value:inputs[1].value.trim(), secret_id:inputs[2].value.trim()});
  });
  const out=document.getElementById('jenkinsResult');
  out.innerHTML=`<div class="loading show"><div class="spinner"></div><span>Génération Jenkinsfile (${mode})...</span></div>`;
  try{
    const res=await fetch('/api/generate-jenkinsfile',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode,github_url,app_name,port,node_port,envs})});
    const data=await res.json();
    if(!data.success){ out.innerHTML=`<div class="alert alert-err">❌ ${data.message}</div>`; return; }
    const label=mode==='k3s'?'☸️ K3s (kubectl apply)':'🐳 Docker run';
    out.innerHTML=`<div class="alert alert-ok">✅ Jenkinsfile généré — <b>${label}</b> — <code>${data.app_name}</code> — port ${port}${mode==='k3s'?' / NodePort '+node_port:''}</div>
      <div style="display:flex;gap:8px;margin:10px 0"><button class="btn-add" onclick="copyJenkins()">📋 Copier</button><button class="btn-add" style="background:linear-gradient(135deg,#0f172a,#334155)" onclick="downloadJenkins('${data.app_name}')">⬇️ Télécharger Jenkinsfile</button></div>
      <pre class="code" id="jenkinsCode">${escapeHtml(data.jenkinsfile)}</pre>`;
    window._lastJenkins=data.jenkinsfile;
    window._lastApp=data.app_name;
  }catch(e){
    out.innerHTML=`<div class="alert alert-err">❌ ${e.message}</div>`;
  }
}
function copyJenkins(){
  const t=document.getElementById('jenkinsCode').textContent;
  navigator.clipboard.writeText(t).then(()=>alert('Copié !'));
}
function downloadJenkins(app){
  const t=window._lastJenkins||document.getElementById('jenkinsCode').textContent;
  const blob=new Blob([t],{type:'text/plain'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='Jenkinsfile'; a.click();
}
function escapeHtml(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
