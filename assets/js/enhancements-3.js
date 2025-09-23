(function (window, document) {
  'use strict';

  const App = {
    // Config
    config: {
      overlaySel: '#modal-overlay',
      containerSel: '#inline-content',
      modalBodySel: '.modal-body',
      closeBtnSel: '.modal-close',
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
        modalBody: q(this.config.modalBodySel, document)
      };
    },

    // Modal + content loader
    openModal() {
      this.dom.overlay.hidden = false;
      this.dom.overlay.classList.add('is-open');
      document.body.classList.add('modal-open');
      this.resetScroll();
    },

    closeModal() {
      this.dom.overlay.classList.remove('is-open');
      document.body.classList.remove('modal-open');
      this.dom.container.innerHTML = '';
      this.dom.overlay.hidden = true;
    },

    async loadIntoModal(url) {
      this.openModal();
      this.dom.container.innerHTML = '<p>Loading…</p>';
      this.resetScroll();
      try {
        const res = await fetch(url, { cache: 'no-store' });
        if (!res.ok) throw new Error(res.status + ' ' + res.statusText);
        const data = await res.text();
        this.dom.container.innerHTML = data; // Insert content as HTML
      } catch (error) {
        console.error("Error loading content:", error);
        this.dom.container.innerHTML = '<p>Failed to load content.</p>';
      }
    },

    // Event bindings
    bindLaunchers() {
      document.querySelectorAll(this.config.launcherSel).forEach(link => {
        link.addEventListener('click', (event) => {
          event.preventDefault();
          const url = link.getAttribute('data-load');
          if (url) this.loadIntoModal(url);
        });
      });
    },

    bindModalControls() {
      this.dom.overlay.addEventListener('click', (e) => {
        if (e.target === this.dom.overlay) this.closeModal();
      });
      if (this.dom.closeBtn) {
        this.dom.closeBtn.addEventListener('click', () => this.closeModal());
      }
    },

    resetScroll() {
      if (this.dom.container) this.dom.container.scrollTop = 0;
    },

    // Styles (no sticky header or columns)
    ensureStyles() {
      if (document.getElementById(this.config.injectStylesId)) return;

      const css = `
#inline-content {
  padding: 1em;
}
#inline-content p {
  margin: 0;
}
`;
      const style = document.createElement('style');
      style.id = this.config.injectStylesId;
      style.textContent = css;
      document.head.appendChild(style);
    },

    enhanceExistingAndObserve() {
      const container = this.dom.container;
      if (!container) return;

      // Watch for injected content
      const mo = new MutationObserver((mutations) => {
        for (const m of mutations) {
          m.addedNodes.forEach(node => {
            if (node.nodeType !== 1) return;
            if (node.tagName === 'TABLE') this.enhanceTable(node);
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