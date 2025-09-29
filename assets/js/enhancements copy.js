/* Inline modal loader + table enhancer (no sticky header)
   - Opens a full-screen modal and loads external content into #inline-content
   - Zoom controls (+/−) and "fit to width" on double-click minus
   - Table enhancement: sorting + single-select row highlight (no sticky header/columns)
*/
(function (window, document) {
  'use strict';

  const App = {
    // Config
    config: {
      overlaySel: '#modal-overlay',
      containerSel: '#inline-content',
      modalBodySel: '.modal-body',
      closeBtnSel: '.modal-close',
      zoomInBtnSel: '.zoom-in',
      zoomOutBtnSel: '.zoom-out',
      launcherSel: 'a[data-load]',

      defaultZoomPx: 9,
      minZoomPx: 4,
      maxZoomPx: 36,
      zoomStepPx: 2,

      injectStylesId: 'inline-table-enhancer-styles'
    },

    // State
    state: { zoomPx: null, inited: false },

    // Init
    init() {
      if (this.state.inited) return;
      this.state.inited = true;

      this.cacheDom();
      if (!this.dom.overlay || !this.dom.container) return;

      this.state.zoomPx = this.config.defaultZoomPx;

      this.bindLaunchers();
      this.bindModalControls();
      this.ensureStyles();

      this.enhanceExistingAndObserve();
    },

    cacheDom() {
      const q = (sel, root = document) => root.querySelector(sel);
      this.dom = {
        overlay: q(this.config.overlaySel),
        container: q(this.config.containerSel),
        closeBtn: q(this.config.closeBtnSel, document),
        zoomInBtn: q(this.config.zoomInBtnSel, document),
        zoomOutBtn: q(this.config.zoomOutBtnSel, document),
        modalBody: q(this.config.modalBodySel, document)
      };
    },

    // Modal + zoom
    applyZoom() {
      this.dom.container.style.fontSize = this.state.zoomPx + 'px';
    },

    fitToWidth() {
      const body = this.dom.modalBody || this.dom.overlay || document.body;
      let guard = 50;
      while (this.dom.container.scrollWidth > body.clientWidth &&
             this.state.zoomPx > this.config.minZoomPx && guard--) {
        this.state.zoomPx = Math.max(this.config.minZoomPx, this.state.zoomPx - 1);
        this.applyZoom();
      }
    },

    openModal() {
      this.dom.overlay.hidden = false;
      this.dom.overlay.classList.add('is-open');
      document.body.classList.add('modal-open');
      this.applyZoom();
      this.resetScroll();
    },

    closeModal() {
      this.dom.overlay.classList.remove('is-open');
      document.body.classList.remove('modal-open');
      this.dom.container.innerHTML = '';
      this.dom.container.classList.remove('as-pre');
      this.dom.overlay.hidden = true;
    },

    // Content loader
    async loadIntoModal(url) {
      this.openModal();
      this.dom.container.classList.remove('as-pre');
      this.dom.container.innerHTML = '<p>Loading…</p>';
      this.resetScroll();
      try {
        const res = await fetch(url, { cache: 'no-store' });
        if (!res.ok) throw new Error(res.status + ' ' + res.statusText);
        const txt = await res.text();
        if (/<\s*(table|thead|tbody|tr|td|th|div|span|p|ul|ol|a|h[1-6])\b/i.test(txt)) {
          // Render the content as HTML
          this.dom.container.innerHTML = txt;
        } else {
          // Render the content as plain text
          this.dom.container.classList.add('as-pre');
          this.dom.container.textContent = txt;
        }
        this.onContentInjected();
      } catch (err) {
        console.error(err);
        this.dom.container.classList.remove('as-pre');
        this.dom.container.innerHTML = '<p>Failed to load content.</p>';
      }
    },

    // Events
    bindLaunchers() {
      document.querySelectorAll(this.config.launcherSel).forEach(el => {
        el.addEventListener('click', (e) => {
          e.preventDefault();
          const url = el.getAttribute('data-load');
          if (url) this.loadIntoModal(url);
        });
      });
    },

    bindModalControls() {
      this.dom.overlay.addEventListener('click', (e) => {
        if (e.target === this.dom.overlay) this.closeModal();
      });
      if (this.dom.closeBtn) this.dom.closeBtn.addEventListener('click', () => this.closeModal());
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.dom.overlay.classList.contains('is-open')) this.closeModal();
      });

      if (this.dom.zoomInBtn) {
        this.dom.zoomInBtn.addEventListener('click', () => {
          this.state.zoomPx = Math.min(this.config.maxZoomPx, this.state.zoomPx + this.config.zoomStepPx);
          this.applyZoom();
        });
      }
      if (this.dom.zoomOutBtn) {
        this.dom.zoomOutBtn.addEventListener('click', () => {
          this.state.zoomPx = Math.max(this.config.minZoomPx, this.state.zoomPx - this.config.zoomStepPx);
          this.applyZoom();
        });
        this.dom.zoomOutBtn.addEventListener('dblclick', (e) => {
          e.preventDefault();
          this.fitToWidth();
        });
      }
    },

    resetScroll() {
      if (this.dom.modalBody) this.dom.modalBody.scrollTop = 0;
      if (this.dom.container) this.dom.container.scrollTop = 0;
    },

    onContentInjected() {
      this.resetScroll();
      requestAnimationFrame(() => this.resetScroll());
    },

    // Styles (no sticky header or columns)
    ensureStyles() {
      if (document.getElementById(this.config.injectStylesId)) return;

      const css = `
#inline-content .enhanced-table {
  border-collapse: collapse;
  width: max-content;
  table-layout: fixed;
  margin-top: 0; /* no offset */
}
#inline-content .enhanced-table th, #inline-content .enhanced-table td {
  border: 1px solid #c9c9c9;
  padding: 0.5em 0.75em;
  text-align: left;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}
/* Sort affordance */
#inline-content .enhanced-table thead th.sortable { cursor: pointer; user-select: none; }
#inline-content .enhanced-table thead th.sort-asc::after { content: " ▲"; }
#inline-content .enhanced-table thead th.sort-desc::after { content: " ▼"; }
/* Zebra + row selection */
#inline-content .enhanced-table tbody tr:nth-child(odd) { background: rgba(144,144,144,0.05); }
#inline-content .enhanced-table tbody tr.row-selected > td { background: #fff8c5; }
`;
      const style = document.createElement('style');
      style.id = this.config.injectStylesId;
      style.textContent = css;
      document.head.appendChild(style);
    },

    // Sorting helpers
    parseCellValue(text) {
      if (!text) return { n: NaN, s: '' };
      let t = text.trim();
      if (/^[.]\d/.test(t)) t = '0' + t;
      const num = t.replace(/[^\d.+-]/g, '');
      const n = num.length ? Number(num) : NaN;
      return { n, s: t.toLowerCase() };
    },

    inferNumeric(rows, colIndex) {
      let checks = 0, nums = 0;
      for (const tr of rows) {
        const cell = tr.children[colIndex];
        if (!cell) continue;
        checks++;
        const { n } = this.parseCellValue(cell.textContent || '');
        if (!Number.isNaN(n)) nums++;
        if (checks >= 12) break;
      }
      return nums >= Math.max(3, Math.ceil(checks * 0.5));
    },

    ensureThead(table) {
      if (table.tHead) return;
      const firstRow = table.querySelector('tr');
      if (!firstRow) return;
      const thead = table.createTHead();
      thead.appendChild(firstRow);
    },

    makeSortable(table) {
      this.ensureThead(table);
      const thead = table.tHead;
      const tbody = table.tBodies[0];
      if (!thead || !tbody || !thead.rows.length) return;

      const headers = Array.from(thead.rows[0].cells);
      headers.forEach((th, i) => {
        const firstCell = tbody.rows[0]?.cells[i];
        const hasOnlyInputs = firstCell && firstCell.querySelector('input,select,button');
        if (hasOnlyInputs) return;

        th.classList.add('sortable');
        th.addEventListener('click', () => {
          const rows = Array.from(tbody.rows);
          const numeric = this.inferNumeric(rows, i);

          const currentDir = th.classList.contains('sort-asc') ? 'asc'
                           : th.classList.contains('sort-desc') ? 'desc' : null;
          const nextDir = currentDir === 'asc' ? 'desc' : 'asc';

          headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
          th.classList.add(nextDir === 'asc' ? 'sort-asc' : 'sort-desc');

          const withIndex = rows.map((tr, idx) => ({ tr, idx }));
          withIndex.sort((a, b) => {
            const A = a.tr.children[i]?.textContent ?? '';
            const B = b.tr.children[i]?.textContent ?? '';
            if (numeric) {
              const { n: na } = this.parseCellValue(A);
              const { n: nb } = this.parseCellValue(B);
              const aNaN = Number.isNaN(na), bNaN = Number.isNaN(nb);
              if (aNaN && bNaN) return a.idx - b.idx;
              if (aNaN) return 1;
              if (bNaN) return -1;
              return nextDir === 'asc' ? na - nb : nb - na;
            } else {
              const sa = A.toLowerCase(), sb = B.toLowerCase();
              if (sa === sb) return a.idx - b.idx;
              return nextDir === 'asc' ? (sa < sb ? -1 : 1) : (sa > sb ? -1 : 1);
            }
          });

          const frag = document.createDocumentFragment();
          withIndex.forEach(({ tr }) => frag.appendChild(tr));
          tbody.appendChild(frag);
        });
      });
    },

    enhanceTable(table) {
      if (!table || table.classList.contains('enhanced-table')) return;
      table.classList.add('enhanced-table');
      this.makeSortable(table);
    },

    enhanceExistingAndObserve() {
      const container = this.dom.container;
      if (!container) return;

      // Enhance existing tables
      container.querySelectorAll('table').forEach((t) => this.enhanceTable(t));

      // Single-select row highlight
      container.addEventListener('click', (e) => {
        if (e.target.closest('a,button,label,select,textarea')) return;
        const cell = e.target.closest('td,th');
        if (!cell) return;
        if (cell.parentElement.parentElement.tagName === 'THEAD') return;
        const row = cell.parentElement;
        const table = row.closest('table');
        table?.querySelectorAll('tbody tr.row-selected').forEach(r => {
          if (r !== row) r.classList.remove('row-selected');
        });
        row.classList.toggle('row-selected');
      });

      // Watch for injected tables
      const mo = new MutationObserver((mutations) => {
        for (const m of mutations) {
          m.addedNodes.forEach(node => {
            if (node.nodeType !== 1) return;
            if (node.tagName === 'TABLE') this.enhanceTable(node);
            else node.querySelectorAll?.('table').forEach((t) => this.enhanceTable(t));
          });
        }
      });
      mo.observe(container, { childList: true, subtree: true });
    }
  };

  // Auto-init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init(), { once: true });
  } else {
    App.init();
  }

  // Optional global
  window.InlineModal = App;
})(window, document);

