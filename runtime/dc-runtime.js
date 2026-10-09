/*
 * Husna preview runtime
 * ---------------------
 * Renders a .dc.html design file in an ordinary browser, so the Husna screens run on any static
 * web host (or a local server) without the Claude Design canvas.
 *
 * A .dc.html file is a template plus a small logic class:
 *
 *   <x-dc> … markup with {{holes}}, <sc-if>, <sc-for>, <dc-import> … </x-dc>
 *   <script type="text/x-dc" data-dc-script data-props='{…}'>
 *     class Component extends DCLogic { state = {…}; renderVals() { return {…}; } }
 *   </script>
 *
 * This file implements that format on top of React (loaded before it; see tools/build-support.mjs):
 *   {{ a.b }}                         dotted lookup into renderVals() and loop variables
 *   attr="{{ x }}"                    the raw value (function, boolean, number, string)
 *   attr="a {{ x }} b"                interpolated string
 *   <sc-if value="{{ cond }}">        renders its children when cond is truthy
 *   <sc-for list="{{ xs }}" as="x">   repeats its children; {{ x.field }} and {{ $index }} in scope
 *   <dc-import name="Other" p="…">    mounts the sibling file Other.dc.html, other attributes become props
 *   <helmet>                          its <link> and <style> children are moved into <head>
 *
 * Tweak props (the data-props on the script tag) can be set from the address bar when previewing:
 *   OrgProfile.dc.html?viewer=Member
 */
(function () {
  'use strict';
  if (typeof React === 'undefined' || typeof ReactDOM === 'undefined') { console.error('[husna runtime] React is not loaded'); return; }
  var h = React.createElement;

  // Hide the raw template until it is rendered.
  var hide = document.createElement('style');
  hide.textContent = 'x-dc{display:none!important}';
  document.head.appendChild(hide);

  // ------------------------------------------------------------------ a small, literal HTML reader
  // The browser's own parser moves unknown tags out of tables (<sc-for> around <tr>), so the template
  // is read from the file's text instead. Tags must be closed explicitly, which every Husna screen does.
  var VOID = { area: 1, base: 1, br: 1, col: 1, embed: 1, hr: 1, img: 1, input: 1, link: 1, meta: 1, source: 1, track: 1, wbr: 1 };
  var RAW = { script: 1, style: 1 };
  var decoder = document.createElement('textarea');
  function decode(s) { if (s.indexOf('&') < 0) return s; decoder.innerHTML = s; return decoder.value; }

  function parse(src) {
    var root = { tag: '#root', attrs: [], children: [] }, stack = [root], i = 0, n = src.length;
    var attrRe = /\s*([^\s=\/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/y;
    function top() { return stack[stack.length - 1]; }
    function text(s) { if (s) top().children.push({ text: decode(s) }); }
    while (i < n) {
      var lt = src.indexOf('<', i);
      if (lt < 0) { text(src.slice(i)); break; }
      if (lt > i) { text(src.slice(i, lt)); i = lt; }
      if (src.startsWith('<!--', i)) { var e = src.indexOf('-->', i); i = e < 0 ? n : e + 3; continue; }
      if (src[i + 1] === '/') {
        var gt = src.indexOf('>', i), name = src.slice(i + 2, gt).trim();
        for (var k = stack.length - 1; k > 0; k--) if (stack[k].tag === name) { stack.length = k; break; }
        i = gt + 1; continue;
      }
      if (!/[A-Za-z]/.test(src[i + 1] || '')) { text('<'); i += 1; continue; }
      var m = /^<([A-Za-z][\w:-]*)/.exec(src.slice(i, i + 80)), node = { tag: m[1], attrs: [], children: [] };
      i += m[0].length;
      for (;;) {
        var ws = /\s*/y; ws.lastIndex = i; ws.exec(src); i = ws.lastIndex;
        if (src[i] === '>') { i += 1; break; }
        if (src[i] === '/' && src[i + 1] === '>') { i += 2; node.selfClosed = true; break; }
        attrRe.lastIndex = i;
        var a = attrRe.exec(src);
        if (!a || a.index !== i || attrRe.lastIndex === i) { i += 1; continue; }
        var v = a[2] !== undefined ? a[2] : a[3] !== undefined ? a[3] : a[4];
        node.attrs.push({ name: a[1], value: v === undefined ? true : decode(v) });
        i = attrRe.lastIndex;
      }
      top().children.push(node);
      var lower = node.tag.toLowerCase();
      if (VOID[lower] || node.selfClosed) continue;
      if (RAW[lower]) {
        var close = src.toLowerCase().indexOf('</' + lower, i);
        if (close < 0) close = n;
        node.children.push({ text: src.slice(i, close) });
        i = src.indexOf('>', close) + 1 || n;
        continue;
      }
      stack.push(node);
    }
    return root.children;
  }

  // ------------------------------------------------------------------ holes
  var HOLE = /\{\{\s*([^}]*?)\s*\}\}/g;
  function lookup(path, scopes) {
    if (path === 'true') return true;
    if (path === 'false') return false;
    if (path === 'null') return null;
    if (path === 'undefined') return undefined;
    if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
    if (/^(['"]).*\1$/.test(path)) return path.slice(1, -1);
    var parts = path.split('.'), v, found = false;
    for (var i = scopes.length - 1; i >= 0; i--) if (scopes[i] && Object.prototype.hasOwnProperty.call(scopes[i], parts[0])) { v = scopes[i][parts[0]]; found = true; break; }
    if (!found) return undefined;
    for (var j = 1; j < parts.length && v != null; j++) v = v[parts[j]];
    return v;
  }
  /** attr="{{x}}" gives the raw value; attr="a {{x}}" gives a string; a plain attr gives itself. */
  function attrValue(raw, scopes) {
    if (raw === true || raw.indexOf('{{') < 0) return { literal: true, value: raw };
    var whole = /^\s*\{\{\s*([^}]*?)\s*\}\}\s*$/.exec(raw);
    if (whole) return { literal: false, value: lookup(whole[1], scopes) };
    return { literal: false, value: raw.replace(HOLE, function (_, p) { var v = lookup(p, scopes); return v == null || v === false ? '' : String(v); }) };
  }

  // ------------------------------------------------------------------ attributes, the way React wants them
  var RENAME = { 'class': 'className', 'for': 'htmlFor', readonly: 'readOnly', maxlength: 'maxLength', minlength: 'minLength', tabindex: 'tabIndex', colspan: 'colSpan', rowspan: 'rowSpan',
    autocomplete: 'autoComplete', autofocus: 'autoFocus', inputmode: 'inputMode', spellcheck: 'spellCheck', enterkeyhint: 'enterKeyHint', datetime: 'dateTime', crossorigin: 'crossOrigin',
    srcset: 'srcSet', novalidate: 'noValidate', contenteditable: 'contentEditable', defaultvalue: 'defaultValue', defaultchecked: 'defaultChecked', viewbox: 'viewBox' };
  var BOOL = { checked: 1, selected: 1, disabled: 1, readOnly: 1, required: 1, multiple: 1, hidden: 1, autoFocus: 1, open: 1, noValidate: 1, defaultChecked: 1 };
  var SVG = { svg: 1, path: 1, circle: 1, rect: 1, line: 1, polyline: 1, polygon: 1, ellipse: 1, g: 1, defs: 1, marker: 1, text: 1, use: 1, mask: 1, clipPath: 1, linearGradient: 1, radialGradient: 1, stop: 1 };
  function camel(s) { return s.replace(/-([a-z])/g, function (_, c) { return c.toUpperCase(); }); }
  function styleObject(s) {
    var out = {};
    String(s).split(';').forEach(function (decl) {
      var c = decl.indexOf(':'); if (c < 0) return;
      var k = decl.slice(0, c).trim(), v = decl.slice(c + 1).trim(); if (!k) return;
      out[k.indexOf('--') === 0 ? k : camel(k)] = v;
    });
    return out;
  }
  function buildProps(node, scopes) {
    var tag = node.tag.toLowerCase(), props = {};
    node.attrs.forEach(function (a) {
      if (a.name.indexOf('hint-') === 0) return;
      var name = RENAME[a.name] || RENAME[a.name.toLowerCase()] || a.name;
      if (SVG[node.tag] && name.indexOf('-') > 0 && name.indexOf('aria-') !== 0 && name.indexOf('data-') !== 0) name = camel(name);
      var r = attrValue(a.value, scopes), v = r.value;
      if (name === 'style') { if (v && typeof v === 'string') props.style = styleObject(v); else if (v && typeof v === 'object') props.style = v; return; }
      if (BOOL[name] && r.literal) v = true;                                   // checked, checked="" and checked="checked" all mean on
      if (r.literal && (tag === 'input' || tag === 'textarea')) {               // a literal starting state stays editable
        if (name === 'checked') name = 'defaultChecked';
        if (name === 'value' && tag === 'textarea') name = 'defaultValue';
        if (name === 'value' && tag === 'input') { var ty = node.attrs.filter(function (x) { return x.name === 'type'; })[0]; if (!ty || !/^(checkbox|radio|hidden|submit|button)$/.test(ty.value)) name = 'defaultValue'; }
      }
      if (v === undefined || v === null) return;
      if (v === true && !BOOL[name] && name.indexOf('aria-') !== 0 && name.indexOf('data-') !== 0 && r.literal) v = '';
      props[name] = v;
    });
    return props;
  }

  // ------------------------------------------------------------------ rendering a template
  function renderNodes(nodes, scopes, keyBase) {
    var out = [];
    for (var i = 0; i < nodes.length; i++) {
      var r = renderNode(nodes[i], scopes, keyBase + '.' + i);
      if (Array.isArray(r)) Array.prototype.push.apply(out, r); else if (r !== null && r !== undefined) out.push(r);
    }
    return out;
  }
  function renderNode(node, scopes, key) {
    if (node.text !== undefined) {
      if (node.text.indexOf('{{') < 0) return node.text;
      var parts = [], last = 0, m, n = 0; HOLE.lastIndex = 0;
      while ((m = HOLE.exec(node.text))) {
        if (m.index > last) parts.push(node.text.slice(last, m.index));
        var v = lookup(m[1], scopes);
        parts.push(h('span', { className: 'sc-interp', key: key + ':' + n++ }, v == null || v === false || v === true || typeof v === 'function' ? null : (React.isValidElement(v) ? v : String(v))));
        last = m.index + m[0].length;
      }
      if (last < node.text.length) parts.push(node.text.slice(last));
      return parts;
    }
    var tag = node.tag;
    if (tag === 'helmet') return null;
    if (tag === 'sc-if') {
      var cond = node.attrs.filter(function (a) { return a.name === 'value'; })[0];
      return cond && attrValue(cond.value, scopes).value ? renderNodes(node.children, scopes, key) : null;
    }
    if (tag === 'sc-for') {
      var la = node.attrs.filter(function (a) { return a.name === 'list'; })[0], as = (node.attrs.filter(function (a) { return a.name === 'as'; })[0] || {}).value || 'item';
      var list = la ? attrValue(la.value, scopes).value : null;
      if (!list || !list.map) return null;
      return list.map(function (item, idx) {
        var scope = { $index: idx }; scope[as] = item;
        return h(React.Fragment, { key: key + '#' + idx }, renderNodes(node.children, scopes.concat([scope]), key + '#' + idx));
      });
    }
    if (tag === 'dc-import') {
      var props = { key: key }, name = null, hint = null;
      node.attrs.forEach(function (a) {
        if (a.name === 'name') { name = a.value; return; }
        if (a.name === 'hint-size') { hint = a.value; return; }
        if (a.name.indexOf('hint-') === 0) return;
        props[camel(a.name)] = attrValue(a.value, scopes).value;
      });
      return h(Import, { key: key, file: name, hint: hint, pass: props });
    }
    var p = buildProps(node, scopes); p.key = key;
    var lower = tag.toLowerCase();
    if (VOID[lower]) return h(lower, p);
    if (lower === 'textarea') {
      var t = node.children.map(function (c) { return c.text || ''; }).join('');
      if (t && p.value === undefined && p.defaultValue === undefined) p.defaultValue = t;
      return h('textarea', p);
    }
    if (RAW[lower]) { p.dangerouslySetInnerHTML = { __html: node.children.map(function (c) { return c.text || ''; }).join('') }; return h(lower, p); }
    var kids = renderNodes(node.children, scopes, key);
    return kids.length ? h(SVG[tag] ? tag : lower, p, kids) : h(SVG[tag] ? tag : lower, p);
  }

  // ------------------------------------------------------------------ files become components
  class DCLogic extends React.Component { renderVals() { return {}; } }
  window.DCLogic = DCLogic;

  var components = {}, loading = {}, seenHead = {};
  function addToHead(nodes) {
    nodes.forEach(function (n) {
      if (!n.tag) return;
      var tag = n.tag.toLowerCase(), sig = tag + JSON.stringify(n.attrs) + (n.children[0] ? n.children[0].text : '');
      if (seenHead[sig] || (tag !== 'link' && tag !== 'style' && tag !== 'meta')) return;
      seenHead[sig] = 1;
      var el = document.createElement(tag);
      n.attrs.forEach(function (a) { el.setAttribute(a.name, a.value === true ? '' : a.value); });
      if (tag === 'style') el.textContent = n.children.map(function (c) { return c.text || ''; }).join('');
      document.head.appendChild(el);
    });
  }
  function build(name, src) {
    var body = /<x-dc>([\s\S]*)<\/x-dc>/.exec(src);
    if (!body) throw new Error(name + ': no <x-dc> block');
    var tree = parse(body[1]);
    tree.forEach(function (n) { if (n.tag === 'helmet') addToHead(n.children); });
    var template = tree.filter(function (n) { return n.tag !== 'helmet'; });
    var script = /<script\b[^>]*data-dc-script[^>]*>([\s\S]*?)<\/script>/.exec(src), code = script ? script[1] : 'class Component extends DCLogic {}';
    var Component = new Function('DCLogic', 'React', code + '\n;return Component;')(DCLogic, React);
    Component.displayName = name;
    Component.prototype.render = function () {
      var vals;
      try { vals = this.renderVals() || {}; } catch (err) { console.error('[husna runtime] ' + name + ' renderVals failed', err); vals = {}; }
      return h('div', { className: 'sc-host' }, renderNodes(template, [vals], name));
    };
    return Component;
  }
  function load(file) {
    if (components[file]) return Promise.resolve(components[file]);
    if (!loading[file]) loading[file] = fetch(new URL(file + '.dc.html', location.href).href).then(function (r) { if (!r.ok) throw new Error(file + '.dc.html: ' + r.status); return r.text(); })
      .then(function (src) { components[file] = build(file, src); return components[file]; });
    return loading[file];
  }
  class Import extends React.Component {
    constructor(props) { super(props); this.state = { C: components[props.file] || null, failed: false }; }
    componentDidMount() {
      this.alive = true;
      if (!this.state.C) load(this.props.file).then((C) => { if (this.alive) this.setState({ C: C }); }, (err) => { console.error('[husna runtime]', err); if (this.alive) this.setState({ failed: true }); });
    }
    componentWillUnmount() { this.alive = false; }
    render() {
      if (this.state.C) return h(this.state.C, this.props.pass);
      var size = String(this.props.hint || '').split(','), style = { width: (size[0] || '100%').trim(), height: (size[1] || 'auto').trim() };
      return h('div', { className: 'sc-host', style: style, 'aria-busy': this.state.failed ? undefined : 'true' });
    }
  }

  // ------------------------------------------------------------------ start
  function queryProps() {
    var out = {};
    new URLSearchParams(location.search).forEach(function (v, k) { out[k] = v === 'true' ? true : v === 'false' ? false : v; });
    return out;
  }
  function boot() {
    var self = location.pathname.split('/').pop() || 'index.html', name = decodeURIComponent(self).replace(/\.dc\.html$/, '');
    fetch(location.href.split('#')[0].split('?')[0]).then(function (r) { return r.text(); }).then(function (src) {
      var Component = build(name, src); components[name] = Component;
      var old = document.querySelector('x-dc'); if (old) old.remove();
      var root = document.createElement('div'); root.id = 'dc-root';
      document.body.insertBefore(root, document.body.firstChild);
      ReactDOM.createRoot(root).render(h(Component, queryProps()));
      if (location.hash.length > 1) setTimeout(function () { var el = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (el) el.scrollIntoView(); }, 60);
    }).catch(function (err) {
      console.error('[husna runtime]', err);
      var note = document.createElement('p');
      note.style.cssText = 'margin:40px;font:16px/1.5 system-ui,sans-serif;color:#f3f0e7;background:#14201c;padding:20px;border-radius:12px;max-width:60ch';
      note.textContent = 'This screen needs to be opened through a web server, not as a file. From the repository folder run: node tools/serve.mjs  and open http://localhost:4173';
      document.body.appendChild(note);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
