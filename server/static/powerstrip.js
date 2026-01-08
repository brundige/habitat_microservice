async function getOutletState(index) {
  const res = await fetch(`/api/powerstrip/${index}`);
  if (!res.ok) throw new Error(`Failed to fetch state: ${res.status}`);
  return await res.json();
}

async function setOutletState(index, action) {
  const res = await fetch(`/api/powerstrip/${index}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action })
  });
  if (!res.ok) throw new Error(`Failed to set state: ${res.status}`);
  return await res.json();
}

async function refreshPowerstripPanel() {
  const container = document.getElementById('powerstrip-panel');
  if (!container) return;
  const outlets = container.querySelectorAll('.outlet');
  for (const el of outlets) {
    const idx = el.dataset.index;
    el.querySelector('.state').textContent = 'loading...';
    try {
      const data = await getOutletState(idx);
      const state = data.state;
      el.querySelector('.state').textContent = state === null ? 'unknown' : (state ? 'on' : 'off');
      el.classList.toggle('on', state === true);
    } catch (e) {
      el.querySelector('.state').textContent = 'error';
      console.error(e);
    }
  }
}

async function onToggleClick(e) {
  const btn = e.currentTarget;
  const el = btn.closest('.outlet');
  const idx = el.dataset.index;
  btn.disabled = true;
  try {
    await setOutletState(idx, 'toggle');
    await refreshPowerstripPanel();
  } catch (err) {
    console.error(err);
    alert('Failed to toggle outlet: ' + err.message);
  } finally {
    btn.disabled = false;
  }
}

function wirePowerstripButtons() {
  const container = document.getElementById('powerstrip-panel');
  if (!container) return;
  container.querySelectorAll('.toggle-btn').forEach(b => b.addEventListener('click', onToggleClick));
}

window.addEventListener('DOMContentLoaded', () => {
  wirePowerstripButtons();
  refreshPowerstripPanel();
  // poll every 10 seconds
  setInterval(refreshPowerstripPanel, 10000);
});

