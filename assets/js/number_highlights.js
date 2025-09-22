// Number highlighting
// old
// document.addEventListener('DOMContentLoaded', function () {
//     const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
//     let node;
//     while ((node = walker.nextNode())) {
//         const parent = node.parentNode;
//         if (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE') continue;

//         const replacedHTML = node.nodeValue.replace(/(\\d+)/g, '<span class="number-highlight">$1</span>');
//         if (replacedHTML !== node.nodeValue) {
//             const tempDiv = document.createElement('div');
//             tempDiv.innerHTML = replacedHTML;

//             while (tempDiv.firstChild) {
//                 parent.insertBefore(tempDiv.firstChild, node);
//             }
//             parent.removeChild(node);
//         }
//     }
// });
// new
// Number highlighting (safe, no innerHTML)
document.addEventListener('DOMContentLoaded', () => {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  const skipTags = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'NOSCRIPT']);

  let node;
  while ((node = walker.nextNode())) {
    const parent = node.parentNode;
    if (!parent || skipTags.has(parent.tagName)) continue;
    if (parent.closest && parent.closest('.number-highlight')) continue;

    const text = node.nodeValue;
    const regex = /(\d+)/g; // match digits
    let last = 0, hasMatch = false;

    const frag = document.createDocumentFragment();
    for (const m of text.matchAll(regex)) {
      hasMatch = true;
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      const span = document.createElement('span');
      span.className = 'number-highlight';
      span.textContent = m[1];
      frag.appendChild(span);
      last = m.index + m[0].length;
    }
    if (!hasMatch) continue;
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));

    parent.insertBefore(frag, node);
    parent.removeChild(node);
  }
});