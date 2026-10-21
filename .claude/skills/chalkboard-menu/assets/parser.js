/* Chalkboard menu — parser and renderer.
   One parser, used by both the editor preview and the public board.
   Keep it that way: it is the seam between storage and presentation.
   When the source moves from JSON to a database, only the loader changes. */

function parseMenu(text){
  const blocks = [];
  let sec = null;

  for (const raw of String(text || '').split('\n')){
    const line = raw.trimEnd();
    if (!line.trim() || line.trim().startsWith('//')) continue;

    // an indented line describes the item above it
    const indented = /^[ \t]{2,}/.test(raw) || /^\t/.test(raw);
    const t = line.trim();

    if (indented && sec && sec.items.length){
      const last = sec.items[sec.items.length - 1];
      last.desc = last.desc ? last.desc + ' ' + t : t;
      continue;
    }
    if (t.startsWith('#')){
      blocks.push({type:'title', text:t.replace(/^#+\s*/,'')});
      sec = null; continue;
    }
    if (t.startsWith('==')){
      sec = {type:'section', name:t.replace(/^=+\s*/,'').replace(/\s*=+$/,''), items:[]};
      blocks.push(sec); continue;
    }
    if (t.startsWith('!')){
      blocks.push({type:'notice', text:t.replace(/^!\s*/,'').replace(/\s*!$/,'')});
      sec = null; continue;
    }

    // anything else is an item; an unlabelled section is created if needed
    // so a menu that opens straight into items still renders
    const [name, price] = t.split('|');
    if (!sec){ sec = {type:'section', name:'', items:[]}; blocks.push(sec); }
    sec.items.push({name:name.trim(), price:(price||'').trim(), desc:''});
  }
  return blocks;
}

function escapeHtml(s){
  return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function renderMenu(blocks, opts){
  opts = opts || {};
  if (!blocks.length){
    return '<p class="empty">' + escapeHtml(opts.emptyText || 'No menu yet.') + '</p>';
  }
  let html = '', cols = '';
  const flush = () => { if (cols){ html += '<div class="cols">' + cols + '</div>'; cols = ''; } };

  for (const b of blocks){
    if (b.type === 'title'){
      flush();
      html += '<h1 class="title">' + escapeHtml(b.text) + '</h1><div class="rule"></div>';
    } else if (b.type === 'notice'){
      flush();
      html += '<p class="notice">' + escapeHtml(b.text) + '</p>';
    } else {
      let s = '<section class="sec">';
      if (b.name) s += '<h2>' + escapeHtml(b.name) + '</h2>';
      for (const it of b.items){
        s += '<div class="item"><span class="nm">' + escapeHtml(it.name) + '</span>';
        if (it.price) s += '<span class="lead"></span><span class="pr">' + escapeHtml(it.price) + '</span>';
        s += '</div>';
        if (it.desc) s += '<p class="desc">' + escapeHtml(it.desc) + '</p>';
      }
      cols += s + '</section>';
    }
  }
  flush();

  let stamp = '';
  if (opts.updated){
    const d = new Date(opts.updated);
    const when = isNaN(d) ? opts.updated
      : d.toLocaleDateString(opts.locale || 'en-NZ', {day:'numeric', month:'short'});
    stamp = '<p class="stamp">updated ' + escapeHtml(when) + '</p>';
  }
  return '<div class="ink">' + html + stamp + '</div>';
}

/* section headings render as h2 inside .sec — match the stylesheet */
if (typeof module !== 'undefined') module.exports = {parseMenu, renderMenu, escapeHtml};
