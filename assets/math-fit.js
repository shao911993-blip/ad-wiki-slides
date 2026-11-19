/* ==========================================================================
   視覺異常檢測論文筆記站 — 共用數學公式渲染與自動縮字級腳本 (assets/math-fit.js)
   規範：KaTeX 渲染完成後，檢查每個 .katex-display 是否超出容器寬度；
         若超出則自動縮小該條公式字級（最小至 0.5em），不拆行、不左右捲動，
         並於視窗大小改變時重新計算。放得下的公式維持原本大小。
   ========================================================================== */

(function () {
  var MIN_FONT_EM = 0.5;
  var MATH_DELIMITERS = [
    { left: '$$', right: '$$', display: true },
    { left: '\\[', right: '\\]', display: true },
    { left: '$', right: '$', display: false },
    { left: '\\(', right: '\\)', display: false }
  ];

  function getContentWidth(el) {
    if (!el) return 0;
    var cs = window.getComputedStyle(el);
    var padL = parseFloat(cs.paddingLeft) || 0;
    var padR = parseFloat(cs.paddingRight) || 0;
    return Math.max(0, el.clientWidth - padL - padR);
  }

  function fitDisplayMath() {
    // 1. 檢查每個獨立區塊公式 (.katex-display)
    var displays = document.querySelectorAll('.katex-display');
    displays.forEach(function (el) {
      el.style.fontSize = '';
      var katexEl = el.querySelector('.katex');
      if (!katexEl) return;

      var availWidth = getContentWidth(el);
      if (availWidth <= 0) return;

      var mathWidth = Math.max(
        katexEl.scrollWidth || 0,
        katexEl.getBoundingClientRect().width || 0
      );

      if (mathWidth > availWidth) {
        var ratio = (availWidth / mathWidth) * 0.99;
        var scale = Math.max(MIN_FONT_EM, Math.floor(ratio * 1000) / 1000);
        el.style.fontSize = scale + 'em';
      }
    });

    // 2. 檢查較長的行內公式 (.katex) 在窄螢幕或表格內是否單獨超出容器寬度
    var allK = document.querySelectorAll('.katex');
    var inlines = [];
    allK.forEach(function (katexEl) {
      if (!katexEl.closest('.katex-display')) {
        inlines.push(katexEl);
      }
    });

    // 先暫時隱藏行內公式以量測父容器真實可用寬度（避免公式撐開表格或清單）
    inlines.forEach(function (katexEl) {
      katexEl.style.fontSize = '';
      katexEl.style.display = 'none';
    });

    var inlineAvail = inlines.map(function (katexEl) {
      var parent = katexEl.parentElement;
      while (parent && window.getComputedStyle(parent).display === 'inline') {
        parent = parent.parentElement;
      }
      return getContentWidth(parent);
    });

    inlines.forEach(function (katexEl, idx) {
      katexEl.style.display = '';
      var availWidth = inlineAvail[idx];
      if (availWidth <= 0) return;

      var mathWidth = Math.max(
        katexEl.scrollWidth || 0,
        katexEl.getBoundingClientRect().width || 0
      );

      if (mathWidth > availWidth) {
        var ratio = (availWidth / mathWidth) * 0.98;
        var scale = Math.max(MIN_FONT_EM, Math.floor(ratio * 1000) / 1000);
        katexEl.style.fontSize = scale + 'em';
      }
    });
  }

  function initMath() {
    if (typeof renderMathInElement === 'function' && !document.querySelector('.katex')) {
      renderMathInElement(document.body, { delimiters: MATH_DELIMITERS });
    }
    fitDisplayMath();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMath);
  } else {
    initMath();
  }

  window.addEventListener('load', fitDisplayMath);
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(fitDisplayMath);
  }

  var resizeRaf = null;
  window.addEventListener('resize', function () {
    if (resizeRaf) cancelAnimationFrame(resizeRaf);
    resizeRaf = requestAnimationFrame(fitDisplayMath);
  });

  window.fitDisplayMath = fitDisplayMath;
})();
