(function (window, document) {
  'use strict';

  const SELECTORS = {
    modalBody: '.modal-body',
    inlineContent: '#inline-content',
  };

  function makeHeaderSticky(table) {
    const thead = table.querySelector('thead');
    if (!thead) return;

    // Apply sticky styles to the header row
    thead.style.position = 'sticky';
    thead.style.top = '0'; // Adjust this value if you want to offset it below the modal bar
    thead.style.zIndex = '2';
    thead.style.background = 'inherit'; // Ensure it matches the table's background
    thead.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)'; // Optional: Add a shadow for better visibility
  }

  function enhanceTableWithStickyHeader() {
    const inlineContent = document.querySelector(SELECTORS.inlineContent);
    if (!inlineContent) return;

    const table = inlineContent.querySelector('table');
    if (table) {
      makeHeaderSticky(table);
    }
  }

  function observeModalContent() {
    const modalBody = document.querySelector(SELECTORS.modalBody);
    if (!modalBody) return;

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1 && node.tagName === 'TABLE') {
            // Enhance only newly added tables
            makeHeaderSticky(node);
          }
        });
      });
    });

    observer.observe(modalBody, { childList: true, subtree: true });
  }

  function initStickyHeaders() {
    observeModalContent();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initStickyHeaders);
  } else {
    initStickyHeaders();
  }
})(window, document);