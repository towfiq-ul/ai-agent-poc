/* Live backend status indicator in the nav bar */
(function () {
  const dot   = document.getElementById('status-dot');
  const label = document.getElementById('status-label');

  function check() {
    fetch('/api/status/', { signal: AbortSignal.timeout(5000) })
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(data => {
        dot.className     = 'status-dot online';
        label.textContent = data.llm_provider + ' · ' + data.llm_model;

        // Update sidebar meta fields if they exist on the page
        const set = (id, val) => {
          const el = document.getElementById(id);
          if (el && val) el.textContent = val;
        };
        set('meta-embedding', data.embedding_model);
        set('meta-provider',  data.llm_provider);
        set('meta-model',     data.llm_model);
      })
      .catch(() => {
        dot.className     = 'status-dot offline';
        label.textContent = 'backend offline';
      });
  }

  check();
  setInterval(check, 30_000);
})();
