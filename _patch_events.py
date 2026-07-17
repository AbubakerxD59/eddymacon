#!/usr/bin/env python3
"""Patch the live admin SPA to add Events CRUD."""
from pathlib import Path
import subprocess
import sys

path = Path("/Applications/MAMP/htdocs/eddymacon/assets/index-Bpoe2-CA.js")
data = path.read_text(encoding="utf-8")

URL_PREFIX = '(/\\/admin(?:\\/index\\.php)?$/.test((location.pathname || "").replace(/\\/+$/, "")) ? "../" : "")'


def check(label):
    path.write_text(data, encoding="utf-8")
    r = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"PARSE FAIL after {label}:", r.stderr[-800:])
        sys.exit(1)
    print(f"OK {label}")


def must_replace(old, new, label, count=1):
    global data
    found = data.count(old)
    if found < count:
        raise SystemExit(f"{label}: expected >= {count}, found {found}\nOLD[:200]={old[:200]!r}")
    data = data.replace(old, new, count if count != -1 else found)
    print(f"  {label} ({found})")


# ---------------------------------------------------------------------------
# 1) Menu keys + nav labels + header title
# ---------------------------------------------------------------------------
MENU_OLD = '[["content", "Content"], ["design", "Design"], ["books", "Books"], ["inquiries", "Contacts"], ["deals", "Deals"]]'
MENU_NEW = '[["content", "Content"], ["design", "Design"], ["books", "Books"], ["events", "Events"], ["inquiries", "Contacts"], ["deals", "Deals"]]'

MENU_KEYS_OLD = '["content", "design", "books", "inquiries", "deals"]'
MENU_KEYS_NEW = '["content", "design", "books", "events", "inquiries", "deals"]'

HEADER_OLD = 'children: j === "content" ? "Content" : j === "design" ? "Design" : j === "books" ? "Books" : j === "inquiries" ? "Contacts" : "Deals"'
HEADER_NEW = 'children: j === "content" ? "Content" : j === "design" ? "Design" : j === "books" ? "Books" : j === "events" ? "Events" : j === "inquiries" ? "Contacts" : "Deals"'

must_replace(MENU_KEYS_OLD, MENU_KEYS_NEW, "menu keys", count=2)
must_replace(MENU_OLD, MENU_NEW, "nav menus", count=3)
must_replace(HEADER_OLD, HEADER_NEW, "header title")

# ---------------------------------------------------------------------------
# 2) Admin component props + local event form state
# ---------------------------------------------------------------------------
must_replace(
    "e_ = ({ content: s, onSave: n, inquiries: l, onDeleteInquiry: r, deals: da, onDeleteDeal: rd, books: bk, onSaveBook: sb, onDeleteBook: db, onLogout: c, addToast: h }) =>",
    "e_ = ({ content: s, onSave: n, inquiries: l, onDeleteInquiry: r, deals: da, onDeleteDeal: rd, books: bk, onSaveBook: sb, onDeleteBook: db, events: ev, onSaveEvent: se, onDeleteEvent: deEv, onLogout: c, addToast: h }) =>",
    "admin props",
)

must_replace(
    "[bf, setBf] = Pe.useState(null), [bkBusy, setBkBusy] = Pe.useState(!1), D = C => { C.preventDefault(), h(\"Use /admin login\") };",
    "[bf, setBf] = Pe.useState(null), [bkBusy, setBkBusy] = Pe.useState(!1), [ef, setEf] = Pe.useState(null), [evBusy, setEvBusy] = Pe.useState(!1), D = C => { C.preventDefault(), h(\"Use /admin login\") };",
    "event form state",
)

# ---------------------------------------------------------------------------
# 3) Events panel + modal
# ---------------------------------------------------------------------------
inp = 'className: "w-full bg-brand-dark border border-white/10 p-4 text-white text-xs"'
txa = 'className: "w-full bg-brand-dark border border-white/10 p-4 text-white h-28 text-xs italic"'
lab = 'className: "text-[10px] font-bold text-gray-600 uppercase"'
file_cls = (
    'className: "block w-full text-[10px] text-gray-400 file:mr-4 file:py-2 file:px-4 '
    "file:border-0 file:text-[10px] file:font-black file:uppercase file:tracking-widest "
    'file:bg-gold-500 file:text-black hover:file:bg-white"'
)
sel = 'className: "w-full bg-brand-dark border border-white/10 p-4 text-white text-xs"'

empty_event = (
    '{id:0,title:"",description:"",cover_image:"",thumbnail:"",event_date:"",event_time:"",'
    'price:"",location:"",type:"physical",webinar_link:"",media:[],coverPreview:null,thumbPreview:null,coverFile:null,thumbFile:null}'
)

events_panel = (
    'j === "events" ? x.jsxs("div", { className: "space-y-8 animate-reveal-up", children: ['
    'x.jsxs("div", { className: "flex flex-wrap items-center justify-between gap-4", children: ['
    'x.jsxs("div", { className: "space-y-2", children: ['
    'x.jsx("h2", { className: "text-xl font-black uppercase tracking-[0.4em] text-gold-500", children: "Events" }),'
    'x.jsx("p", { className: "text-[10px] text-gray-500 uppercase tracking-widest", children: "Create and manage events, cover images, and gallery media." })'
    "]}),"
    f'x.jsx("button", {{ type: "button", onClick: () => setEf({empty_event}), '
    'className: "px-6 py-3 bg-gold-500 text-black text-[10px] font-black uppercase tracking-widest hover:bg-white transition-all", children: "+ Add Event" })'
    "]}),"
    '(ev == null ? void 0 : ev.length) === 0 ? x.jsx("div", { className: "p-20 border border-white/5 text-center text-gray-600 uppercase tracking-widest italic", children: "No events yet. Add your first event." }) : '
    'x.jsx("div", { className: "space-y-4", children: (ev || []).map(E => x.jsxs("div", { className: "p-6 sm:p-8 bg-brand-accent border border-white/5 flex flex-col sm:flex-row justify-between items-start gap-6", children: ['
    'x.jsxs("div", { className: "flex gap-5 min-w-0 flex-1", children: ['
    'E.cover_image || E.thumbnail ? x.jsx("img", { src: emAsset(E.cover_image || E.thumbnail), alt: E.title || "Cover", className: "w-20 h-20 object-cover border border-white/10 shrink-0" }) : '
    'x.jsx("div", { className: "w-20 h-20 border border-white/10 bg-brand-dark/60 shrink-0 flex items-center justify-center text-[9px] text-gray-600 uppercase tracking-widest", children: "No image" }),'
    'x.jsxs("div", { className: "space-y-2 min-w-0", children: ['
    'x.jsxs("div", { className: "flex flex-wrap items-center gap-3", children: ['
    'x.jsx("h4", { className: "text-xl font-serif font-black italic truncate", children: E.title }),'
    'x.jsx("span", { className: "text-[9px] font-black uppercase tracking-widest text-black bg-gold-500 px-2 py-0.5", children: E.type || "physical" })'
    "]}),"
    'x.jsx("p", { className: "text-[11px] font-mono text-gray-400", children: [E.event_date || "", E.event_time ? " · " + String(E.event_time).slice(0, 5) : ""].join("") }),'
    'E.location && x.jsx("p", { className: "text-sm text-gray-500 truncate", children: E.location }),'
    'E.description && x.jsx("p", { className: "text-sm text-gray-400 line-clamp-2", children: E.description })'
    "]})]}),"
    'x.jsxs("div", { className: "flex items-center gap-2 shrink-0", children: ['
    'x.jsx("button", { type: "button", onClick: () => setEf({ id: E.id, title: E.title || "", description: E.description || "", cover_image: E.cover_image || "", thumbnail: E.thumbnail || "", '
    'event_date: E.event_date || "", event_time: String(E.event_time || "").slice(0, 5), price: E.price == null ? "" : E.price, location: E.location || "", type: E.type || "physical", '
    'webinar_link: E.webinar_link || "", media: (E.media || []).map((m, i) => ({ type: m.type || "image", media_url: m.media_url || "", sort_order: m.sort_order ?? i })), '
    'coverPreview: null, thumbPreview: null, coverFile: null, thumbFile: null }), '
    'className: "px-4 py-2 border border-white/10 text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-gold-500 hover:border-gold-500/40 transition-colors", children: "Edit" }),'
    'x.jsx("button", { type: "button", disabled: emDelBusy === E.id, onClick: () => deEv(E.id), title: "Delete", '
    'className: "p-3 text-gray-700 hover:text-red-500 transition-colors disabled:opacity-50", children: x.jsx(d0, { size: 22 }) })'
    "]})"
    "]}, E.id))"
    "})"
    "]})"
    " : "
)

event_modal = (
    'ef && x.jsxs("div", { className: "em-admin-modal fixed inset-0 z-[3000] flex items-center justify-center", children: ['
    'x.jsx("div", { className: "absolute inset-0 bg-black/80 backdrop-blur-sm", onClick: () => { if (!evBusy) { ef.coverPreview && URL.revokeObjectURL(ef.coverPreview); ef.thumbPreview && URL.revokeObjectURL(ef.thumbPreview); setEf(null) } } }),'
    'x.jsxs("div", { className: "em-admin-modal-dialog relative flex flex-col w-full max-w-2xl h-full max-h-screen bg-brand-accent border border-white/10 shadow-2xl overflow-hidden", onClick: e => e.stopPropagation(), children: ['
    'x.jsxs("div", { className: "flex items-center justify-between gap-4 shrink-0 px-8 sm:px-10 py-6 border-b border-white/10", children: ['
    'x.jsx("h3", { className: "text-2xl font-serif font-black italic text-gold-500", children: ef.id ? "Edit Event" : "Add Event" }),'
    'x.jsx("button", { type: "button", disabled: evBusy, onClick: () => { ef.coverPreview && URL.revokeObjectURL(ef.coverPreview); ef.thumbPreview && URL.revokeObjectURL(ef.thumbPreview); setEf(null) }, className: "text-gray-500 hover:text-white transition-colors", title: "Close", children: x.jsx(m0, { size: 28 }) })'
    "]}),"
    'x.jsxs("form", { className: "flex-1 min-h-0 overflow-y-auto px-8 sm:px-10 py-6 space-y-6", onSubmit: async e => { e.preventDefault(); if (evBusy) return; setEvBusy(!0); try { '
    'let cover = ef.cover_image || "", thumb = ef.thumbnail || ""; '
    'if (ef.coverFile) { const fd = new FormData; fd.append("file", ef.coverFile); const R = await fetch("../backend/media/upload.php", { method: "POST", credentials: "same-origin", body: fd }); const J = await R.json(); if (!J.ok) throw new Error(J.error || "Cover upload failed"); cover = J.path || (J.filename ? "uploads/" + J.filename : ""); if (!cover) throw new Error("Upload missing cover path") } '
    'if (ef.thumbFile) { const fd = new FormData; fd.append("file", ef.thumbFile); const R = await fetch("../backend/media/upload.php", { method: "POST", credentials: "same-origin", body: fd }); const J = await R.json(); if (!J.ok) throw new Error(J.error || "Thumbnail upload failed"); thumb = J.path || (J.filename ? "uploads/" + J.filename : ""); if (!thumb) throw new Error("Upload missing thumbnail path") } '
    'const media = []; for (const m of ef.media || []) { if (m.file) { const fd = new FormData; fd.append("file", m.file); const R = await fetch("../backend/media/upload.php", { method: "POST", credentials: "same-origin", body: fd }); const J = await R.json(); if (!J.ok) throw new Error(J.error || "Media upload failed"); const path = J.path || (J.filename ? "uploads/" + J.filename : ""); if (!path) throw new Error("Upload missing media path"); media.push({ type: m.type || "image", media_url: path, sort_order: m.sort_order || 0 }) } else if (m.media_url) { media.push({ type: m.type || "image", media_url: m.media_url, sort_order: m.sort_order || 0 }) } } '
    'await se({ id: ef.id || 0, title: ef.title, description: ef.description, cover_image: cover, thumbnail: thumb, event_date: ef.event_date, event_time: ef.event_time, price: ef.price === "" || ef.price == null ? null : Number(ef.price), location: ef.location, type: ef.type || "physical", webinar_link: ef.webinar_link, media }); '
    'ef.coverPreview && URL.revokeObjectURL(ef.coverPreview); ef.thumbPreview && URL.revokeObjectURL(ef.thumbPreview); setEf(null) '
    '} catch (err) { window.toastr ? toastr.error(err && err.message || "Could not save event", "Error") : h(err && err.message || "Could not save event") } finally { setEvBusy(!1) } }, children: ['
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Title" }}), '
    f'x.jsx("input", {{ {inp}, required: !0, value: ef.title || "", onChange: C => setEf(P => ({{ ...P, title: C.target.value }})) }})] }}),'
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Description" }}), '
    f'x.jsx("textarea", {{ {txa}, value: ef.description || "", onChange: C => setEf(P => ({{ ...P, description: C.target.value }})) }})] }}),'
    'x.jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-4", children: ['
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Date" }}), '
    f'x.jsx("input", {{ {inp}, required: !0, type: "date", value: ef.event_date || "", onChange: C => setEf(P => ({{ ...P, event_date: C.target.value }})) }})] }}),'
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Time" }}), '
    f'x.jsx("input", {{ {inp}, required: !0, type: "time", value: ef.event_time || "", onChange: C => setEf(P => ({{ ...P, event_time: C.target.value }})) }})] }})'
    "]}),"
    'x.jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-4", children: ['
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Price" }}), '
    f'x.jsx("input", {{ {inp}, type: "number", step: "0.01", min: "0", placeholder: "Leave blank for free", value: ef.price === 0 || ef.price ? ef.price : "", onChange: C => setEf(P => ({{ ...P, price: C.target.value }})) }})] }}),'
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Type" }}), '
    f'x.jsx("select", {{ {sel}, value: ef.type || "physical", onChange: C => setEf(P => ({{ ...P, type: C.target.value }})), children: [x.jsx("option", {{ value: "physical", children: "Physical" }}), x.jsx("option", {{ value: "online", children: "Online" }})] }})] }})'
    "]}),"
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Location" }}), '
    f'x.jsx("input", {{ {inp}, value: ef.location || "", onChange: C => setEf(P => ({{ ...P, location: C.target.value }})) }})] }}),'
    f'x.jsxs("div", {{ className: "space-y-2", children: [x.jsx("label", {{ {lab}, children: "Webinar Link" }}), '
    f'x.jsx("input", {{ {inp}, type: "url", placeholder: "https://...", value: ef.webinar_link || "", onChange: C => setEf(P => ({{ ...P, webinar_link: C.target.value }})) }})] }}),'
    'x.jsxs("div", { className: "grid grid-cols-1 sm:grid-cols-2 gap-6", children: ['
    'x.jsxs("div", { className: "space-y-4", children: ['
    f'x.jsx("label", {{ {lab}, children: "Cover Image" }}),'
    '(ef.coverPreview || ef.cover_image) ? x.jsx("img", { src: ef.coverPreview || emAsset(ef.cover_image), alt: "Cover preview", className: "w-28 h-28 object-cover border border-white/10" }) : null,'
    f'x.jsx("input", {{ type: "file", accept: "image/jpeg,image/png,image/webp,image/gif", {file_cls}, '
    "onChange: C => { const f = C.target.files && C.target.files[0]; if (!f) return; setEf(P => { P && P.coverPreview && URL.revokeObjectURL(P.coverPreview); return { ...P, coverFile: f, coverPreview: URL.createObjectURL(f) } }); C.target.value = \"\" } })"
    "]}),"
    'x.jsxs("div", { className: "space-y-4", children: ['
    f'x.jsx("label", {{ {lab}, children: "Thumbnail" }}),'
    '(ef.thumbPreview || ef.thumbnail) ? x.jsx("img", { src: ef.thumbPreview || emAsset(ef.thumbnail), alt: "Thumbnail preview", className: "w-28 h-28 object-cover border border-white/10" }) : null,'
    f'x.jsx("input", {{ type: "file", accept: "image/jpeg,image/png,image/webp,image/gif", {file_cls}, '
    "onChange: C => { const f = C.target.files && C.target.files[0]; if (!f) return; setEf(P => { P && P.thumbPreview && URL.revokeObjectURL(P.thumbPreview); return { ...P, thumbFile: f, thumbPreview: URL.createObjectURL(f) } }); C.target.value = \"\" } })"
    "]})"
    "]}),"
    'x.jsxs("div", { className: "space-y-4", children: ['
    f'x.jsx("label", {{ {lab}, children: "Gallery Media" }}),'
    '(ef.media || []).length > 0 && x.jsx("div", { className: "space-y-3", children: (ef.media || []).map((m, idx) => x.jsxs("div", { className: "flex items-center gap-3 p-3 border border-white/10", children: ['
    'm.preview || (m.type === "image" && m.media_url) ? x.jsx("img", { src: m.preview || emAsset(m.media_url), alt: "Media", className: "w-12 h-12 object-cover border border-white/10 shrink-0" }) : '
    'x.jsx("div", { className: "w-12 h-12 border border-white/10 flex items-center justify-center text-[9px] uppercase text-gray-600 shrink-0", children: m.type || "media" }),'
    'x.jsxs("div", { className: "min-w-0 flex-1 space-y-1", children: ['
    f'x.jsx("select", {{ {sel}, value: m.type || "image", onChange: C => setEf(P => {{ const media = [...(P.media || [])]; media[idx] = {{ ...media[idx], type: C.target.value }}; return {{ ...P, media }} }}), children: [x.jsx("option", {{ value: "image", children: "Image" }}), x.jsx("option", {{ value: "video", children: "Video" }})] }}),'
    'x.jsx("p", { className: "text-[10px] text-gray-500 truncate", children: m.media_url || (m.file && m.file.name) || "New file" })'
    "]}),"
    'x.jsx("button", { type: "button", onClick: () => setEf(P => { const media = [...(P.media || [])]; const rem = media.splice(idx, 1)[0]; rem && rem.preview && URL.revokeObjectURL(rem.preview); return { ...P, media } }), className: "text-[10px] uppercase tracking-widest text-red-400 hover:text-red-300", children: "Remove" })'
    "]}, idx))"
    "}),"
    f'x.jsx("input", {{ type: "file", accept: "image/jpeg,image/png,image/webp,image/gif", {file_cls}, '
    "onChange: C => { const f = C.target.files && C.target.files[0]; if (!f) return; setEf(P => ({ ...P, media: [...(P.media || []), { type: \"image\", media_url: \"\", file: f, preview: URL.createObjectURL(f), sort_order: (P.media || []).length }] })); C.target.value = \"\" } }),"
    f'x.jsxs("div", {{ className: "flex gap-2", children: [x.jsx("input", {{ {inp}, type: "url", placeholder: "Or paste video/image URL", id: "em-media-url-input" }}), '
    'x.jsx("button", { type: "button", onClick: () => { const el = document.getElementById("em-media-url-input"); const url = el && el.value.trim(); if (!url) return; setEf(P => ({ ...P, media: [...(P.media || []), { type: /\\.(mp4|webm|mov)(\\?|$)/i.test(url) ? "video" : "image", media_url: url, sort_order: (P.media || []).length }] })); if (el) el.value = "" }, className: "px-4 py-3 border border-white/10 text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-gold-500 shrink-0", children: "Add URL" })] })'
    "]}),"
    'x.jsxs("div", { className: "flex gap-3 pt-4 border-t border-white/10", children: ['
    'x.jsx("button", { type: "submit", disabled: evBusy, className: "px-8 py-3 bg-gold-500 text-black text-[10px] font-black uppercase tracking-widest hover:bg-white transition-all disabled:opacity-60", children: evBusy ? "Saving..." : "Save Event" }),'
    'x.jsx("button", { type: "button", disabled: evBusy, onClick: () => { ef.coverPreview && URL.revokeObjectURL(ef.coverPreview); ef.thumbPreview && URL.revokeObjectURL(ef.thumbPreview); setEf(null) }, '
    'className: "px-6 py-3 border border-white/10 text-[10px] font-black uppercase tracking-widest text-gray-500 hover:text-white transition-colors", children: "Cancel" })'
    "]})"
    "]})"
    "]})"
    "]})"
)

# Insert events panel: books ): CONTENT  →  books ): events ): CONTENT
content_marker = '] }, B.id)) })] }) : x.jsxs("div", { className: "grid grid-cols-1 gap-8 animate-reveal-up"'
ci = data.find(content_marker)
if ci < 0:
    raise SystemExit("books->content marker missing")
# Replace the ` : x.jsxs("div"...` after books close with ` : ` + events_panel + `x.jsxs("div"...`
# content_marker is `] }, B.id)) })] }) : x.jsxs(...)`
prefix = '] }, B.id)) })] }) : '
if data[ci:ci + len(prefix)] != prefix:
    raise SystemExit(f"prefix mismatch: {data[ci:ci+len(prefix)]!r}")
rest_start = 'x.jsxs("div", { className: "grid grid-cols-1 gap-8 animate-reveal-up"'
data = data[:ci] + prefix + events_panel + rest_start + data[ci + len(content_marker):]
print("  events panel inserted")

# Insert event modal before fm modal (after book modal)
fm_marker = 'fm && x.jsxs("div", { className: "em-admin-modal fixed inset-0 z-[3000] flex items-center justify-center"'
fi = data.find(fm_marker)
if fi < 0:
    raise SystemExit("fm modal marker missing")
data = data[:fi] + event_modal + ", " + data[fi:]
print("  event modal inserted")
check("events admin ui")

# ---------------------------------------------------------------------------
# 4) App state, fetch, save/delete handlers, mount props
# ---------------------------------------------------------------------------
must_replace(
    "const [s, n] = Pe.useState(_n), [l, r] = Pe.useState([]), [da, setDa] = Pe.useState([]), [bk, setBk] = Pe.useState([]), [c, h] = Pe.useState([]),",
    "const [s, n] = Pe.useState(_n), [l, r] = Pe.useState([]), [da, setDa] = Pe.useState([]), [bk, setBk] = Pe.useState([]), [ev, setEv] = Pe.useState([]), [c, h] = Pe.useState([]),",
    "app events state",
)

must_replace(
    'else console.debug("[Books] No books") } catch (bkErr) { console.error("[Books] Fetch error:", bkErr) } } catch (Re) { console.error("[App] Fatal Error during Initialization:", Re) }',
    'else console.debug("[Books] No books") } catch (bkErr) { console.error("[Books] Fetch error:", bkErr) }; '
    'console.debug("[Events] Fetching events..."); try { const er = await fetch(' + URL_PREFIX + ' + "backend/events/list.php", { credentials: "same-origin" }), ej = await er.json(); '
    "if (ej && ej.ok && Array.isArray(ej.events)) { setEv(ej.events); console.debug(`[Events] Found ${ej.events.length} events.`) } "
    'else console.debug("[Events] No events") } catch (evErr) { console.error("[Events] Fetch error:", evErr) } } catch (Re) { console.error("[App] Fatal Error during Initialization:", Re) }',
    "events fetch",
)

must_replace(
    'Save Error"); throw err } }, V = async de => { de.preventDefault(); if (emDBusy)',
    'Save Error"); throw err } }, '
    "GE = async de => { try { const R = await fetch("
    + URL_PREFIX
    + ' + "backend/events/delete.php", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: de }) }), J = await R.json(); '
    'if (J && J.ok) { setEv(Re => Re.filter(Ut => Ut.id !== de)); window.toastr ? toastr.success("Event deleted", "Success") : D("Record Purged") } '
    'else { window.toastr ? toastr.error(J && J.error || "Delete failed", "Error") : D("Delete Error") } '
    '} catch { window.toastr ? toastr.error("Delete failed", "Error") : D("Delete Error") } }, '
    "SE = async de => { try { const R = await fetch("
    + URL_PREFIX
    + ' + "backend/events/save.php", { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify(de) }), J = await R.json(); '
    'if (!J || !J.ok) throw new Error(J && J.error || "Could not save event"); '
    "const saved = J.event; setEv(Re => { const rest = Re.filter(Ut => Ut.id !== saved.id); const next = [saved, ...rest]; "
    "return next.slice().sort((a, b) => String(a.event_date || \"\").localeCompare(String(b.event_date || \"\")) || String(a.event_time || \"\").localeCompare(String(b.event_time || \"\")) || a.id - b.id) }); "
    'window.toastr ? toastr.success(de.id ? "Event updated" : "Event added", "Success") : D("Event saved"); return saved '
    '} catch (err) { window.toastr ? toastr.error(err && err.message || "Could not save event", "Error") : D(err && err.message || "Save Error"); throw err } }, '
    "V = async de => { de.preventDefault(); if (emDBusy)",
    "GE/SE handlers",
)

must_replace(
    "deals: da, onDeleteDeal: GD, books: bk, onSaveBook: SB, onDeleteBook: GB, onLogout:",
    "deals: da, onDeleteDeal: GD, books: bk, onSaveBook: SB, onDeleteBook: GB, events: ev, onSaveEvent: SE, onDeleteEvent: GE, onLogout:",
    "mount events props",
)
check("events handlers")

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
keys = [
    "backend/events/list.php",
    "backend/events/save.php",
    "backend/events/delete.php",
    'j === "events"',
    '["events", "Events"]',
    "onSaveEvent: SE",
    "Save Event",
    "+ Add Event",
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
