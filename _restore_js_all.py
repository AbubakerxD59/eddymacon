#!/usr/bin/env python3
"""Restore all PHP-backed frontend patches onto the original minified bundle.

After a successful restore from a pristine bundle, also run:
  python3 _patch_books.py
to add Books CRUD (admin nav + public sale links).
"""
from pathlib import Path
import re
import subprocess
import sys

path = Path("/Applications/MAMP/htdocs/eddymacon/assets/index-Bpoe2-CA.js")
data = path.read_text(encoding="utf-8")

ADMIN_PREFIX = '(/\\\\/admin(?:\\\\/index\\\\.php)?$/.test((location.pathname||"").replace(/\\\\/+$/,""))?"../":"")'
# In the actual JS file we need single backslashes for regex:
URL_PREFIX = '(/\\/admin(?:\\/index\\.php)?$/.test((location.pathname||"").replace(/\\/+$/,""))?"../":"")'


def check(label):
    path.write_text(data, encoding="utf-8")
    r = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"PARSE FAIL after {label}:", r.stderr[-400:])
        sys.exit(1)
    print(f"OK {label}")


def must_replace(old, new, label, count=1):
    global data
    found = data.count(old)
    if found < count:
        raise SystemExit(f"{label}: expected {count}, found {found}\nOLD[:120]={old[:120]!r}")
    data = data.replace(old, new, count if count != -1 else found)
    print(f"  {label}")


# SVG icons (compact, shared)
MAIL = (
    'x.jsx("svg",{xmlns:"http://www.w3.org/2000/svg",width:18,height:18,viewBox:"0 0 24 24",fill:"none",'
    'stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round",className:"shrink-0",'
    'children:[x.jsx("rect",{width:20,height:16,x:2,y:4,rx:2}),x.jsx("path",{d:"m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"})]})'
)
PHONE = (
    'x.jsx("svg",{xmlns:"http://www.w3.org/2000/svg",width:18,height:18,viewBox:"0 0 24 24",fill:"none",'
    'stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round",className:"shrink-0",'
    'children:x.jsx("path",{d:"M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"})})'
)
WA = (
    'x.jsx("svg",{xmlns:"http://www.w3.org/2000/svg",width:18,height:18,viewBox:"0 0 24 24",fill:"currentColor",className:"shrink-0",'
    'children:x.jsx("path",{d:"M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"})})'
)

# ---------------------------------------------------------------------------
# 1) Helpers: emTimeAgo + emAsset before e_
# ---------------------------------------------------------------------------
old_e = 'e_=({content:s,onSave:n,inquiries:l,onDeleteInquiry:r,onLogout:c,addToast:h})=>'
helpers = (
    'emParseDate=t=>{if(t==null||t==="")return null;'
    'if(t instanceof Date)return isNaN(t.getTime())?null:t;'
    'let str=String(t).trim();'
    'str=str.replace(/(\\.\\d{3})\\d+/,"$1");'
    'let d=new Date(str);'
    'if(isNaN(d.getTime())&&/^\\d{4}-\\d{2}-\\d{2} /.test(str))d=new Date(str.replace(" ","T"));'
    'if(isNaN(d.getTime())&&/^\\d{4}-\\d{2}-\\d{2}T/.test(str))d=new Date(str);'
    'if(isNaN(d.getTime())&&/^\\d{4}-\\d{2}-\\d{2}/.test(str))d=new Date(str.replace(/-/g,"/").replace("T"," "));'
    'return isNaN(d.getTime())?null:d},'
    'emTimeAgo=t=>{const d=emParseDate(t);if(!d)return"";'
    'const sec=Math.max(0,Math.floor((Date.now()-d.getTime())/1e3));'
    'if(sec<60)return"just now";'
    'const m=Math.floor(sec/60);if(m<60)return m===1?"1 minute ago":m+" minutes ago";'
    'const h=Math.floor(m/60);if(h<24)return h===1?"1 hour ago":h+" hours ago";'
    'const dy=Math.floor(h/24);if(dy<30)return dy===1?"1 day ago":dy+" days ago";'
    'const mo=Math.floor(dy/30);if(mo<12)return mo===1?"1 month ago":mo+" months ago";'
    'const y=Math.floor(dy/365);return y===1?"1 year ago":y+" years ago"},'
    'emFormatUsd=v=>{if(v==null||v==="")return"";const s=String(v).trim();'
    'const n=Number(s.replace(/[^0-9.-]/g,""));'
    'if(!isFinite(n))return s.startsWith("$")?s:"$"+s;'
    'return"$"+n.toLocaleString("en-US",{maximumFractionDigits:2})},'
    'emAsset=p=>{if(!p)return p;if(/^https?:\\/\\//i.test(p)||p.startsWith("data:")||p.startsWith("/"))return p;'
    'return(/\\/admin(?:\\/index\\.php)?$/.test((location.pathname||"").replace(/\\/+$/,""))?"../":"")+p},'
    'e_=({content:s,onSave:n,inquiries:l,onDeleteInquiry:r,deals:da,onDeleteDeal:rd,onLogout:c,addToast:h})=>'
)
must_replace(old_e, helpers, "helpers+props")

# ---------------------------------------------------------------------------
# 2) Replace entire admin component body (from state through locked screen)
# ---------------------------------------------------------------------------
e_start = data.find('e_=({content:s,onSave:n,inquiries:l,onDeleteInquiry:r,deals:da,onDeleteDeal:rd,onLogout:c,addToast:h})=>{')
t_start = data.find('function t_(){')
if e_start < 0 or t_start < 0:
    raise SystemExit("admin bounds missing")

# Keep design panel from original
orig_admin = data[e_start:t_start]
d0 = orig_admin.find('j==="design"?')
d1 = orig_admin.find('):j==="inquiries"?')
if d0 < 0 or d1 < 0:
    raise SystemExit("design panel markers missing")
design_panel = orig_admin[d0:d1]  # includes j==="design"?...]}]

inp = 'className:"w-full bg-brand-dark border border-white/10 p-4 text-white text-xs"'
txa = 'className:"w-full bg-brand-dark border border-white/10 p-6 text-white h-40 text-xs italic"'
lab = 'className:"text-[10px] font-bold text-gray-600 uppercase"'
file_cls = (
    'className:"block w-full text-[10px] text-gray-400 file:mr-4 file:py-2 file:px-4 '
    "file:border-0 file:text-[10px] file:font-black file:uppercase file:tracking-widest "
    'file:bg-gold-500 file:text-black hover:file:bg-white"'
)

def field(label, value_expr, section, key):
    return (
        f'x.jsxs("div",{{className:"space-y-2",children:[x.jsx("label",{{{lab},children:"{label}"}}),'
        f'x.jsx("input",{{{inp},value:{value_expr},'
        f"onChange:C=>y({{...d,{section}:{{...d.{section},{key}:C.target.value}}}})}})]}})"
    )

def tarea(label, value_expr, section, key):
    return (
        f'x.jsxs("div",{{className:"space-y-2",children:[x.jsx("label",{{{lab},children:"{label}"}}),'
        f'x.jsx("textarea",{{{txa},value:{value_expr},'
        f"onChange:C=>y({{...d,{section}:{{...d.{section},{key}:C.target.value}}}})}})]}})"
    )

hero_img = (
    f'x.jsxs("div",{{className:"space-y-4 max-w-md",children:['
    f'x.jsx("label",{{{lab},children:"Hero Image"}}),'
    'x.jsx("div",{className:"aspect-[4/5] max-h-72 overflow-hidden border border-white/10 bg-brand-dark",'
    'children:x.jsx("img",{src:ph&&ph.preview?ph.preview:emAsset(d.hero.image),alt:"Hero preview",'
    'className:"w-full h-full object-cover"})}),'
    'ph&&x.jsx("p",{className:"text-[9px] text-gold-500 uppercase tracking-widest",'
    'children:"Pending — click Commit Changes to publish"}),'
    f'x.jsx("input",{{type:"file",accept:"image/jpeg,image/png,image/webp,image/gif",{file_cls},'
    "onChange:C=>{const f=C.target.files&&C.target.files[0];if(!f)return;"
    "setPh(P=>{P&&P.preview&&URL.revokeObjectURL(P.preview);"
    'return{file:f,preview:URL.createObjectURL(f)}});C.target.value=""}})'
    "]})"
)

approach_img = (
    f'x.jsxs("div",{{className:"space-y-4 max-w-md",children:['
    f'x.jsx("label",{{{lab},children:"Approach Image"}}),'
    'x.jsx("div",{className:"aspect-[4/5] max-h-72 overflow-hidden border border-white/10 bg-brand-dark",'
    'children:x.jsx("img",{src:pa&&pa.preview?pa.preview:emAsset(d.approach.image),alt:"Approach preview",'
    'className:"w-full h-full object-cover"})}),'
    'pa&&x.jsx("p",{className:"text-[9px] text-gold-500 uppercase tracking-widest",'
    'children:"Pending — click Commit Changes to publish"}),'
    f'x.jsx("input",{{type:"file",accept:"image/jpeg,image/png,image/webp,image/gif",{file_cls},'
    "onChange:C=>{const f=C.target.files&&C.target.files[0];if(!f)return;"
    "setPa(P=>{P&&P.preview&&URL.revokeObjectURL(P.preview);"
    'return{file:f,preview:URL.createObjectURL(f)}});C.target.value=""}})'
    "]})"
)

content_panel = (
    'x.jsxs("div",{className:"grid grid-cols-1 gap-8 animate-reveal-up",children:['
    'x.jsx("div",{className:"flex gap-1 border-b border-white/10",children:[["hero","Hero"],["approach","Approach"]].map(([id,label])=>'
    'x.jsx("button",{type:"button",onClick:()=>setCt(id),className:"px-6 py-3 text-[10px] font-black uppercase tracking-[0.3em] transition-colors "+(ct===id?"text-gold-500 border-b-2 border-gold-500":"text-gray-500 hover:text-white"),children:label},id))}),'
    'ct==="hero"?x.jsxs("section",{className:"space-y-10 p-12 bg-brand-accent/30 border border-white/5",children:['
    'x.jsx("h2",{className:"text-xl font-black uppercase tracking-[0.4em] text-gold-500 border-b border-white/5 pb-6",children:"Hero"}),'
    'x.jsx("p",{className:"text-[10px] text-gray-500 uppercase tracking-widest",children:"Edit hero content. Click Commit Changes to publish to the live site."}),'
    + hero_img + ","
    + 'x.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-10",children:['
    + field("Badge", 'd.hero.badge||""', "hero", "badge") + ","
    + field("Headline Alpha", "d.hero.titleLine1", "hero", "titleLine1") + ","
    + field("Headline Beta", "d.hero.titleLine2", "hero", "titleLine2") + ","
    + field("Primary CTA", 'd.hero.ctaPrimary||""', "hero", "ctaPrimary") + ","
    + field("Secondary CTA", 'd.hero.ctaSecondary||""', "hero", "ctaSecondary")
    + "]}),"
    + tarea("Description", "d.hero.description", "hero", "description")
    + ']}):x.jsxs("section",{className:"space-y-10 p-12 bg-brand-accent/30 border border-white/5",children:['
    'x.jsx("h2",{className:"text-xl font-black uppercase tracking-[0.4em] text-gold-500 border-b border-white/5 pb-6",children:"Approach"}),'
    'x.jsx("p",{className:"text-[10px] text-gray-500 uppercase tracking-widest",children:"Edit approach content. Click Commit Changes to publish to the live site."}),'
    + approach_img + ","
    + 'x.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-10",children:['
    + field("Badge", 'd.approach.badge||""', "approach", "badge") + ","
    + field("Title", 'd.approach.title||""', "approach", "title") + ","
    + field("Mission Title", 'd.approach.missionTitle||""', "approach", "missionTitle") + ","
    + field("Mission Value", 'd.approach.missionValue||""', "approach", "missionValue")
    + "]}),"
    + tarea("Description", 'd.approach.description||""', "approach", "description") + ","
    + 'x.jsxs("div",{className:"space-y-6",children:['
    'x.jsx("h3",{className:"text-[10px] font-black uppercase tracking-[0.3em] text-gold-500",children:"Cards"}),'
    'x.jsx("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-8",children:(d.approach.cards||[]).map((card,idx)=>'
    'x.jsxs("div",{className:"space-y-3 p-6 border border-white/10 bg-brand-dark/40",children:['
    f'x.jsxs("div",{{className:"space-y-2",children:[x.jsx("label",{{{lab},children:"Card Title"}}),'
    f'x.jsx("input",{{{inp},value:card.title||"",'
    "onChange:C=>{const cards=[...(d.approach.cards||[])];cards[idx]={...cards[idx],title:C.target.value};"
    "y({...d,approach:{...d.approach,cards}})}})]}),"
    f'x.jsxs("div",{{className:"space-y-2",children:[x.jsx("label",{{{lab},children:"Card Description"}}),'
    'x.jsx("textarea",{className:"w-full bg-brand-dark border border-white/10 p-4 text-white h-28 text-xs italic",'
    'value:card.desc||"",'
    "onChange:C=>{const cards=[...(d.approach.cards||[])];cards[idx]={...cards[idx],desc:C.target.value};"
    "y({...d,approach:{...d.approach,cards}})}})]})"
    "]},idx))})"
    "]})"  # cards wrap
    "]})"  # approach section
    "]})"  # content grid
)

pt = '{single_family:"Single Family",multi_family:"Multi Family",commercial:"Commercial",land:"Land"}'
ex = '{flip:"Flip",rental:"Rental",wholesale:"Wholesale",brrrr:"BRRRR",not_sure:"Not Sure"}'

contacts_panel = (
    'j==="contacts"?x.jsx("div",{className:"space-y-8 animate-reveal-up",children:'
    '(l==null?void 0:l.length)===0?x.jsx("div",{className:"p-20 border border-white/5 text-center text-gray-600 uppercase tracking-widest italic",children:"No contact messages yet."}):'
    'l==null?void 0:l.map(C=>x.jsxs("div",{className:"p-8 bg-brand-accent border border-white/5 flex justify-between items-start gap-6 group",children:['
    'x.jsxs("div",{className:"space-y-3 min-w-0 flex-1",children:['
    'x.jsxs("div",{className:"flex flex-wrap items-baseline justify-between gap-3",children:['
    'x.jsx("h4",{className:"text-xl font-serif font-black italic",children:C.name}),'
    'x.jsx("span",{className:"text-[10px] font-black text-gold-500 tracking-wide",children:emTimeAgo(C.created_at||C.timestamp)||""})'
    ']}),'
    'C.email&&x.jsxs("div",{className:"flex items-center gap-3 text-sm text-gray-400 font-mono min-w-0",children:['
    'x.jsx("span",{className:"truncate",children:C.email}),'
    'x.jsx("a",{href:`mailto:${C.email}`,title:"Email",className:"text-gray-500 hover:text-gold-500 transition-colors shrink-0",children:' + MAIL + '})'
    ']}),'
    'C.phone&&x.jsxs("div",{className:"flex items-center gap-3 text-sm text-gray-400 font-mono min-w-0",children:['
    'x.jsx("span",{className:"truncate",children:C.phone}),'
    'x.jsxs("div",{className:"flex items-center gap-2 shrink-0",children:['
    'x.jsx("a",{href:`https://wa.me/${String(C.phone).replace(/\\D/g,"")}`,target:"_blank",rel:"noopener noreferrer",title:"WhatsApp",className:"text-gray-500 hover:text-emerald-400 transition-colors",children:' + WA + '}),'
    'x.jsx("a",{href:`tel:${C.phone}`,title:"Call",className:"text-gray-500 hover:text-gold-500 transition-colors",children:' + PHONE + '})'
    ']})'
    ']}),'
    'x.jsxs("div",{className:"mt-3 space-y-2",children:['
    'x.jsx("p",{className:"text-sm text-gray-300 whitespace-pre-wrap leading-relaxed",children:(C.message||"").length>140?(C.message||"").slice(0,140)+"…":C.message}),'
    '(C.message||"").length>140&&x.jsx("button",{type:"button",onClick:()=>setFm(C),className:"text-[10px] font-black uppercase tracking-widest text-gold-500 hover:text-white transition-colors",children:"View Full Details"})'
    ']})'
    ']}),'
    'x.jsx("button",{onClick:()=>r(C.id),title:"Delete",className:"p-3 text-gray-700 hover:text-red-500 transition-colors shrink-0",children:x.jsx(d0,{size:22})})'
    "]},C.id))"
    "):"
)

deals_panel = (
    'j==="deals"?x.jsx("div",{className:"space-y-8 animate-reveal-up",children:'
    '(da==null?void 0:da.length)===0?x.jsx("div",{className:"p-20 border border-white/5 text-center text-gray-600 uppercase tracking-widest italic",children:"No deal analyses yet."}):'
    "da==null?void 0:da.map(C=>x.jsxs(\"div\",{className:\"p-8 bg-brand-accent border border-white/5 flex justify-between items-start gap-6 group\",children:["
    'x.jsxs("div",{className:"space-y-3 min-w-0 flex-1",children:['
    'x.jsxs("div",{className:"flex flex-wrap items-baseline justify-between gap-3",children:['
    'x.jsx("h4",{className:"text-xl font-serif font-black italic",children:C.name}),'
    'x.jsx("span",{className:"text-[10px] font-black text-gold-500 tracking-wide",children:emTimeAgo(C.created_at||C.timestamp)||""})'
    ']}),'
    "C.email&&x.jsxs(\"div\",{className:\"flex items-center gap-3 text-sm text-gray-400 font-mono min-w-0\",children:["
    'x.jsx("span",{className:"truncate",children:C.email}),'
    'x.jsx("a",{href:`mailto:${C.email}`,title:"Email",className:"text-gray-500 hover:text-gold-500 transition-colors shrink-0",children:' + MAIL + '})]}),'
    "C.phone&&x.jsxs(\"div\",{className:\"flex items-center gap-3 text-sm text-gray-400 font-mono min-w-0\",children:["
    'x.jsx("span",{className:"truncate",children:C.phone}),'
    'x.jsxs("div",{className:"flex items-center gap-2 shrink-0",children:['
    'x.jsx("a",{href:`https://wa.me/${String(C.phone).replace(/\\D/g,"")}`,target:"_blank",rel:"noopener noreferrer",title:"WhatsApp",className:"text-gray-500 hover:text-emerald-400 transition-colors",children:' + WA + '}),'
    'x.jsx("a",{href:`tel:${C.phone}`,title:"Call",className:"text-gray-500 hover:text-gold-500 transition-colors",children:' + PHONE + '})'
    ']})'
    ']}),'
    'x.jsxs("div",{className:"mt-2 space-y-2 text-sm text-gray-300",children:['
    'x.jsxs("p",{children:[x.jsx("span",{className:"text-[10px] uppercase font-black text-gray-500 tracking-widest mr-2",children:"Address"}),C.property_address]}),'
    'x.jsxs("p",{children:[x.jsx("span",{className:"text-[10px] uppercase font-black text-gray-500 tracking-widest mr-2",children:"Asking"}),C.asking_price]}),'
    'x.jsxs("div",{className:"flex flex-wrap gap-2 pt-1",children:['
    f'x.jsx("span",{{className:"text-[10px] uppercase font-black text-gold-500 border border-gold-500/20 px-2 py-0.5",children:({pt})[C.property_type]||C.property_type}}),'
    f'x.jsx("span",{{className:"text-[10px] uppercase font-black text-gold-500 border border-gold-500/20 px-2 py-0.5",children:({ex})[C.preferred_exit_strategy]||C.preferred_exit_strategy}})'
    "]}),"
    'x.jsxs("div",{className:"pt-2 space-y-2",children:['
    'x.jsx("p",{className:"text-sm text-gray-300 whitespace-pre-wrap",children:(C.query||"").length>160?(C.query||"").slice(0,160)+"…":(C.query||"")}),'
    'x.jsx("button",{type:"button",onClick:()=>setFm({...C,_type:"deal"}),className:"text-[10px] font-black uppercase tracking-widest text-gold-500 hover:text-white transition-colors",children:"View full details"})'
    "]}),"
    "]}),"
    "]}),"
    'x.jsx("button",{onClick:()=>rd(C.id),title:"Delete",className:"p-3 text-gray-700 hover:text-red-500 transition-colors shrink-0",children:x.jsx(d0,{size:22})})'
    "]},C.id))"
    "):"
)

fm_modal = (
    'fm&&x.jsxs("div",{className:"em-admin-modal fixed inset-0 z-[3000] flex items-center justify-center",children:['
    'x.jsx("div",{className:"absolute inset-0 bg-black/80 backdrop-blur-sm",onClick:()=>setFm(null)}),'
    'x.jsxs("div",{className:"em-admin-modal-dialog relative flex flex-col w-full max-w-3xl h-full max-h-screen bg-brand-accent border border-white/10 shadow-2xl overflow-hidden",onClick:e=>e.stopPropagation(),children:['
    'x.jsxs("div",{className:"flex items-center justify-between gap-4 shrink-0 px-8 sm:px-10 py-6 border-b border-white/10",children:['
    'x.jsx("h3",{className:"text-2xl font-serif font-black italic text-gold-500",children:fm._type==="deal"?"Deal Details":"Contact Message"}),'
    'x.jsx("button",{type:"button",onClick:()=>setFm(null),className:"text-gray-500 hover:text-white transition-colors",title:"Close",children:x.jsx(m0,{size:28})})'
    "]}),"
    'x.jsxs("div",{className:"flex-1 min-h-0 overflow-y-auto px-8 sm:px-10 py-6 space-y-6",children:['
    'x.jsx("div",{className:"text-lg font-serif font-black italic",children:fm.name||""}),'
    'fm.email&&x.jsxs("div",{className:"flex items-center gap-3 text-sm text-gray-400 font-mono min-w-0",children:['
    'x.jsx("span",{className:"truncate",children:fm.email}),'
    'x.jsx("a",{href:`mailto:${fm.email}`,className:"text-gray-500 hover:text-gold-500 shrink-0",title:"Email",children:'
    + MAIL
    + "})]}),"
    'fm.phone&&x.jsxs("div",{className:"flex items-center gap-3 text-sm text-gray-400 font-mono min-w-0",children:['
    'x.jsx("span",{className:"truncate",children:fm.phone}),'
    'x.jsxs("div",{className:"flex items-center gap-2 shrink-0",children:['
    'x.jsx("a",{href:`https://wa.me/${String(fm.phone).replace(/\\D/g,"")}`,target:"_blank",rel:"noopener noreferrer",className:"text-gray-500 hover:text-emerald-400",title:"WhatsApp",children:'
    + WA
    + "}),"
    'x.jsx("a",{href:`tel:${fm.phone}`,className:"text-gray-500 hover:text-gold-500",title:"Call",children:'
    + PHONE
    + "})]})]}),"
    'fm._type==="deal"&&x.jsxs("div",{className:"space-y-3 text-sm text-gray-300 border-t border-white/10 pt-6",children:['
    'fm.property_address&&x.jsxs("p",{children:[x.jsx("span",{className:"text-[10px] uppercase font-black text-gray-500 tracking-widest mr-2",children:"Address"}),fm.property_address]}),'
    'fm.asking_price&&x.jsxs("p",{children:[x.jsx("span",{className:"text-[10px] uppercase font-black text-gray-500 tracking-widest mr-2",children:"Asking"}),emFormatUsd(fm.asking_price)]}),'
    'x.jsxs("div",{className:"flex flex-wrap gap-2",children:['
    f'fm.property_type&&x.jsx("span",{{className:"text-[10px] uppercase font-black text-gold-500 border border-gold-500/20 px-2 py-0.5",children:({pt})[fm.property_type]||fm.property_type}}),'
    f'fm.preferred_exit_strategy&&x.jsx("span",{{className:"text-[10px] uppercase font-black text-gold-500 border border-gold-500/20 px-2 py-0.5",children:({ex})[fm.preferred_exit_strategy]||fm.preferred_exit_strategy}})'
    "]})"
    "]}),"
    'x.jsx("div",{className:"border-t border-white/10"}),'
    'x.jsx("p",{className:"text-[10px] uppercase font-black text-gray-500 tracking-widest",children:fm._type==="deal"?"Query":"Message"}),'
    'x.jsx("p",{className:"text-sm sm:text-base text-gray-200 whitespace-pre-wrap leading-relaxed",children:fm._type==="deal"?(fm.query||fm.message||""):(fm.message||"")}),'
    'x.jsx("span",{className:"text-[10px] font-black text-gold-500 inline-block border border-gold-500/20 px-2 py-0.5",children:emTimeAgo(fm.created_at||fm.timestamp)||""})'
    "]})"
    "]})"
    "]})"
)

commit_handler = (
    "onClick:async()=>{try{let next={...d,hero:{...d.hero},approach:{...d.approach}};"
    'const up=async f=>{const fd=new FormData;fd.append("file",f);'
    'const R=await fetch("../backend/media/upload.php",{method:"POST",credentials:"same-origin",body:fd});'
    'const J=await R.json();if(!J.ok)throw new Error(J.error||"Upload failed");'
    'const imgPath=J.path||(J.filename?"uploads/"+J.filename:"");if(!imgPath)throw new Error("Upload missing image path");return imgPath};'
    "if(ph&&ph.file){const heroPath=await up(ph.file);next.hero={...next.hero,image:heroPath};ph.preview&&URL.revokeObjectURL(ph.preview);setPh(null)}"
    "if(pa&&pa.file){const approachPath=await up(pa.file);next.approach={...next.approach,image:approachPath};pa.preview&&URL.revokeObjectURL(pa.preview);setPa(null)}"
    'y(next);await n(next);window.toastr?toastr.success("Changes saved successfully","Success"):h("Changes saved successfully")}'
    'catch(err){window.toastr?toastr.error(err&&err.message||"Save failed","Error"):h(err&&err.message||"Save failed")}}'
)

new_admin = (
    'e_=({content:s,onSave:n,inquiries:l,onDeleteInquiry:r,deals:da,onDeleteDeal:rd,onLogout:c,addToast:h})=>{'
    "const[d,y]=Pe.useState(s),[g,v]=Pe.useState(!!window.__ADMIN_AUTHENTICATED__),[w,E]=Pe.useState(\"\"),"
    '[j,k]=Pe.useState((()=>{const m=new URLSearchParams(location.search).get("menu");'
    'return["content","design","contacts","deals"].includes(m)?m:"content"})()),'
    "[ph,setPh]=Pe.useState(null),[pa,setPa]=Pe.useState(null),[fm,setFm]=Pe.useState(null),[ct,setCt]=Pe.useState(\"hero\"),"
    'D=C=>{C.preventDefault(),h("Use /admin login")};'
    "Pe.useEffect(()=>{const fn=()=>{const m=new URLSearchParams(location.search).get(\"menu\");"
    '["content","design","contacts","deals"].includes(m)&&k(m)};'
    "return window.addEventListener(\"popstate\",fn),()=>window.removeEventListener(\"popstate\",fn)},[]);"
    "Pe.useEffect(()=>{if(ph||pa)return;y(s)},[s,ph,pa]);"
    # unlocked shell
    'return g?x.jsxs("div",{className:"min-h-screen bg-brand-dark text-white flex selection:bg-gold-500 selection:text-black",children:['
    'x.jsxs("aside",{className:"hidden sm:flex w-64 shrink-0 border-r border-white/10 bg-brand-accent/50 min-h-screen flex-col p-8 space-y-12",children:['
    'x.jsx("a",{href:"../",className:"text-2xl font-serif font-black italic gold-gradient uppercase tracking-tighter block",children:"Command Center"}),'
    'x.jsx("nav",{className:"flex flex-col gap-2",children:[["content","Content"],["design","Design"],["contacts","Contacts"],["deals","Deals"]].map(([id,label])=>'
    'x.jsx("button",{onClick:()=>{k(id);const u=new URL(location.href);u.searchParams.set("menu",id);history.pushState({},"",u);},'
    'className:`w-full text-left px-4 py-3 text-[10px] font-black uppercase tracking-widest transition-all rounded-sm ${j===id?"bg-gold-500 text-black":"text-gray-500 hover:text-white hover:bg-white/5"}`,children:label},id))})'
    "]}),"
    'x.jsxs("div",{className:"flex-1 flex flex-col min-w-0 min-h-screen",children:['
    'x.jsxs("header",{className:"sticky top-0 z-50 flex items-center justify-between gap-4 px-4 sm:px-10 py-4 border-b border-white/10 bg-brand-dark/95 backdrop-blur-md",children:['
    'x.jsxs("div",{className:"flex items-center gap-3 min-w-0",children:['
    'x.jsx("span",{className:"sm:hidden text-sm font-serif font-black italic gold-gradient uppercase",children:"CC"}),'
    'x.jsx("span",{className:"text-[10px] font-black uppercase tracking-[0.4em] text-gold-500 truncate",'
    'children:j==="content"?"Content":j==="design"?"Design":j==="contacts"?"Contacts":"Deals"})'
    "]}),"
    'x.jsxs("div",{className:"flex gap-3 items-center shrink-0",children:['
    f'x.jsxs("button",{{{commit_handler},className:"px-4 sm:px-8 py-3 bg-gold-500 text-black text-[10px] font-black uppercase tracking-widest hover:bg-white transition-all flex items-center",children:[x.jsx(h0,{{size:18,className:"mr-2 sm:mr-3"}})," Commit Changes"]}}),'
    'x.jsx("button",{onClick:c,title:"Log out",className:"p-3 border border-white/10 hover:border-red-500 text-gray-500 hover:text-red-500 transition-all",children:x.jsx(n0,{size:20})})'
    "]})]}),"
    'x.jsxs("div",{className:"sm:hidden flex gap-2 px-4 py-3 border-b border-white/10 overflow-x-auto",children:[["content","Content"],["design","Design"],["contacts","Contacts"],["deals","Deals"]].map(([id,label])=>'
    'x.jsx("button",{onClick:()=>{k(id);const u=new URL(location.href);u.searchParams.set("menu",id);history.pushState({},"",u);},'
    'className:`shrink-0 px-4 py-2 text-[10px] font-black uppercase tracking-widest transition-all rounded-sm ${j===id?"bg-gold-500 text-black":"text-gray-500 border border-white/10"}`,children:label},id))}),'
    'x.jsx("div",{className:"flex-1 overflow-y-auto p-6 sm:p-10 pb-40 max-w-6xl w-full",children:'
    + design_panel
    + "):"
    + contacts_panel
    + deals_panel
    + content_panel
    + "})"  # scroll area
    + "]})"  # flex-1 column
    + ","
    + fm_modal
    + "]})"  # root jsxs
    # locked screen (root ]}) already closed the call — only `:` for ternary)
    + ':x.jsx("div",{className:"fixed inset-0 z-[2000] bg-brand-dark flex items-center justify-center p-6",children:'
    'x.jsxs("div",{className:"w-full max-w-md p-12 glass border border-gold-500/20 text-center space-y-10 animate-reveal-up relative z-10 rounded-sm shadow-2xl",children:['
    'x.jsx(t0,{className:"text-gold-500 mx-auto",size:48}),'
    'x.jsx("h2",{className:"text-3xl font-serif font-black italic gold-gradient uppercase",children:"Strategic Entry"}),'
    'x.jsx("p",{className:"text-sm text-gray-400",children:"Admin access is managed via /admin. Open that URL and sign in with your credentials."}),'
    'x.jsx("a",{href:((location.pathname||"").includes("/admin")?".":"admin/"),className:"inline-block w-full bg-gold-500 text-black py-4 font-black uppercase tracking-widest hover:bg-white transition-all",children:"Go to /admin"})'
    "]})})};"
)

data = data[:e_start] + new_admin + data[t_start:]
print("  admin component replaced")
check("admin component")

# ---------------------------------------------------------------------------
# 3) App state, init fetch, save, delete, deal submit, logout, admin mode
# ---------------------------------------------------------------------------
# isAdmin initial + deals state
must_replace(
    "const[s,n]=Pe.useState(_n),[l,r]=Pe.useState([]),[c,h]=Pe.useState([]),[d,y]=Pe.useState(!1),",
    "const[s,n]=Pe.useState(_n),[l,r]=Pe.useState([]),[da,setDa]=Pe.useState([]),[c,h]=Pe.useState([]),"
    "[d,y]=Pe.useState(!!(window.__ADMIN_AUTHENTICATED__||/\\/admin(?:\\/index\\.php)?$/.test((location.pathname||\"\").replace(/\\/+$/,\"\")))),",
    "app state",
)

# Init effect: alive + content get + contacts + deals + mode
old_init = (
    'Pe.useEffect(()=>{console.debug("[App] Protocol Initialization Sequence Started.");const de=setTimeout(()=>{console.warn("[App] Protocol Timeout Reached. Forcing UI active via fallback."),k(!1),D("Connection Slow - Fallback Active")},3e3);return(async()=>{try{console.debug("[Supabase] Attempting to fetch \'site_settings\' record \'macon_v1\'...");const{data:Re,error:Ut}=await ml.from("site_settings").select("data").eq("id","macon_v1").single();Ut?console.error("[Supabase] Error fetching \'site_settings\':",Ut.message):Re?(console.debug("[Supabase] \'site_settings\' retrieved. Merging with defaults..."),n(Pa=>({..._n,...Re.data,navigation:{..._n.navigation,...Re.data.navigation},hero:{..._n.hero,...Re.data.hero},approach:{..._n.approach,...Re.data.approach},investments:{..._n.investments,...Re.data.investments},contact:{..._n.contact,...Re.data.contact}}))):console.warn("[Supabase] \'site_settings\' record not found. Tables might be empty."),console.debug("[Supabase] Attempting to fetch \'inquiries\'...");const{data:rt,error:An}=await ml.from("inquiries").select("*").order("created_at",{ascending:!1});if(An)console.error("[Supabase] Error fetching \'inquiries\':",An.message);else if(rt){console.debug(`[Supabase] Found ${rt.length} inquiries.`);const Pa=rt.map(Dt=>({id:Dt.id,name:Dt.name,email:Dt.email,subject:Dt.subject,timestamp:new Date(Dt.created_at).toLocaleString(),status:Dt.status}));r(Pa)}}catch(Re){console.error("[App] Fatal Error during Initialization:",Re)}finally{console.debug("[App] Initialization attempt complete. Releasing Loading Lock."),clearTimeout(de),k(!1)}})(),new URLSearchParams(window.location.search).get("mode")==="admin"&&y(!0),()=>clearTimeout(de)},[]);'
)

new_init = (
    'Pe.useEffect(()=>{let alive=!0;console.debug("[App] Protocol Initialization Sequence Started.");'
    'const de=setTimeout(()=>{console.warn("[App] Protocol Timeout Reached. Forcing UI active via fallback."),alive&&(k(!1),D("Connection Slow - Fallback Active"))},3e3);'
    "return(async()=>{try{"
    'console.debug("[Content] Fetching site content...");try{const cUrl=' + URL_PREFIX + '+"backend/content/get.php";'
    "const cRes=await fetch(cUrl,{credentials:\"same-origin\"});const cJson=await cRes.json();"
    "alive&&cJson&&cJson.ok&&cJson.data?(console.debug(\"[Content] Merging with defaults...\"),n(Pa=>({..._n,...cJson.data,navigation:{..._n.navigation,...cJson.data.navigation},hero:{..._n.hero,...cJson.data.hero},approach:{..._n.approach,...cJson.data.approach},investments:{..._n.investments,...cJson.data.investments},contact:{..._n.contact,...cJson.data.contact}}))):console.warn(\"[Content] No content record found.\")}catch(cErr){console.error(\"[Content] Fetch error:\",cErr)};"
    'console.debug("[Contacts] Fetching contact submissions...");try{const cr=await fetch(' + URL_PREFIX + '+"backend/contacts/list.php",{credentials:"same-origin"}),cj=await cr.json();'
    "if(cj&&cj.ok&&Array.isArray(cj.contacts)){const Pa=cj.contacts.map(Dt=>({id:Dt.id,name:Dt.name,email:Dt.email,phone:Dt.phone,message:Dt.message,timestamp:emTimeAgo(Dt.created_at),created_at:Dt.created_at}));"
    "r(Pa.slice().sort((a,b)=>{const tb=emParseDate(b.created_at),ta=emParseDate(a.created_at);return(tb?tb.getTime():0)-(ta?ta.getTime():0)})),console.debug(`[Contacts] Found ${Pa.length} messages.`)}"
    'else console.debug("[Contacts] No contacts or unauthorized")}catch(ce){console.error("[Contacts] Fetch error:",ce)};'
    'console.debug("[Deals] Fetching deal analyses...");try{const dr=await fetch(' + URL_PREFIX + '+"backend/deals/list.php",{credentials:"same-origin"}),dj=await dr.json();'
    "if(dj&&dj.ok&&Array.isArray(dj.deals)){const Pa=dj.deals.map(Dt=>({id:Dt.id,name:Dt.name,email:Dt.email,phone:Dt.phone,property_address:Dt.property_address,asking_price:Dt.asking_price,property_type:Dt.property_type,preferred_exit_strategy:Dt.preferred_exit_strategy,query:Dt.query_text,timestamp:emTimeAgo(Dt.created_at),created_at:Dt.created_at}));"
    "setDa(Pa.slice().sort((a,b)=>{const tb=emParseDate(b.created_at),ta=emParseDate(a.created_at);return(tb?tb.getTime():0)-(ta?ta.getTime():0)}));console.debug(`[Deals] Found ${Pa.length} submissions.`)}"
    'else console.debug("[Deals] No deals or unauthorized")}catch(deErr){console.error("[Deals] Fetch error:",deErr)}'
    '}catch(Re){console.error("[App] Fatal Error during Initialization:",Re)}'
    'finally{console.debug("[App] Initialization attempt complete. Releasing Loading Lock."),alive&&(clearTimeout(de),k(!1))}})(),'
    '(function(){var p=location.pathname.replace(/\\/+$/,"");if(new URLSearchParams(location.search).get("mode")==="admin"){var b=p.replace(/\\/index\\.html?$/,"");location.replace((b.endsWith("/admin")?b:b+"/admin")+"/");return}if(/\\/admin(?:\\/index\\.php)?$/.test(p)||window.__ADMIN_AUTHENTICATED__)y(!0)})(),'
    "()=>{alive=!1;clearTimeout(de)}},[]);"
)
must_replace(old_init, new_init, "init effect")

# Save handler C
old_save = (
    'C=async de=>{console.debug("[App] Initiating Command Commit to Supabase..."),n(de);try{const{error:Ze}=await ml.from("site_settings").upsert({id:"macon_v1",data:de});Ze?(console.error("[Supabase] Save Error:",Ze.message),D("Protocol Sync Error")):D("Protocols Committed to Supabase")}catch{D("Supabase Error: Verify SQL Tables")}},'
)
new_save = (
    'C=async de=>{console.debug("[App] Committing content to database...");'
    "const payload={...de,hero:{...de.hero},approach:{...de.approach}};n(payload);"
    "const sUrl=" + URL_PREFIX + '+"backend/content/save.php";'
    'const sRes=await fetch(sUrl,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify({data:payload})});'
    "const sJson=await sRes.json();"
    'if(!sJson||!sJson.ok)throw new Error(sJson&&sJson.error||"Could not save changes");'
    "if(sJson.data)n(Pa=>({..._n,...sJson.data,navigation:{..._n.navigation,...(sJson.data.navigation||{})},hero:{..._n.hero,...(sJson.data.hero||{})},approach:{..._n.approach,...(sJson.data.approach||{})},investments:{..._n.investments,...(sJson.data.investments||{})},contact:{..._n.contact,...(sJson.data.contact||{})}}))},"
)
must_replace(old_save, new_save, "save handler")

# Delete contacts + deals handlers + V deal submit — replace G and V together
old_gv = (
    ',G=async de=>{try{const{error:Ze}=await ml.from("inquiries").delete().eq("id",de);Ze||(r(Re=>Re.filter(Ut=>Ut.id!==de)),D("Record Purged"))}catch{D("Delete Error")}},'
    'V=async de=>{de.preventDefault();const Ze=new FormData(de.currentTarget),Re=Ze.get("name"),Ut=Ze.get("email");'
    'try{const{data:rt,error:An}=await ml.from("inquiries").insert({name:Re,email:Ut,subject:w.title,status:"new"}).select().single();'
    "if(!An&&rt){const Pa={id:rt.id,name:rt.name,email:rt.email,subject:rt.subject,timestamp:new Date(rt.created_at).toLocaleString(),status:rt.status};"
    'r(Dt=>[Pa,...Dt]),D("Transmission Confirmed"),E({isOpen:!1,title:""})}else D("Submission Error - Verify Tables")}'
    'catch{D("Transmission Failure")}},'
)
new_gv = (
    ",G=async de=>{try{const R=await fetch("
    + URL_PREFIX
    + '+"backend/contacts/delete.php",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:de})}),J=await R.json();'
    'if(J&&J.ok){r(Re=>Re.filter(Ut=>Ut.id!==de));window.toastr?toastr.success("Contact deleted","Success"):D("Record Purged")}'
    'else{window.toastr?toastr.error(J&&J.error||"Delete failed","Error"):D("Delete Error")}'
    '}catch{window.toastr?toastr.error("Delete failed","Error"):D("Delete Error")}},'
    "GD=async de=>{try{const R=await fetch("
    + URL_PREFIX
    + '+"backend/deals/delete.php",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:de})}),J=await R.json();'
    'if(J&&J.ok){setDa(Re=>Re.filter(Ut=>Ut.id!==de));window.toastr?toastr.success("Deal deleted","Success"):D("Record Purged")}'
    'else{window.toastr?toastr.error(J&&J.error||"Delete failed","Error"):D("Delete Error")}'
    '}catch{window.toastr?toastr.error("Delete failed","Error"):D("Delete Error")}},'
    "V=async de=>{de.preventDefault();const f=de.currentTarget,fd=new FormData(f),payload={"
    'name:String(fd.get("name")||"").trim(),'
    'phone:String(fd.get("phone")||"").trim(),'
    'email:String(fd.get("email")||"").trim(),'
    'property_address:String(fd.get("property_address")||"").trim(),'
    'asking_price:String(fd.get("asking_price")||"").trim(),'
    'property_type:String(fd.get("property_type")||"").trim(),'
    'preferred_exit_strategy:String(fd.get("preferred_exit_strategy")||"").trim(),'
    'query:String(fd.get("query")||"").trim()'
    '};try{const R=await fetch("backend/deals/submit.php",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}),J=await R.json();'
    'if(!J||!J.ok)throw new Error(J&&J.error||"Submission failed");'
    'f.reset();E({isOpen:!1,title:""});'
    'window.toastr?toastr.success("Thank you! Your deal analysis request has been submitted.","Success"):D("Transmission Confirmed")'
    '}catch(err){window.toastr?toastr.error(err&&err.message||"Could not submit deal","Error"):D(err&&err.message||"Transmission Failure")}},'
)
must_replace(old_gv, new_gv, "G/GD/V handlers")

# Mount admin with deals props + logout
must_replace(
    "const L=Fb(s.activeTemplate);return d?x.jsx(e_,{content:s,onSave:C,inquiries:l,onDeleteInquiry:G,onLogout:()=>y(!1),addToast:D})",
    'const L=Fb("gamma");return d?x.jsx(e_,{content:s,onSave:C,inquiries:l,onDeleteInquiry:G,deals:da,onDeleteDeal:GD,'
    'onLogout:()=>{fetch("../backend/auth/logout.php",{method:"POST",credentials:"same-origin"}).finally(function(){location.reload()})},addToast:D})',
    "mount+gamma+logout",
)
check("handlers")

# ---------------------------------------------------------------------------
# 4) Public image emAsset wrap + remove grayscale
# ---------------------------------------------------------------------------
must_replace(
    'src:(Ct=s.hero)==null?void 0:Ct.image',
    'src:emAsset((Ct=s.hero)==null?void 0:Ct.image)',
    "hero img",
)
must_replace(
    'src:(ct=s.approach)==null?void 0:ct.image',
    'src:emAsset((ct=s.approach)==null?void 0:ct.image)',
    "approach img",
)
must_replace(
    'className:"w-full h-full object-cover grayscale hover:grayscale-0 transition-all duration-[1.5s]"',
    'className:"w-full h-full object-cover transition-all duration-[1.5s]"',
    "hero grayscale",
)
must_replace(
    'className:"w-full h-full object-cover grayscale brightness-90"',
    'className:"w-full h-full object-cover brightness-90"',
    "approach grayscale",
)
must_replace(
    '${s.activeTemplate==="beta"?"grayscale brightness-110":""}',
    '${s.activeTemplate==="beta"?"brightness-110":""}',
    "wrapper grayscale",
)

# ---------------------------------------------------------------------------
# 5) Contact Us form before footer
# ---------------------------------------------------------------------------
footer_marker = 'x.jsx("footer",{className:`py-32 sm:py-60 px-6 sm:px-24 border-t ${L.border} ${s.activeTemplate==="beta"?"bg-gray-100":"bg-brand-gray"}`'
contact_section = (
    'x.jsxs("section",{id:"contact-us",className:`py-24 sm:py-32 px-6 sm:px-24 border-t ${L.border}`,children:['
    'x.jsxs("div",{className:"max-w-4xl mx-auto space-y-12",children:['
    'x.jsxs("div",{className:"text-center space-y-4",children:['
    'x.jsx("h2",{className:`text-[clamp(2rem,5vw,3.5rem)] ${L.heading}`,children:"Contact Us"}),'
    'x.jsx("p",{className:`text-base sm:text-lg italic ${L.muted}`,children:"Send a message and our team will get back to you."})]}),'
    'x.jsxs("form",{className:"space-y-8",onSubmit:async de=>{de.preventDefault();const f=de.currentTarget,fd=new FormData(f),'
    'payload={name:String(fd.get("name")||"").trim(),email:String(fd.get("email")||"").trim(),phone:String(fd.get("phone")||"").trim(),message:String(fd.get("message")||"").trim()};'
    'try{const R=await fetch("backend/contacts/submit.php",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)}),J=await R.json();'
    'if(!J.ok)throw new Error(J.error||"Submission failed");f.reset();'
    'window.toastr?toastr.success("Thank you! Your message has been sent.","Success"):D("Message sent")'
    '}catch(err){window.toastr?toastr.error(err&&err.message||"Could not send message","Error"):D(err&&err.message||"Could not send message")}},children:['
    'x.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-8",children:['
    'x.jsxs("div",{className:"space-y-2",children:[x.jsx("label",{className:`text-[11px] font-black uppercase tracking-widest ${L.muted}`,children:"Name"}),'
    'x.jsx("input",{name:"name",required:!0,className:`w-full bg-transparent border-b-2 py-3 text-base focus:outline-none ${s.activeTemplate==="alpha"?"border-white/10 text-white":s.activeTemplate==="beta"?"border-black/20 text-black":"border-brand-cyan/20 text-brand-cyan"}`,placeholder:"Your name"})]}),'
    'x.jsxs("div",{className:"space-y-2",children:[x.jsx("label",{className:`text-[11px] font-black uppercase tracking-widest ${L.muted}`,children:"Email Address"}),'
    'x.jsx("input",{name:"email",type:"email",required:!0,className:`w-full bg-transparent border-b-2 py-3 text-base focus:outline-none ${s.activeTemplate==="alpha"?"border-white/10 text-white":s.activeTemplate==="beta"?"border-black/20 text-black":"border-brand-cyan/20 text-brand-cyan"}`,placeholder:"you@example.com"})]})]}),'
    'x.jsxs("div",{className:"space-y-2",children:[x.jsx("label",{className:`text-[11px] font-black uppercase tracking-widest ${L.muted}`,children:"Phone Number"}),'
    'x.jsx("input",{name:"phone",type:"tel",required:!0,className:`w-full bg-transparent border-b-2 py-3 text-base focus:outline-none ${s.activeTemplate==="alpha"?"border-white/10 text-white":s.activeTemplate==="beta"?"border-black/20 text-black":"border-brand-cyan/20 text-brand-cyan"}`,placeholder:"+1 555 000 0000"})]}),'
    'x.jsxs("div",{className:"space-y-2",children:[x.jsx("label",{className:`text-[11px] font-black uppercase tracking-widest ${L.muted}`,children:"Message"}),'
    'x.jsx("textarea",{name:"message",required:!0,rows:5,className:`w-full bg-transparent border-2 p-4 text-base focus:outline-none rounded-sm ${s.activeTemplate==="alpha"?"border-white/10 text-white":s.activeTemplate==="beta"?"border-black/20 text-black":"border-brand-cyan/20 text-brand-cyan"}`,placeholder:"How can we help?"})]}),'
    'x.jsx(Qs,{template:s.activeTemplate,type:"submit",className:"w-full md:w-auto px-16 py-5 text-sm",children:"Send Message"})'
    "]})]})]}),"
) + footer_marker
must_replace(footer_marker, contact_section, "contact form")
check("contact form")

# ---------------------------------------------------------------------------
# 6) Force public theme to gamma (leave admin gold)
# ---------------------------------------------------------------------------
pub_start = data.find('):x.jsxs("div",{className:`min-h-screen ${L.bg}')
pub_end = data.find('const Zg=document.getElementById("root")')
if pub_start < 0 or pub_end < 0:
    raise SystemExit("public branch bounds missing")
before, mid, after = data[:pub_start], data[pub_start:pub_end], data[pub_end:]
mid = mid.replace("s.activeTemplate", '"gamma"')
data = before + mid + after
print("  public gamma forced")
check("gamma")

# ---------------------------------------------------------------------------
# 7) Analyze Deal modal — full form + scrollable
# ---------------------------------------------------------------------------
inp_cls = 'className:`w-full bg-transparent border-b-2 py-3 text-base sm:text-lg focus:outline-none italic border-brand-cyan/20 text-brand-cyan font-mono`'
sel_cls = 'className:`w-full bg-[#000814] border-b-2 py-3 text-base sm:text-lg focus:outline-none italic border-brand-cyan/20 text-brand-cyan font-mono`'
lab_cls = 'className:"text-[10px] font-black uppercase tracking-widest text-gray-500"'
txa_cls = 'className:`w-full bg-transparent border-2 p-4 text-base focus:outline-none rounded-sm border-brand-cyan/20 text-brand-cyan font-mono`'

def text_field(label, name, placeholder="", typ=None):
    parts = [f'name:"{name}"', "required:!0"]
    if typ:
        parts.insert(1, f'type:"{typ}"')
    parts.append(inp_cls)
    if placeholder:
        parts.append(f'placeholder:"{placeholder}"')
    attrs = ",".join(parts)
    return (
        'x.jsxs("div",{className:"space-y-3",children:['
        f'x.jsx("label",{{{lab_cls},children:"{label}"}}),'
        f'x.jsx("input",{{{attrs}}})'
        "]})"
    )

def select_field(label, name, options):
    option_nodes = ['x.jsx("option",{value:"",disabled:!0,children:"Select..."},"")']
    for value, text in options:
        option_nodes.append(f'x.jsx("option",{{value:"{value}",children:"{text}"}},"{value}")')
    return (
        'x.jsxs("div",{className:"space-y-3",children:['
        f'x.jsx("label",{{{lab_cls},children:"{label}"}}),'
        f'x.jsxs("select",{{name:"{name}",required:!0,defaultValue:"",{sel_cls},children:['
        + ",".join(option_nodes)
        + "]})"
        "]})"
    )

property_types = [
    ("single_family", "Single Family"),
    ("multi_family", "Multi Family"),
    ("commercial", "Commercial"),
    ("land", "Land"),
]
exits = [
    ("flip", "Flip"),
    ("rental", "Rental"),
    ("wholesale", "Wholesale"),
    ("brrrr", "BRRRR (Buy, Renovate, Rent, Refinance, Repeat)"),
    ("not_sure", "Not Sure"),
]

new_form = (
    'x.jsxs("form",{className:"space-y-8",onSubmit:V,children:['
    'x.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-8",children:['
    + text_field("Name", "name", "Full Name") + ","
    + text_field("Phone Number", "phone", "+1 555 000 0000", "tel") + ","
    + text_field("Email Address", "email", "you@example.com", "email") + ","
    + text_field("Asking Price", "asking_price", "$250,000")
    + "]})" + ","
    + text_field("Property Address", "property_address", "Street, City, State") + ","
    + 'x.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-8",children:['
    + select_field("Property Type", "property_type", property_types) + ","
    + select_field("Preferred Exit Strategy", "preferred_exit_strategy", exits)
    + "]})" + ","
    + 'x.jsxs("div",{className:"space-y-3",children:['
    + f'x.jsx("label",{{{lab_cls},children:"Query"}}),'
    + f'x.jsx("textarea",{{name:"query",required:!0,rows:4,{txa_cls},placeholder:"Tell us about the deal..."}})'
    + "]})" + ","
    + 'x.jsx(Qs,{template:"gamma",type:"submit",className:"w-full py-6 text-sm",children:"Submit Deal Analysis"})'
    + "]})"
)

old_form_start = 'x.jsxs("form",{className:"space-y-12",onSubmit:V,children:['
# After gamma force, template is "gamma"
old_form_end = 'x.jsx(Qs,{template:"gamma",type:"submit",className:"w-full py-8 text-sm",children:"Commit Transmission"})]})'
si = data.find(old_form_start)
ei = data.find(old_form_end, si)
if si < 0 or ei < 0:
    # try without gamma already
    old_form_end2 = 'x.jsx(Qs,{template:s.activeTemplate,type:"submit",className:"w-full py-8 text-sm",children:"Commit Transmission"})]})'
    ei = data.find(old_form_end2, si)
    if si < 0 or ei < 0:
        raise SystemExit(f"deal form not found {si} {ei}")
    end_len = len(old_form_end2)
else:
    end_len = len(old_form_end)
data = data[:si] + new_form + data[ei + end_len :]
print("  deal form replaced")

must_replace(
    "relative w-full max-w-4xl p-12 sm:p-24 animate-reveal-up glass border rounded-sm shadow-2xl",
    "relative w-full max-w-4xl max-h-[92vh] overflow-y-auto p-8 sm:p-16 animate-reveal-up glass border rounded-sm shadow-2xl",
    "modal scroll",
)
i = data.find("TACTICAL INTAKE")
h = data.rfind("text-center mb-16 space-y-6", 0, i)
if h > 0:
    data = data[:h] + "text-center mb-10 space-y-4" + data[h + len("text-center mb-16 space-y-6") :]
    print("  modal header spacing")

check("deal form")

# ---------------------------------------------------------------------------
# Final verification
# ---------------------------------------------------------------------------
keys = [
    "backend/content/get.php",
    "backend/content/save.php",
    "backend/deals/list.php",
    "backend/deals/submit.php",
    "backend/contacts/submit.php",
    "backend/media/upload.php",
    "setCt",
    'Fb("gamma")',
    'j==="deals"',
    "Submit Deal Analysis",
    "Contact Us",
    "__ADMIN_AUTHENTICATED__",
    "emAsset",
    "emTimeAgo",
    "fm&&",
]
print("\n=== VERIFICATION ===")
ok = True
for k in keys:
    present = k in data
    print(f"{'YES' if present else 'NO '} {k}")
    ok = ok and present
print("macon_admin_2025 gone:", "macon_admin_2025" not in data)
print("site_settings upsert gone:", '.from("site_settings").upsert' not in data)
print("DONE" if ok else "MISSING KEYS")
sys.exit(0 if ok else 1)
