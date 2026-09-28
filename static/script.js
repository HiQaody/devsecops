// DevSecOps Generator - script.js (Docker uniquement)

function updateEnvCount() {
  const count = document.querySelectorAll('#envContainer .env-row').length;
  const el = document.getElementById('envCount');
  if (el) el.textContent = count + ' variable' + (count > 1 ? 's' : '');
}

function addRow(name = '', val = '', cred = '') {
  const container = document.getElementById('envContainer');
  const row = document.createElement('div');
  row.className = 'env-row';
  row.innerHTML = `
    <input name="env_name" type="text" class="input" placeholder="DB_HOST" value="${name}">
    <input name="env_value" type="text" class="input" placeholder="postgres.svc" value="${val}">
    <input name="secret_id" type="text" class="input" placeholder="POSTGRES_HOST_ID" value="${cred}">
    <button type="button" class="btn-remove" onclick="removeRow(this)" title="Supprimer">✕</button>
  `;
  container.appendChild(row);
  row.style.opacity = '0';
  row.style.transform = 'translateX(-12px)';
  setTimeout(() => {
    row.style.transition = 'all 0.3s ease';
    row.style.opacity = '1';
    row.style.transform = 'translateX(0)';
  }, 10);
  updateEnvCount();
}

function removeRow(btn) {
  const row = btn.closest('.env-row');
  const container = document.getElementById('envContainer');
  if (container.children.length <= 1) {
    row.querySelectorAll('input').forEach(i => i.value = '');
    return;
  }
  row.style.transition = 'all 0.25s ease';
  row.style.opacity = '0';
  row.style.transform = 'translateX(14px)';
  setTimeout(() => { row.remove(); updateEnvCount(); }, 250);
}

function clearEnv() {
  const c = document.getElementById('envContainer');
  c.innerHTML = '';
  addRow();
  updateEnvCount();
}

function addPreset() {
  addRow('DB_HOST', 'postgres.svc', 'POSTGRES_HOST_ID');
  addRow('DB_PORT', '5432', 'POSTGRES_PORT_ID');
  addRow('DB_USERNAME', 'postgres', 'POSTGRES_USER_ID');
  addRow('DB_PASSWORD', 'postgres', 'POSTGRES_PASSWORD_ID');
  addRow('BASE_URL', 'https://gateway.tsirylab.com', 'GATEWAY_URL_ID');
}

function getCredentialId(key, project) {
  const upper = key.toUpperCase();
  if (project === 'EMIT') {
    // EMIT : POSTGRES_... (DB_ -> POSTGRES_)
    if (upper.startsWith('DB_')) {
      return 'POSTGRES_' + upper.substring(3) + '_ID';
    }
    return upper + '_ID';
  } else if (project === 'ITDCMADA') {
    // ITDCMADA : DB_... (POSTGRES_ -> DB_)
    if (upper.startsWith('POSTGRES_')) {
      return 'DB_' + upper.substring(9) + '_ID';
    }
    return upper + '_ID';
  }
  // AUTO
  return upper + '_ID';
}

function clearPasteArea() {
  const area = document.getElementById('envPasteArea');
  const fileInput = document.getElementById('envFileInput');
  const result = document.getElementById('parseResult');
  if (area) area.value = '';
  if (fileInput) fileInput.value = '';
  if (result) result.innerHTML = '';
}

function parseEnvExample() {
  const area = document.getElementById('envPasteArea');
  const projectSel = document.getElementById('projectType');
  const result = document.getElementById('parseResult');
  const project = projectSel ? projectSel.value : 'AUTO';
  const content = area ? area.value : '';

  if (!content.trim()) {
    if (result) result.innerHTML = `<div class="alert alert-error"><span>❌</span><div>Aucun contenu à analyser</div></div>`;
    return;
  }

  const lines = content.split(/\r?\n/);
  const parsed = [];
  const seen = new Set();

  for (let raw of lines) {
    let line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    // Ignorer les lignes sans =
    const eqIdx = line.indexOf('=');
    if (eqIdx === -1) continue;
    let key = line.substring(0, eqIdx).trim();
    let val = line.substring(eqIdx + 1).trim();

    // Nettoyer la valeur : enlever quotes simples/doubles
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.substring(1, val.length - 1);
    }
    // Ignorer si valeur est une référence ${VAR} pure
    // On garde quand même la clé, valeur peut être vide ou ${...}
    // Normaliser la clé : enlever export, espaces
    if (key.startsWith('export ')) key = key.substring(7).trim();
    // Valider le nom
    key = key.toUpperCase();
    if (!/^[A-Z0-9_]+$/.test(key)) continue;
    if (seen.has(key)) continue;
    seen.add(key);

    // Ignorer certaines clés non pertinentes ? Pour l'instant on garde tout
    // Filtrer les clés qui sont des références TYPEORM_ etc. ? On garde

    const cred = getCredentialId(key, project);
    parsed.push({ name: key, value: val, cred: cred });
  }

  if (parsed.length === 0) {
    if (result) result.innerHTML = `<div class="alert alert-error"><span>❌</span><div>Aucune variable détectée. Vérifiez le format <code>KEY=VALUE</code></div></div>`;
    return;
  }

  // Vider et remplir le tableau
  const container = document.getElementById('envContainer');
  container.innerHTML = '';
  parsed.forEach(p => addRow(p.name, p.value, p.cred));

  // Message de succès avec détail du mapping
  const detail = parsed.slice(0, 5).map(p => `<code>${p.name}</code> → <code>${p.cred}</code>`).join(', ') + (parsed.length > 5 ? ` +${parsed.length - 5} autres` : '');
  if (result) {
    const projLabel = project === 'EMIT' ? 'EMIT (POSTGRES_...)' : project === 'ITDCMADA' ? 'ITDCMADA (DB_...)' : 'AUTO';
    result.innerHTML = `<div class="alert alert-success"><span>✅</span><div><strong>${parsed.length} variables détectées</strong> — Projet: <b>${projLabel}</b><br><small>${detail}</small></div></div>`;
  }
  updateEnvCount();
}

function copyCode(id) {
  const el = document.getElementById(id);
  const text = el.textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = event.target.closest('button');
    const old = btn.textContent;
    btn.textContent = '✅ Copié !';
    setTimeout(() => btn.textContent = old, 1500);
  }).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); ta.remove();
    alert('Copié !');
  });
}

function downloadFile(id, filename) {
  const el = document.getElementById(id);
  const text = el.textContent;
  const blob = new Blob([text], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function downloadAll() {
  downloadFile('dockerfileCode', 'Dockerfile');
  setTimeout(() => downloadFile('jenkinsfileCode', 'Jenkinsfile'), 300);
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('genForm');
  const loading = document.getElementById('loading');
  const result = document.getElementById('result');
  const submitBtn = document.getElementById('submitBtn');
  const previewSection = document.getElementById('previewSection');

  updateEnvCount();

  // Gestion fichier .env.example -> textarea
  const fileInput = document.getElementById('envFileInput');
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const area = document.getElementById('envPasteArea');
        if (area) area.value = ev.target.result;
      };
      reader.readAsText(file);
    });
  }

  // Placeholder anime
  const imageInput = document.querySelector('input[name="name_images"]');
  if (imageInput) {
    const placeholders = ['mon-app-backend', 'service-auth', 'api-gateway', 'matac', 'servicetsena'];
    let idx = 0;
    setInterval(() => {
      if (imageInput.value === '' && document.activeElement !== imageInput) {
        imageInput.placeholder = placeholders[idx];
        idx = (idx + 1) % placeholders.length;
      }
    }, 2000);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    result.innerHTML = '';
    previewSection.classList.add('hidden');
    loading.classList.add('show');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Génération...';

    const imageName = form.name_images.value.trim().toLowerCase().replace(/\s+/g, '-');
    const port = form.port_container.value.trim();

    const rows = document.querySelectorAll('#envContainer .env-row');
    const envs = [];
    let hasError = false;

    rows.forEach(row => {
      const name = row.querySelector('input[name="env_name"]').value.trim();
      const value = row.querySelector('input[name="env_value"]').value.trim();
      const secret_id = row.querySelector('input[name="secret_id"]').value.trim();
      if (!name && !value && !secret_id) return;
      if (name) {
        if (!/^[A-Z0-9_]+$/.test(name)) {
          hasError = true;
          row.querySelector('input[name="env_name"]').style.borderColor = '#ef4444';
        } else {
          row.querySelector('input[name="env_name"]').style.borderColor = '';
        }
        envs.push({
          name: name.toUpperCase(),
          value: value,
          secret_id: secret_id || name + '_ID'
        });
      }
    });

    if (hasError) {
      loading.classList.remove('show');
      submitBtn.disabled = false;
      submitBtn.textContent = '🎯 Générer Dockerfile & Jenkinsfile';
      result.innerHTML = `<div class="alert alert-error"><span>❌</span><div><strong>Erreur :</strong> Les noms de variables doivent être en MAJUSCULES (ex: DB_HOST)</div></div>`;
      return;
    }

    if (!imageName || !port) {
      loading.classList.remove('show');
      submitBtn.disabled = false;
      submitBtn.textContent = '🎯 Générer Dockerfile & Jenkinsfile';
      result.innerHTML = `<div class="alert alert-error"><span>❌</span><div><strong>Champs requis manquants</strong></div></div>`;
      return;
    }

    try {
      const payload = {
        app_name: imageName,
        name_images: imageName,
        image_name: imageName,
        port: port,
        port_container: port,
        envs: envs
      };

      const res = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      loading.classList.remove('show');
      submitBtn.disabled = false;
      submitBtn.textContent = '🎯 Générer Dockerfile & Jenkinsfile';

      if (data.success) {
        result.innerHTML = `
          <div class="alert alert-success">
            <span>✅</span>
            <div>
              <strong>Succès !</strong> ${data.message}<br>
              <code>generated/${imageName}/</code> → Dockerfile + Jenkinsfile <b>🐳 Docker</b> (docker build → docker run)
            </div>
          </div>`;

        const dockerEl = document.getElementById('dockerfileCode');
        const jenkinsEl = document.getElementById('jenkinsfileCode');
        if (dockerEl) dockerEl.textContent = data.dockerfile || '—';
        if (jenkinsEl) jenkinsEl.textContent = data.jenkinsfile || '—';

        previewSection.classList.remove('hidden');
        previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        window._lastDockerfile = data.dockerfile;
        window._lastJenkinsfile = data.jenkinsfile;
      } else {
        result.innerHTML = `<div class="alert alert-error"><span>❌</span><div><strong>Erreur :</strong> ${data.message}</div></div>`;
      }
    } catch (err) {
      loading.classList.remove('show');
      submitBtn.disabled = false;
      submitBtn.textContent = '🎯 Générer Dockerfile & Jenkinsfile';
      result.innerHTML = `<div class="alert alert-error"><span>❌</span><div><strong>Erreur réseau :</strong> Impossible de contacter le serveur Flask (python app.py)</div></div>`;
    }
  });
});
