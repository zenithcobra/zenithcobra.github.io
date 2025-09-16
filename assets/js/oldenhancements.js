/* Inline modal loader + table enhancer
   - Opens a full-screen modal and loads external content into #inline-content
   - Provides zoom controls (+/−) and "fit to width" on double-click minus
   - Enhances tables: sticky header, sorting, single-select row highlight
   - Optional sticky first two columns (config.stickyColumns)
*/
(function (window, document) {
  'use strict';

  const App = {
    // ===== Configuration (change to taste) =====
    config: {
      // Selectors inside your modal
      overlaySel: '#modal-overlay',
      containerSel: '#inline-content',
      modalBodySel: '.modal-body',
      closeBtnSel: '.modal-close',
      zoomInBtnSel: '.zoom-in',
      zoomOutBtnSel: '.zoom-out',

      // Links that should load content into the modal
      launcherSel: 'a[data-load]',

      // Zoom settings (font-size applied to #inline-content)
      defaultZoomPx: 8, // make smaller/larger by changing this
      minZoomPx: 4,
      maxZoomPx: 36,
      zoomStepPx: 2,

      // Table features
      stickyColumns: false, // set true to keep first two columns sticky
      injectStylesId: 'inline-table-enhancer-styles'
    },

    // ===== State =====
    state: {
      zoomPx: null,
      inited: false
    },

    // ===== Init =====
    init() {
      if (this.state.inited) return;
      this.state.inited = true;

      this.cacheDom();
      if (!this.dom.overlay || !this.dom.container) return;

      this.state.zoomPx = this.config.defaultZoomPx;

      this.bindLaunchers();
      this.bindModalControls();
      this.ensureStyles();
      this.updateStickTop();

      // Enhance any existing tables now, then watch for injected content
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

    // ===== Modal open/close + zoom =====
    applyZoom() {
      this.dom.container.style.fontSize = this.state.zoomPx + 'px';
      // Changing font size can affect sticky header offset; recompute
      this.updateStickTop();
    },

    fitToWidth() {
      // Shrink font until content width fits the modal body (or min)
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

    // ===== Content loader =====
    async loadIntoModal(url) {
      this.openModal();
      this.dom.container.classList.remove('as-pre');
      this.dom.container.innerHTML = '<p>Loading…</p>';
      this.resetScroll(); // keep at top while loading
      try {
        const res = await fetch(url, { cache: 'no-store' });
        if (!res.ok) throw new Error(res.status + ' ' + res.statusText);
        const txt = await res.text();
        if (/<\s*(table|thead|tbody|tr|td|th|div|span|p|ul|ol)\b/i.test(txt)) {
          this.dom.container.innerHTML = txt;
        } else {
          this.dom.container.classList.add('as-pre');
          this.dom.container.textContent = txt;
        }
        this.onContentInjected(); // adjust after injection
      } catch (err) {
        console.error(err);
        this.dom.container.classList.remove('as-pre');
        this.dom.container.innerHTML = '<p>Failed to load content.</p>';
      }
    },

    // ===== Event wiring =====
    bindLaunchers() {
      // Called once at init: bind all a[data-load] to open and fetch content
      document.querySelectorAll(this.config.launcherSel).forEach(el => {
        el.addEventListener('click', (e) => {
          e.preventDefault();
          const url = el.getAttribute('data-load');
          if (url) this.loadIntoModal(url);
        });
      });
    },

    bindModalControls() {
      // Backdrop click closes modal
      this.dom.overlay.addEventListener('click', (e) => {
        if (e.target === this.dom.overlay) this.closeModal();
      });

      // Close button and Esc
      if (this.dom.closeBtn) this.dom.closeBtn.addEventListener('click', () => this.closeModal());
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.dom.overlay.classList.contains('is-open')) {
          this.closeModal();
        }
      });

      // Zoom controls (+/−)
      if (this.dom.zoomInBtn) {
        this.dom.zoomInBtn.addEventListener('click', () => {
          this.state.zoomPx = Math.min(this.config.maxZoomPx, this.state.zoomPx + this.config.zoomStepPx);
          this.applyZoom();
        });
      }
      if (this.dom.zoomOutBtn) {
        // Single click: step down
        this.dom.zoomOutBtn.addEventListener('click', () => {
          this.state.zoomPx = Math.max(this.config.minZoomPx, this.state.zoomPx - this.config.zoomStepPx);
          this.applyZoom();
        });
        // Double-click: fit to width
        this.dom.zoomOutBtn.addEventListener('dblclick', (e) => {
          e.preventDefault();
          this.fitToWidth();
        });
      }

      // Recompute sticky header offset on resize (modal bar height may change)
      window.addEventListener('resize', () => this.updateStickTop());
    },

    // ===== Sticky header offset (keeps table header below the modal top bar) =====
    updateStickTop() {
      const overlay = this.dom.overlay;
      const bar = overlay ? overlay.querySelector('.modal-bar') : null;
      const body = this.dom.modalBody || document.body;
      const h = bar ? bar.offsetHeight : 0;
      body.style.setProperty('--stick-top', h + 'px');
      body.style.setProperty('--stick-gap', '12px'); // add a small gap below bar
    },
    resetScroll() {
      if (this.dom.modalBody) this.dom.modalBody.scrollTop = 0;
      if (this.dom.container) this.dom.container.scrollTop = 0;
    },
    onContentInjected() {
      this.updateStickTop();
      this.resetScroll();                  // immediately
      requestAnimationFrame(() => this.resetScroll()); // after layout
    },
    // ===== Table enhancement (styles + sorting + (optional) sticky columns + row highlight) =====
    // ...existing code...
    ensureStyles() {
      if (document.getElementById(this.config.injectStylesId)) return;

      const css = `
    #inline-content .enhanced-table {
      border-collapse: collapse;
      width: max-content;
      table-layout: fixed;
      /* Add a small top offset so the table sits below the modal bar */
      margin-top: var(--stick-gap, 8px);
    }
    #inline-content .enhanced-table th, #inline-content .enhanced-table td {
      border: 1px solid #c9c9c9;
      padding: 0.5em 0.75em;
      text-align: left;
      white-space: normal;
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    /* Sticky header sits below modal bar + small gap */
    #inline-content .enhanced-table thead th {
      position: sticky;
      top: calc(var(--stick-top, 0px) + var(--stick-gap, 8px));
      z-index: 2;
      background: #fff;
      /* Stronger bottom divider to separate header from rows while scrolling */
      box-shadow: 0 2px 0 rgba(0,0,0,0.08);
    }
    #inline-content .enhanced-table thead th.sortable { cursor: pointer; user-select: none; }
    #inline-content .enhanced-table thead th.sort-asc::after { content: " ▲"; }
    #inline-content .enhanced-table thead th.sort-desc::after { content: " ▼"; }
    #inline-content .enhanced-table tbody tr:nth-child(odd) { background: rgba(144,144,144,0.05); }
    #inline-content .enhanced-table tbody tr.row-selected > td { background: #fff8c5; }
    `;
      const style = document.createElement('style');
      style.id = this.config.injectStylesId;
      style.textContent = css;
      document.head.appendChild(style);
    },
    // ...existing code...

    // Convert text to numeric/string keys for sorting
    parseCellValue(text) {
      if (!text) return { n: NaN, s: '' };
      let t = text.trim();
      if (/^[.]\d/.test(t)) t = '0' + t; // ".333" -> "0.333"
      const num = t.replace(/[^\d.+-]/g, ''); // strip non-numeric (keep . + - digits)
      const n = num.length ? Number(num) : NaN;
      return { n, s: t.toLowerCase() };
    },

    inferNumeric(rows, colIndex) {
      // Sample a few rows to decide if the column is numeric
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
        // Skip columns where first data row has only inputs/controls (e.g., checkbox column)
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

          // Update header indicator
          headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
          th.classList.add(nextDir === 'asc' ? 'sort-asc' : 'sort-desc');

          // Sort with stability
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

          // Re-append in new order
          const frag = document.createDocumentFragment();
          withIndex.forEach(({ tr }) => frag.appendChild(tr));
          tbody.appendChild(frag);
        });
      });
    },

    setFrozenOffsets(table) {
      if (!this.config.stickyColumns) return;
      const firstRow = table.querySelector('tr');
      const c1 = firstRow?.children[0];
      if (!c1) return;
      const w1 = c1.getBoundingClientRect().width;
      table.style.setProperty('--c1w', w1 + 'px');
    },

    observeResize(table) {
      if (!this.config.stickyColumns) return;
      if (!('ResizeObserver' in window)) {
        window.addEventListener('resize', () => this.setFrozenOffsets(table));
        return;
      }
      const ro = new ResizeObserver(() => this.setFrozenOffsets(table));
      ro.observe(table);
    },

    enhanceTable(table) {
        if (!table || table.classList.contains('enhanced-table')) return;
        table.classList.add('enhanced-table');
        this.makeSortable(table);
      },

    enhanceExistingAndObserve() {
      const container = this.dom.container;
      if (!container) return;

      // 1) Enhance any existing tables (called once at init)
      container.querySelectorAll('table').forEach((t) => this.enhanceTable(t));

      // 2) Single-select row highlight (toggle selected row on click)
      container.addEventListener('click', (e) => {
        // Ignore clicks on interactive controls/links
        if (e.target.closest('a,button,label,select,textarea')) return;
        const cell = e.target.closest('td,th');
        if (!cell) return;
        if (cell.parentElement.parentElement.tagName === 'THEAD') return; // skip header
        const row = cell.parentElement;
        const table = row.closest('table');
        // Clear selection in the same table
        table?.querySelectorAll('tbody tr.row-selected').forEach(r => {
          if (r !== row) r.classList.remove('row-selected');
        });
        // Toggle current row
        row.classList.toggle('row-selected');
      });

      // 3) Watch for injected content and enhance future tables
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
      
      // Recompute sticky header offset when container style/class changes (e.g., zoom)
      const zoomObserver = new MutationObserver(() => {
        this.updateStickTop();
      });
      zoomObserver.observe(container, { attributes: true, attributeFilter: ['style', 'class'] });
    }
  };

  // Auto-init on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init(), { once: true });
  } else {
    App.init();
  }

  // Expose for optional manual control (e.g., InlineModal.loadIntoModal(url))
  window.InlineModal = App;
})(window, document);