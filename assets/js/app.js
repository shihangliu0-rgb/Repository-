/* ============================================================
 * DevBox · app.js —— 应用外壳
 * 侧边栏 / 首页 / hash 路由 / 主题切换 / 搜索 / Toast / 快捷键
 * ============================================================ */
(function () {
  'use strict';
  var D = globalThis.DevBox;
  var U = globalThis.DevUtil;

  var main = document.getElementById('main');
  var nav = document.getElementById('nav');
  var searchInput = document.getElementById('searchInput');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('overlay');
  var cleanups = [];

  /* ---------------- Toast ---------------- */
  var toastEl = document.createElement('div');
  toastEl.id = 'toast';
  document.body.appendChild(toastEl);
  var toastTimer = null;
  D.toast = function (msg, type) {
    toastEl.textContent = msg;
    toastEl.className = 'show' + (type === 'err' ? ' err' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.className = ''; }, 1800);
  };

  /* ---------------- 复制按钮 ---------------- */
  D.copyBtn = function (getText, label) {
    return U.h('button', {
      class: 'btn ghost sm copybtn',
      onclick: function () {
        var v = typeof getText === 'function' ? getText() : getText;
        U.copyText(v == null ? '' : String(v)).then(function (ok) {
          D.toast(ok ? '✓ 已复制到剪贴板' : '复制失败', ok ? undefined : 'err');
        });
      }
    }, label || '复制');
  };

  /* ---------------- 主题 ---------------- */
  var themeBtn = document.getElementById('themeBtn');
  var themeBtnTop = document.getElementById('themeBtnTop');
  function curTheme() { return document.documentElement.getAttribute('data-theme') || 'light'; }
  function toggleTheme() {
    var next = curTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('devbox.theme', next); } catch (e) {}
  }
  themeBtn.addEventListener('click', toggleTheme);
  themeBtnTop.addEventListener('click', toggleTheme);
  if (window.matchMedia) {
    try {
      matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        var saved = null;
        try { saved = localStorage.getItem('devbox.theme'); } catch (err) {}
        if (saved !== 'light' && saved !== 'dark') {
          document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
        }
      });
    } catch (e) {}
  }

  /* ---------------- 移动端菜单 ---------------- */
  var menuBtn = document.getElementById('menuBtn');
  function closeMenu() { sidebar.classList.remove('open'); overlay.hidden = true; }
  menuBtn.addEventListener('click', function () {
    sidebar.classList.toggle('open');
    overlay.hidden = !sidebar.classList.contains('open');
  });
  overlay.addEventListener('click', closeMenu);

  /* ---------------- 最近使用 ---------------- */
  function getRecent() {
    try { return JSON.parse(localStorage.getItem('devbox.recent') || '[]').filter(function (id) { return D.getTool(id); }); }
    catch (e) { return []; }
  }
  function pushRecent(id) {
    var r = [id].concat(getRecent().filter(function (x) { return x !== id; })).slice(0, 6);
    try { localStorage.setItem('devbox.recent', JSON.stringify(r)); } catch (e) {}
  }

  /* ---------------- 搜索 ---------------- */
  function matchTool(t, q) {
    if (!q) return true;
    var hay = (t.name + ' ' + t.id + ' ' + (t.desc || '') + ' ' + (t.keywords || []).join(' ')).toLowerCase();
    return q.toLowerCase().split(/\s+/).every(function (w) { return hay.indexOf(w) !== -1; });
  }

  searchInput.addEventListener('input', function () { renderNav(searchInput.value); });

  document.addEventListener('keydown', function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || '';
    if (e.key === '/' && tag !== 'INPUT' && tag !== 'TEXTAREA' && !document.activeElement.isContentEditable) {
      e.preventDefault();
      searchInput.focus();
    }
    if (e.key === 'Escape') {
      if (sidebar.classList.contains('open')) closeMenu();
      else if (document.activeElement === searchInput) { searchInput.value = ''; renderNav(''); searchInput.blur(); }
    }
  });

  /* ---------------- 侧边栏 ---------------- */
  function renderNav(query) {
    query = (query || '').trim();
    nav.innerHTML = '';
    D.categories.forEach(function (cat) {
      var items = D.tools.filter(function (t) { return t.category === cat.id && matchTool(t, query); });
      if (!items.length) return;
      var group = U.h('div', { class: 'nav-group' },
        U.h('div', { class: 'nav-group-title' }, cat.icon + ' ' + cat.name),
        items.map(function (t) {
          return U.h('a', { class: 'nav-item', href: '#/' + t.id, 'data-id': t.id },
            U.h('span', { class: 'ico' }, t.icon), t.name);
        }));
      nav.appendChild(group);
    });
    if (!nav.children.length) {
      nav.appendChild(U.h('div', { class: 'nav-empty muted' }, '没有匹配的工具'));
    }
    markActive();
  }

  function markActive() {
    var id = currentRoute();
    nav.querySelectorAll('.nav-item').forEach(function (a) {
      a.classList.toggle('active', a.getAttribute('data-id') === id);
      if (a.classList.contains('active')) a.scrollIntoView({ block: 'nearest' });
    });
  }

  /* ---------------- 首页 ---------------- */
  function renderHome(root) {
    var heroSearch = U.h('input', {
      type: 'search', placeholder: '搜索 ' + D.tools.length + ' 个工具，如：json、时间戳、二维码…',
      autocomplete: 'off',
      oninput: function () { renderGrids(heroSearch.value); }
    });

    var recent = getRecent();
    var recentSection = null;
    if (recent.length) {
      recentSection = U.h('div', { class: 'home-section' },
        U.h('h2', {}, '🕘 最近使用'),
        U.h('div', { class: 'chips' }, recent.map(function (id) {
          var t = D.getTool(id);
          return U.h('a', { class: 'chip', href: '#/' + t.id }, t.icon + ' ' + t.name);
        })));
    }

    var gridsWrap = U.h('div', {});
    root.append(
      U.h('div', { class: 'hero' },
        U.h('h1', {}, 'DevBox 开发者工具箱'),
        U.h('p', { class: 'sub' }, '17 个高频开发工具 · 纯前端本地运行 · 数据不出浏览器 · 离线可用'),
        U.h('div', { class: 'hero-search' }, heroSearch)
      ),
      recentSection,
      gridsWrap
    );

    function renderGrids(query) {
      query = (query || '').trim();
      gridsWrap.innerHTML = '';
      var any = false;
      D.categories.forEach(function (cat) {
        var items = D.tools.filter(function (t) { return t.category === cat.id && matchTool(t, query); });
        if (!items.length) return;
        any = true;
        gridsWrap.append(U.h('div', { class: 'home-section' },
          U.h('h2', {}, cat.icon + ' ' + cat.name + ' ', U.h('span', { class: 'cnt' }, String(items.length))),
          U.h('div', { class: 'cards' }, items.map(function (t) {
            return U.h('a', { class: 'card', href: '#/' + t.id },
              U.h('span', { class: 'ico' }, t.icon),
              U.h('span', {}, U.h('b', {}, t.name), U.h('span', { class: 'desc' }, t.desc || '')));
          }))));
      });
      if (!any) gridsWrap.append(U.h('div', { class: 'home-empty' }, '😅 没有找到匹配的工具'));
    }
    renderGrids('');
  }

  /* ---------------- 工具页 ---------------- */
  function renderTool(root, tool) {
    root.append(
      U.h('div', { class: 'tool-head' },
        U.h('div', { class: 'tool-icon' }, tool.icon),
        U.h('div', {},
          U.h('h1', {}, tool.name),
          U.h('p', { class: 'muted' }, tool.desc || ''))),
      (() => { var body = U.h('div', { class: 'tool-body' }); var c = tool.render(body); if (typeof c === 'function') cleanups.push(c); return body; })()
    );
  }

  /* ---------------- 路由 ---------------- */
  function currentRoute() {
    var m = location.hash.match(/^#\/([\w-]+)/);
    return m ? m[1] : '';
  }

  function render() {
    cleanups.forEach(function (fn) { try { fn(); } catch (e) {} });
    cleanups = [];
    var id = currentRoute();
    var tool = id ? D.getTool(id) : null;
    main.innerHTML = '';
    if (tool) {
      renderTool(main, tool);
      pushRecent(tool.id);
      document.title = tool.name + ' · DevBox 工具箱';
    } else {
      renderHome(main);
      document.title = 'DevBox · 开发者工具箱';
    }
    markActive();
    closeMenu();
    window.scrollTo(0, 0);
  }

  window.addEventListener('hashchange', render);
  document.getElementById('verText').textContent = 'v' + D.version + ' · ' + D.tools.length + ' 工具';
  renderNav('');
  render();
})();
