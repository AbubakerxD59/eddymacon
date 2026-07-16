#!/usr/bin/env python3
"""Patch the live admin SPA to add Books CRUD + public sale links."""
from pathlib import Path
import subprocess
import sys

path = Path("/Applications/MAMP/htdocs/eddymacon/assets/index-Bpoe2-CA.js")
data = path.read_text(encoding="utf-8")

URL_PREFIX = '(/\\/admin(?:\\/index\\.php)?$/.test((location.pathname||"").replace(/\\/+$/,""))?"../":"")'


def check(label):
    path.write_text(data, encoding="utf-8")
    r = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"PARSE FAIL after {label}:", r.stderr[-500:])
        sys.exit(1)
    print(f"OK {label}")


def must_replace(old, new, label, count=1):
    global data
    found = data.count(old)
    if found < count:
        raise SystemExit(f"{label}: expected {count}, found {found}\nOLD[:160]={old[:160]!r}")
    data = data.replace(old, new, count if count != -1 else found)
    print(f"  {label} ({found})")


MENU_OLD = '[["content","Content"],["design","Design"],["inquiries","Contacts"],["deals","Deals"]]'
MENU_NEW = '[["content","Content"],["design","Design"],["books","Books"],["inquiries","Contacts"],["deals","Deals"]]'

MENU_KEYS_OLD = '["content","design","inquiries","deals"]'
MENU_KEYS_NEW = '["content","design","books","inquiries","deals"]'

HEADER_OLD = 'children:j==="content"?"Content":j==="design"?"Design":j==="inquiries"?"Contacts":"Deals"}'
HEADER_NEW = 'children:j==="content"?"Content":j==="design"?"Design":j==="books"?"Books":j==="inquiries"?"Contacts":"Deals"}'

# ---------------------------------------------------------------------------
# 1) Menu keys + nav labels + header title
# ---------------------------------------------------------------------------
must_replace(MENU_KEYS_OLD, MENU_KEYS_NEW, "menu keys", count=2)
must_replace(MENU_OLD, MENU_NEW, "nav menus", count=3)
must_replace(HEADER_OLD, HEADER_NEW, "header title")

# ---------------------------------------------------------------------------
# 2) Admin component props + local book form state
# ---------------------------------------------------------------------------
must_replace(
    'e_=({content:s,onSave:n,inquiries:l,onDeleteInquiry:r,deals:da,onDeleteDeal:rd,onLogout:c,addToast:h})=>',
    'e_=({content:s,onSave:n,inquiries:l,onDeleteInquiry:r,deals:da,onDeleteDeal:rd,books:bk,onSaveBook:sb,onDeleteBook:db,onLogout:c,addToast:h})=>',
    "admin props",
)

must_replace(
    '[emLogoutBusy,setEmLogoutBusy]=Pe.useState(!1),D=C=>{C.preventDefault(),h("Use /admin login")};',
    '[emLogoutBusy,setEmLogoutBusy]=Pe.useState(!1),[bf,setBf]=Pe.useState(null),[bkBusy,setBkBusy]=Pe.useState(!1),'
    'D=C=>{C.preventDefault(),h("Use /admin login")};',
    "book form state",
)

# ---------------------------------------------------------------------------
# 3) Books panel + book form modal (insert before content panel)
# ---------------------------------------------------------------------------
inp = 'className:"w-full bg-brand-dark border border-white/10 p-4 text-white text-xs"'
txa = 'className:"w-full bg-brand-dark border border-white/10 p-4 text-white h-28 text-xs italic"'
lab = 'className:"text-[10px] font-bold text-gray-600 uppercase"'
file_cls = (
    'className:"block w-full text-[10px] text-gray-400 file:mr-4 file:py-2 file:px-4 '
    "file:border-0 file:text-[10px] file:font-black file:uppercase file:tracking-widest "
    'file:bg-gold-500 file:text-black hover:file:bg-white"'
)

books_panel = (
    'j==="books"?x.jsxs("div",{className:"space-y-8 animate-reveal-up",children:['
    'x.jsxs("div",{className:"flex flex-wrap items-center justify-between gap-4",children:['
    'x.jsxs("div",{className:"space-y-2",children:['
    'x.jsx("h2",{className:"text-xl font-black uppercase tracking-[0.4em] text-gold-500",children:"Books"}),'
    'x.jsx("p",{className:"text-[10px] text-gray-500 uppercase tracking-widest",children:"Add books with their sale links. Featured book powers the hero CTA."})'
    "]}),"
    'x.jsx("button",{type:"button",onClick:()=>setBf({id:0,title:"",description:"",sale_url:"",cover_image:"",is_featured:!1,sort_order:0}),'
    'className:"px-6 py-3 bg-gold-500 text-black text-[10px] font-black uppercase tracking-widest hover:bg-white transition-all",children:"+ Add Book"})'
    "]}),"
    '(bk==null?void 0:bk.length)===0?x.jsx("div",{className:"p-20 border border-white/5 text-center text-gray-600 uppercase tracking-widest italic",children:"No books yet. Add your first book."}):'
    'x.jsx("div",{className:"space-y-4",children:(bk||[]).map(B=>x.jsxs("div",{className:"p-6 sm:p-8 bg-brand-accent border border-white/5 flex flex-col sm:flex-row justify-between items-start gap-6",children:['
    'x.jsxs("div",{className:"flex gap-5 min-w-0 flex-1",children:['
    'B.cover_image?x.jsx("img",{src:emAsset(B.cover_image),alt:B.title||"Cover",className:"w-16 h-20 object-cover border border-white/10 shrink-0"}):'
    'x.jsx("div",{className:"w-16 h-20 border border-white/10 bg-brand-dark/60 shrink-0 flex items-center justify-center text-[9px] text-gray-600 uppercase tracking-widest",children:"No cover"}),'
    'x.jsxs("div",{className:"space-y-2 min-w-0",children:['
    'x.jsxs("div",{className:"flex flex-wrap items-center gap-3",children:['
    'x.jsx("h4",{className:"text-xl font-serif font-black italic truncate",children:B.title}),'
    'B.is_featured&&x.jsx("span",{className:"text-[9px] font-black uppercase tracking-widest text-black bg-gold-500 px-2 py-0.5",children:"Featured"})'
    "]}),"
    'B.description&&x.jsx("p",{className:"text-sm text-gray-400 line-clamp-2",children:B.description}),'
    'x.jsx("a",{href:B.sale_url,target:"_blank",rel:"noopener noreferrer",className:"text-[11px] font-mono text-gold-500 hover:text-white transition-colors break-all",children:B.sale_url})'
    "]})]}),"
    'x.jsxs("div",{className:"flex items-center gap-2 shrink-0",children:['
    'x.jsx("button",{type:"button",onClick:()=>setBf({id:B.id,title:B.title||"",description:B.description||"",sale_url:B.sale_url||"",cover_image:B.cover_image||"",is_featured:!!B.is_featured,sort_order:B.sort_order||0}),'
    'className:"px-4 py-2 border border-white/10 text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-gold-500 hover:border-gold-500/40 transition-colors",children:"Edit"}),'
    'x.jsx("button",{type:"button",disabled:emDelBusy===B.id,onClick:()=>db(B.id),title:"Delete",'
    'className:"p-3 text-gray-700 hover:text-red-500 transition-colors disabled:opacity-50",children:x.jsx(d0,{size:22})})'
    "]})"
    "]},B.id))"
    "})"
    "]})"
    ":"
)

book_modal = (
    'bf&&x.jsxs("div",{className:"em-admin-modal fixed inset-0 z-[3000] flex items-center justify-center",children:['
    'x.jsx("div",{className:"absolute inset-0 bg-black/80 backdrop-blur-sm",onClick:()=>{if(!bkBusy){bf.coverPreview&&URL.revokeObjectURL(bf.coverPreview);setBf(null)}}}),'
    'x.jsxs("div",{className:"em-admin-modal-dialog relative flex flex-col w-full max-w-2xl h-full max-h-screen bg-brand-accent border border-white/10 shadow-2xl overflow-hidden",onClick:e=>e.stopPropagation(),children:['
    'x.jsxs("div",{className:"flex items-center justify-between gap-4 shrink-0 px-8 sm:px-10 py-6 border-b border-white/10",children:['
    'x.jsx("h3",{className:"text-2xl font-serif font-black italic text-gold-500",children:bf.id?"Edit Book":"Add Book"}),'
    'x.jsx("button",{type:"button",disabled:bkBusy,onClick:()=>{bf.coverPreview&&URL.revokeObjectURL(bf.coverPreview);setBf(null)},className:"text-gray-500 hover:text-white transition-colors",title:"Close",children:x.jsx(m0,{size:28})})'
    "]}),"
    'x.jsxs("form",{className:"flex-1 min-h-0 overflow-y-auto px-8 sm:px-10 py-6 space-y-6",onSubmit:async e=>{e.preventDefault();if(bkBusy)return;setBkBusy(!0);try{'
    'let cover=bf.cover_image||"";'
    'if(bf.coverFile){const fd=new FormData;fd.append("file",bf.coverFile);'
    'const R=await fetch("../backend/media/upload.php",{method:"POST",credentials:"same-origin",body:fd});'
    'const J=await R.json();if(!J.ok)throw new Error(J.error||"Upload failed");'
    'cover=J.path||(J.filename?"uploads/"+J.filename:"");if(!cover)throw new Error("Upload missing image path")}'
    'await sb({id:bf.id||0,title:bf.title,description:bf.description,sale_url:bf.sale_url,cover_image:cover,is_featured:!!bf.is_featured,sort_order:Number(bf.sort_order)||0});'
    'bf.coverPreview&&URL.revokeObjectURL(bf.coverPreview);setBf(null)'
    '}catch(err){window.toastr?toastr.error(err&&err.message||"Could not save book","Error"):h(err&&err.message||"Could not save book")}'
    'finally{setBkBusy(!1)}},children:['
    f'x.jsxs("div",{{className:"space-y-2",children:[x.jsx("label",{{{lab},children:"Title"}}),'
    f'x.jsx("input",{{{inp},required:!0,value:bf.title||"",onChange:C=>setBf(P=>({{...P,title:C.target.value}}))}})]}}),'
    f'x.jsxs("div",{{className:"space-y-2",children:[x.jsx("label",{{{lab},children:"Sale Link"}}),'
    f'x.jsx("input",{{{inp},required:!0,type:"url",placeholder:"https://...",value:bf.sale_url||"",onChange:C=>setBf(P=>({{...P,sale_url:C.target.value}}))}})]}}),'
    f'x.jsxs("div",{{className:"space-y-2",children:[x.jsx("label",{{{lab},children:"Description"}}),'
    f'x.jsx("textarea",{{{txa},value:bf.description||"",onChange:C=>setBf(P=>({{...P,description:C.target.value}}))}})]}}),'
    'x.jsxs("div",{className:"space-y-4 max-w-xs",children:['
    f'x.jsx("label",{{{lab},children:"Cover Image"}}),'
    '(bf.coverPreview||bf.cover_image)?x.jsx("img",{src:bf.coverPreview||emAsset(bf.cover_image),alt:"Cover preview",className:"w-28 h-36 object-cover border border-white/10"}):null,'
    f'x.jsx("input",{{type:"file",accept:"image/jpeg,image/png,image/webp,image/gif",{file_cls},'
    "onChange:C=>{const f=C.target.files&&C.target.files[0];if(!f)return;"
    "setBf(P=>{P&&P.coverPreview&&URL.revokeObjectURL(P.coverPreview);"
    'return{...P,coverFile:f,coverPreview:URL.createObjectURL(f)}});C.target.value=""}})'
    "]}),"
    'x.jsxs("label",{className:"flex items-center gap-3 cursor-pointer select-none",children:['
    'x.jsx("input",{type:"checkbox",checked:!!bf.is_featured,onChange:C=>setBf(P=>({...P,is_featured:C.target.checked})),'
    'className:"w-4 h-4 accent-[#D4AF37]"}),'
    'x.jsx("span",{className:"text-[10px] font-bold text-gray-400 uppercase tracking-widest",children:"Featured (hero CTA sale link)"})'
    "]}),"
    'x.jsxs("div",{className:"flex gap-3 pt-4 border-t border-white/10",children:['
    'x.jsx("button",{type:"submit",disabled:bkBusy,className:"px-8 py-3 bg-gold-500 text-black text-[10px] font-black uppercase tracking-widest hover:bg-white transition-all disabled:opacity-60",children:bkBusy?"Saving...":"Save Book"}),'
    'x.jsx("button",{type:"button",disabled:bkBusy,onClick:()=>{bf.coverPreview&&URL.revokeObjectURL(bf.coverPreview);setBf(null)},'
    'className:"px-6 py-3 border border-white/10 text-[10px] font-black uppercase tracking-widest text-gray-500 hover:text-white transition-colors",children:"Cancel"})'
    "]})"
    "]})"
    "]})"
    "]})"
)

# Insert books panel into ternary chain: deals ): CONTENT  →  deals ): books ): CONTENT
content_marker = '):x.jsxs("div",{className:"grid grid-cols-1 gap-8 animate-reveal-up"'
# Need the deals panel closing ): before content — find unique context
# Actual: ...]},C.id))}):x.jsxs("div",{className:"grid grid-cols-1 gap-8 animate-reveal-up"
old_chain = ']},C.id))}):x.jsxs("div",{className:"grid grid-cols-1 gap-8 animate-reveal-up"'
# Wait - deals ends with ]},C.id))}): then content. But inquiries also ends similarly.
# Find specifically after deals panel - look for "No deal analyses" then content

deals_empty = 'No deal analyses yet.'
di = data.find(deals_empty)
if di < 0:
    raise SystemExit("deals empty marker missing")
ci = data.find(content_marker, di)
if ci < 0:
    raise SystemExit("content panel after deals missing")

# Verify the character before content_marker starts with deals closing
# content_marker already includes `):`
# Replace `):x.jsxs("div"...` with `):` + books_panel + `x.jsxs("div"...`
# books_panel already ends with `):`
new_at_content = "):" + books_panel + 'x.jsxs("div",{className:"grid grid-cols-1 gap-8 animate-reveal-up"'
# But content_marker is `):x.jsxs(...)` so:
if data[ci:ci + len(content_marker)] != content_marker:
    raise SystemExit("content marker mismatch")
data = data[:ci] + new_at_content + data[ci + len(content_marker) :]
print("  books panel inserted")

# Insert book modal next to fm modal
fm_marker = 'fm&&x.jsxs("div",{className:"em-admin-modal fixed inset-0 z-[3000] flex items-center justify-center"'
fi = data.find(fm_marker)
if fi < 0:
    raise SystemExit("fm modal marker missing")
data = data[:fi] + book_modal + "," + data[fi:]
print("  book modal inserted")
check("books admin ui")

# ---------------------------------------------------------------------------
# 4) App state, fetch, save/delete handlers, mount props
# ---------------------------------------------------------------------------
must_replace(
    "const[s,n]=Pe.useState(_n),[l,r]=Pe.useState([]),[da,setDa]=Pe.useState([]),[c,h]=Pe.useState([]),",
    "const[s,n]=Pe.useState(_n),[l,r]=Pe.useState([]),[da,setDa]=Pe.useState([]),[bk,setBk]=Pe.useState([]),[c,h]=Pe.useState([]),",
    "app books state",
)

must_replace(
    'else console.debug("[Deals] No deals or unauthorized")}catch(deErr){console.error("[Deals] Fetch error:",deErr)}'
    '}catch(Re){console.error("[App] Fatal Error during Initialization:",Re)}',
    'else console.debug("[Deals] No deals or unauthorized")}catch(deErr){console.error("[Deals] Fetch error:",deErr)};'
    'console.debug("[Books] Fetching books...");try{const br=await fetch(' + URL_PREFIX + '+"backend/books/list.php",{credentials:"same-origin"}),bj=await br.json();'
    "if(bj&&bj.ok&&Array.isArray(bj.books)){setBk(bj.books);console.debug(`[Books] Found ${bj.books.length} books.`)}"
    'else console.debug("[Books] No books")}catch(bkErr){console.error("[Books] Fetch error:",bkErr)}'
    '}catch(Re){console.error("[App] Fatal Error during Initialization:",Re)}',
    "books fetch",
)

must_replace(
    '}catch{window.toastr?toastr.error("Delete failed","Error"):D("Delete Error")}},'
    "V=async de=>{de.preventDefault();if(emDBusy)retu",
    '}catch{window.toastr?toastr.error("Delete failed","Error"):D("Delete Error")}},'
    "GB=async de=>{try{const R=await fetch("
    + URL_PREFIX
    + '+"backend/books/delete.php",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify({id:de})}),J=await R.json();'
    'if(J&&J.ok){setBk(Re=>Re.filter(Ut=>Ut.id!==de));window.toastr?toastr.success("Book deleted","Success"):D("Record Purged")}'
    'else{window.toastr?toastr.error(J&&J.error||"Delete failed","Error"):D("Delete Error")}'
    '}catch{window.toastr?toastr.error("Delete failed","Error"):D("Delete Error")}},'
    "SB=async de=>{try{const R=await fetch("
    + URL_PREFIX
    + '+"backend/books/save.php",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},body:JSON.stringify(de)}),J=await R.json();'
    'if(!J||!J.ok)throw new Error(J&&J.error||"Could not save book");'
    "const saved=J.book;setBk(Re=>{const rest=Re.filter(Ut=>Ut.id!==saved.id);const next=[saved,...rest];"
    "return next.slice().sort((a,b)=>(b.is_featured?1:0)-(a.is_featured?1:0)||(a.sort_order||0)-(b.sort_order||0)||a.id-b.id)});"
    'window.toastr?toastr.success(de.id?"Book updated":"Book added","Success"):D("Book saved");return saved'
    '}catch(err){window.toastr?toastr.error(err&&err.message||"Could not save book","Error"):D(err&&err.message||"Save Error");throw err}},'
    "V=async de=>{de.preventDefault();if(emDBusy)retu",
    "GB/SB handlers",
)

must_replace(
    "deals:da,onDeleteDeal:GD,onLogout:",
    "deals:da,onDeleteDeal:GD,books:bk,onSaveBook:SB,onDeleteBook:GB,onLogout:",
    "mount books props",
)
check("books handlers")

# ---------------------------------------------------------------------------
# 5) Public: hero CTA opens books picker modal ("Get Book" / "Get Books")
# ---------------------------------------------------------------------------
must_replace(
    "[w,E]=Pe.useState({isOpen:!1,title:\"\"}),",
    "[w,E]=Pe.useState({isOpen:!1,title:\"\"}),[bmOpen,setBmOpen]=Pe.useState(!1),",
    "bmOpen state",
)

must_replace(
    'onClick:()=>window.open("https://a.co/d/9GrX6ir","_blank"),children:(Fe=s.hero)==null?void 0:Fe.ctaPrimary',
    'onClick:()=>setBmOpen(!0),children:(bk||[]).length>1?"Get Books":"Get Book"',
    "hero CTA books modal",
)

toast_marker = 'x.jsx("div",{className:"fixed bottom-10 left-1/2 -translate-x-1/2 z-[2000] flex flex-col gap-4"'
books_modal = (
    'bmOpen&&x.jsxs("div",{className:"fixed inset-0 z-[1000] flex items-center justify-center p-6",children:['
    'x.jsx("div",{className:"absolute inset-0 bg-brand-dark/98 backdrop-blur-3xl",onClick:()=>setBmOpen(!1)}),'
    'x.jsxs("div",{className:"relative w-full max-w-4xl max-h-[92vh] overflow-y-auto p-8 sm:p-16 animate-reveal-up glass border rounded-sm shadow-2xl border-brand-cyan/20",'
    'onClick:e=>e.stopPropagation(),children:['
    'x.jsx("button",{type:"button",onClick:()=>setBmOpen(!1),className:"absolute top-10 right-10 text-gray-500 hover:text-white transition-colors",children:x.jsx(m0,{size:40})}),'
    'x.jsxs("div",{className:"text-center mb-10 space-y-4",children:['
    'x.jsx("span",{className:"uppercase tracking-[0.8em] text-[10px] font-black italic text-brand-cyan",children:"LIBRARY"}),'
    'x.jsx("h2",{className:`text-4xl sm:text-6xl leading-tight uppercase tracking-tighter ${L.heading}`,children:(bk||[]).length>1?"Get Books":"Get Book"})'
    "]}),"
    '(bk||[]).length===0?x.jsx("p",{className:`text-center text-sm italic ${L.muted}`,children:"No books available yet."}):'
    'x.jsx("div",{className:"grid grid-cols-1 sm:grid-cols-2 gap-8",children:(bk||[]).map(B=>x.jsxs("button",{type:"button",'
    'onClick:()=>{if(B.sale_url)window.open(B.sale_url,"_blank")},'
    'className:"text-left group space-y-4 p-4 border border-brand-cyan/15 hover:border-brand-cyan/50 transition-colors bg-black/20",children:['
    'B.cover_image?x.jsx("div",{className:"aspect-[3/4] max-h-64 overflow-hidden border border-white/10",'
    'children:x.jsx("img",{src:emAsset(B.cover_image),alt:B.title||"Book cover",className:"w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-500"})}):'
    'x.jsx("div",{className:"aspect-[3/4] max-h-64 border border-white/10 flex items-center justify-center",'
    'children:x.jsx("span",{className:"text-[10px] uppercase tracking-widest text-gray-600",children:"No cover"})}),'
    'x.jsxs("div",{className:"space-y-2",children:['
    'x.jsx("h3",{className:`text-xl sm:text-2xl font-serif font-black italic ${L.heading}`,children:B.title}),'
    'B.description&&x.jsx("p",{className:`text-sm line-clamp-2 ${L.muted}`,children:B.description}),'
    'x.jsx("span",{className:"inline-block text-[10px] font-black uppercase tracking-widest text-brand-cyan group-hover:text-white transition-colors",children:"View sale link →"})'
    "]})"
    "]},B.id))"
    "})"
    "]})"
    "]}),"
)
if toast_marker not in data:
    raise SystemExit("toast marker missing for books modal")
data = data.replace(toast_marker, books_modal + toast_marker, 1)
print("  books picker modal inserted")
check("books picker modal")

# ---------------------------------------------------------------------------
# 6) Public books section before footer
# ---------------------------------------------------------------------------
footer_marker = 'x.jsx("footer",{className:`py-32 sm:py-60 px-6 sm:px-24 border-t ${L.border} ${s.activeTemplate==="beta"?"bg-gray-100":"bg-bran'
# Need unique match - use longer unique string from earlier
footer_full_start = 'x.jsx("footer",{className:`py-32 sm:py-60 px-6 sm:px-24 border-t ${L.border}'
fi = data.find(footer_full_start)
if fi < 0:
    raise SystemExit("footer marker missing")

books_section = (
    '(bk&&bk.length>0)&&x.jsxs("section",{id:"books",className:`py-24 sm:py-32 px-6 sm:px-24 border-t ${L.border}`,children:['
    'x.jsxs("div",{className:"max-w-6xl mx-auto space-y-16",children:['
    'x.jsxs("div",{className:"text-center space-y-4",children:['
    'x.jsx("p",{className:`text-[11px] font-black uppercase tracking-[0.4em] ${L.muted}`,children:"Books"}),'
    'x.jsx("h2",{className:`text-[clamp(2rem,5vw,3.5rem)] ${L.heading}`,children:"Get the Book."}),'
    'x.jsx("p",{className:`text-base sm:text-lg italic ${L.muted}`,children:"Practical education from analysis to execution."})'
    "]}),"
    'x.jsx("div",{className:"grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10",children:bk.map(B=>x.jsxs("article",{className:"space-y-6",children:['
    'B.cover_image?x.jsx("div",{className:"aspect-[3/4] overflow-hidden border border-white/10",children:x.jsx("img",{src:emAsset(B.cover_image),alt:B.title||"Book cover",className:"w-full h-full object-cover"})}):'
    'x.jsx("div",{className:`aspect-[3/4] border flex items-center justify-center ${L.border}`,children:x.jsx("span",{className:`text-[10px] uppercase tracking-widest ${L.muted}`,children:"Book"})}),'
    'x.jsxs("div",{className:"space-y-3",children:['
    'x.jsx("h3",{className:`text-2xl font-serif font-black italic ${L.heading}`,children:B.title}),'
    'B.description&&x.jsx("p",{className:`text-sm leading-relaxed ${L.muted}`,children:B.description}),'
    'x.jsx("a",{href:B.sale_url,target:"_blank",rel:"noopener noreferrer",'
    'className:"inline-flex items-center text-[10px] font-black uppercase tracking-widest text-brand-cyan hover:text-white transition-colors",children:"Buy Now →"})'
    "]})"
    "]},B.id))"
    "})"
    "]})"
    "]}),"
)

data = data[:fi] + books_section + data[fi:]
print("  public books section inserted")
check("public books")

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
keys = [
    "backend/books/list.php",
    "backend/books/save.php",
    "backend/books/delete.php",
    'j==="books"',
    '["books","Books"]',
    "onSaveBook:SB",
    "Get the Book.",
    "Featured (hero CTA sale link)",
    'setBmOpen(!0)',
    '(bk||[]).length>1?"Get Books":"Get Book"',
    "LIBRARY",
]
print("\n=== VERIFICATION ===")
ok = True
for k in keys:
    present = k in data
    print(f"{'YES' if present else 'NO '} {k}")
    ok = ok and present

path.write_text(data, encoding="utf-8")
print("DONE" if ok else "MISSING KEYS")
sys.exit(0 if ok else 1)
