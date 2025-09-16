/* Sticky table headers (clone-based, guarded)
   - Clones each table's thead into a sticky container placed just above the table
   - Sits below .modal-bar via --modal-stick-top
   - Skips and never re-clones tables inside sticky headers
*/
(function (window, document) {
  'use strict';

  var SELECTORS = {
    container: '#inline-content',
    overlay: '#modal-overlay',
    modalBody: '.modal-body'
  };

  var tableMap = new WeakMap();
  var STICKY_WRAP_CLASS = 'sticky-head';
  var STICKY_TABLE_CLASS = 'sticky-head-table';
  var CSS_LINK_ID = 'sticky-headers-css';

  function setStickTopVar() {
    try {
      var overlay = document.querySelector(SELECTORS.overlay);
      var body = document.querySelector(SELECTORS.modalBody) || document.body;
      var bar = overlay ? overlay.querySelector('.modal-bar') : null;
      var h = bar ? bar.offsetHeight : 0;
      body.style.setProperty('--modal-stick-top', h + 'px');
    } catch (e) { /* noop */ }
  }

  function ensureThead(table) {
    if (table.tHead) return;
    var firstRow = table.querySelector('tr');
    if (!firstRow) return;
    var thead = table.createTHead();
    thead.appendChild(firstRow);
  }

  function isCloneTable(tbl) {
    return !!(tbl.classList && (tbl.classList.contains(STICKY_TABLE_CLASS) || tbl.closest('.' + STICKY_WRAP_CLASS)));
  }

  function buildStickyFor(table) {
    if (!table || isCloneTable(table)) return;
    ensureThead(table);
    if (!table.tHead) return;

    var stickyWrap = document.createElement('div');
    stickyWrap.className = STICKY_WRAP_CLASS;

    var cloneTable = document.createElement('table');
    cloneTable.className = (table.className || '') + ' ' + STICKY_TABLE_CLASS;

    var clonedHead = table.tHead.cloneNode(true);
    cloneTable.appendChild(clonedHead);
    stickyWrap.appendChild(cloneTable);

    // Insert before table
    table.parentNode.insertBefore(stickyWrap, table);

    // Forward header clicks to the original header (keeps your sorter working)
    var origHeaderCells = Array.prototype.slice.call(table.tHead.rows[0].cells);
    var cloneHeaderCells = Array.prototype.slice.call(clonedHead.rows[0].cells);
    cloneHeaderCells.forEach(function (th, i) {
      th.style.width = '';
      th.addEventListener('click', function () {
        var orig = origHeaderCells[i];
        if (orig) orig.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      });
    });

    tableMap.set(table, {
      stickyWrap: stickyWrap,
      cloneTable: cloneTable,
      clonedHead: clonedHead,
      ro: null,
      mo: null
    });

    attachObservers(table);
    // Initial sync after layout
    requestAnimationFrame(function(){ syncHeaderSize(table); });
  }

  function syncHeaderSize(table) {
    var data = tableMap.get(table);
    if (!data) return;

    var cloneTable = data.cloneTable;
    var clonedHead = data.clonedHead;

    var origHeadRow = table.tHead && table.tHead.rows[0];
    var refRow = origHeadRow || (table.tBodies[0] && table.tBodies[0].rows[0]);
    if (!refRow) return;

    var tableRect = table.getBoundingClientRect();
    cloneTable.style.width = Math.round(tableRect.width) + 'px';

    var origCells = Array.prototype.slice.call(refRow.cells);
    var cloneCells = Array.prototype.slice.call(clonedHead.rows[0].cells);

    // If column count changed, rebuild the clone head
    if (origCells.length !== cloneCells.length) {
      var newHead = table.tHead.cloneNode(true);
      clonedHead.replaceWith(newHead);
      data.clonedHead = newHead;
    }

    var headCells = Array.prototype.slice.call(cloneTable.tHead.rows[0].cells);
    var measureRow = (table.tHead && table.tHead.rows[0]) || (table.tBodies[0] && table.tBodies[0].rows[0]);
    var measureCells = Array.prototype.slice.call(measureRow ? measureRow.cells : []);

    for (var i = 0; i < headCells.length; i++) {
      var w = (measureCells[i] && measureCells[i].getBoundingClientRect().width) || 0;
      var px = Math.max(0, Math.round(w)) + 'px';
      headCells[i].style.width = px;
      headCells[i].style.minWidth = px;
      headCells[i].style.maxWidth = px;
    }
  }

  function attachObservers(table) {
    var data = tableMap.get(table);
    if (!data) return;

    if ('ResizeObserver' in window) {
      data.ro = new ResizeObserver(function () { syncHeaderSize(table); });
      data.ro.observe(table);
    } else {
      window.addEventListener('resize', function () { syncHeaderSize(table); });
    }

    data.mo = new MutationObserver(function () { syncHeaderSize(table); });
    data.mo.observe(table, { childList: true, subtree: true, attributes: true });
  }

  function detachFor(table) {
    var data = tableMap.get(table);
    if (!data) return;
    try { if (data.ro) data.ro.disconnect(); } catch(e){}
    try { if (data.mo) data.mo.disconnect(); } catch(e){}
    if (data.stickyWrap && data.stickyWrap.parentNode) {
      data.stickyWrap.parentNode.removeChild(data.stickyWrap);
    }
    tableMap.delete(table);
  }

  function scanAndAttach(root) {
    var container = root || document.querySelector(SELECTORS.container);
    if (!container) return;
    Array.prototype.forEach.call(container.querySelectorAll('table'), function(tbl) {
      if (!isCloneTable(tbl) && !tableMap.has(tbl)) buildStickyFor(tbl);
    });
  }

  function watchContainer() {
    var container = document.querySelector(SELECTORS.container);
    if (!container) return;

    var mo = new MutationObserver(function (mutations) {
      mutations.forEach(function(m){
        Array.prototype.forEach.call(m.addedNodes, function(node){
          if (node.nodeType !== 1) return;
          if (node.tagName === 'TABLE') {
            if (!isCloneTable(node)) buildStickyFor(node);
          } else {
            var tables = node.querySelectorAll ? node.querySelectorAll('table') : [];
            Array.prototype.forEach.call(tables, function(t){ if (!isCloneTable(t)) buildStickyFor(t); });
          }
        });
        Array.prototype.forEach.call(m.removedNodes, function(node){
          if (node.nodeType !== 1) return;
          if (node.tagName === 'TABLE') detachFor(node);
          else {
            var tables = node.querySelectorAll ? node.querySelectorAll('table') : [];
            Array.prototype.forEach.call(tables, detachFor);
          }
        });
      });
    });
    mo.observe(container, { childList: true, subtree: true });

    window.addEventListener('resize', setStickTopVar);

    // Re-sync widths if zoom/class changes
    var zoomObs = new MutationObserver(function () {
      setStickTopVar();
      Array.prototype.forEach.call(container.querySelectorAll('table'), function(t){ if (!isCloneTable(t)) syncHeaderSize(t); });
    });
    zoomObs.observe(container, { attributes: true, attributeFilter: ['style', 'class'] });
  }

  function ensureCssLink() {
    if (document.getElementById(CSS_LINK_ID)) return;
    var link = document.createElement('link');
    link.id = CSS_LINK_ID;
    link.rel = 'stylesheet';
    link.href = 'assets/css/sticky-headers.css';
    document.head.appendChild(link);
  }

  function init() {
    ensureCssLink();
    setStickTopVar();
    scanAndAttach();
    watchContainer();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})(window, document);