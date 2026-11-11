import { useCallback, useEffect, useRef, useState, type ChangeEvent } from "react";
import { createPortal } from "react-dom";
import { createNote, deleteNote, exportNotes, importNotes, listNotes, updateNote } from "../services/notes.service";
import type { Note, NoteInput } from "../types";

const EMPTY: NoteInput = { title: "", content: "", tags: "", pinned: false };
const errText = (e: unknown) => (e instanceof Error ? e.message : String(e));
const fmt = (iso: string) => (iso ? new Date(iso + "Z").toLocaleString() : "");

function PrintArea({ items }: { items: Note[] }) {
  return createPortal(
    <div className="print-area">
      {items.map((n, i) => (
        <article key={`${n.id}-${i}`}>
          <h1>{n.title || "Untitled"}</h1>
          <p className="print-meta">{n.tags && <>Tags: {n.tags} · </>}{fmt(n.updated_at)}</p>
          <div className="print-body">{n.content}</div>
        </article>
      ))}
    </div>,
    document.body,
  );
}

export default function Notes() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<number | "new" | null>(null);
  const [form, setForm] = useState<NoteInput>(EMPTY);
  const [info, setInfo] = useState("");
  const [error, setError] = useState("");
  const [confirmDel, setConfirmDel] = useState(false);
  const [printItems, setPrintItems] = useState<Note[] | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    try { setNotes(await listNotes(q)); } catch (e) { setError(errText(e)); }
  }, [q]);
  useEffect(() => { const t = setTimeout(load, 200); return () => clearTimeout(t); }, [load]);

  // Print: render the print area, open the print dialog, then clean up.
  useEffect(() => {
    const done = () => setPrintItems(null);
    window.addEventListener("afterprint", done);
    return () => window.removeEventListener("afterprint", done);
  }, []);
  useEffect(() => {
    if (!printItems) return;
    const t = setTimeout(() => window.print(), 150);
    return () => clearTimeout(t);
  }, [printItems]);

  function flash(message: string) { setInfo(message); setError(""); }

  function open(n: Note) {
    setSelected(n.id);
    setForm({ title: n.title, content: n.content, tags: n.tags, pinned: n.pinned });
    setConfirmDel(false); setInfo(""); setError("");
  }
  function startNew() { setSelected("new"); setForm(EMPTY); setConfirmDel(false); setInfo(""); setError(""); }

  async function save() {
    try {
      if (selected === "new") {
        const n = await createNote(form);
        setSelected(n.id);
      } else if (selected !== null) {
        await updateNote(selected, form);
      }
      flash("Saved ✓");
      await load();
    } catch (e) { setError(errText(e)); }
  }

  async function remove() {
    if (typeof selected !== "number") return;
    if (!confirmDel) { setConfirmDel(true); return; }
    try {
      await deleteNote(selected);
      setSelected(null); setForm(EMPTY); setConfirmDel(false);
      flash("Note deleted");
      await load();
    } catch (e) { setError(errText(e)); }
  }

  async function doExport() {
    try {
      const r = await exportNotes();
      flash(`Exported ${r.count} notes to: ${r.path}`);
    } catch (e) { setError(errText(e)); }
  }

  async function doImport(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    try {
      const r = await importNotes(await file.text());
      flash(`Imported ${r.imported} notes`);
      await load();
    } catch (err) { setError(errText(err)); }
  }

  const printCurrent = () => {
    const base = typeof selected === "number" ? notes.find((n) => n.id === selected) : undefined;
    setPrintItems([{ id: base?.id ?? 0, ...form, created_at: base?.created_at ?? "", updated_at: base?.updated_at ?? "" }]);
  };

  return (
    <>
      <div className="page-head">
        <h1>Notes</h1>
        <div className="toolbar">
          <button className="btn" onClick={startNew}>+ New note</button>
          <button className="btn ghost" onClick={() => fileRef.current?.click()}>Import CSV</button>
          <button className="btn ghost" onClick={doExport}>Export CSV</button>
          <button className="btn ghost" disabled={!notes.length} onClick={() => setPrintItems(notes)}>Print all / PDF</button>
          <input ref={fileRef} type="file" accept=".csv,text/csv" hidden onChange={doImport} />
        </div>
      </div>
      {error && <div className="error">{error}</div>}
      {info && <div className="info">{info}</div>}

      <div className="notes-grid">
        <div className="card notes-list">
          <input placeholder="Search notes…" value={q} onChange={(e) => setQ(e.target.value)} />
          {notes.length === 0 && <p className="muted">{q ? "No matching notes." : "No notes yet. Click “New note”."}</p>}
          {notes.map((n) => (
            <button key={n.id} className={selected === n.id ? "note-item active" : "note-item"} onClick={() => open(n)}>
              <strong>{n.pinned && "📌 "}{n.title || "Untitled"}</strong>
              <span className="muted snippet">{n.content.slice(0, 80) || "—"}</span>
              {n.tags && <span className="tags">{n.tags}</span>}
            </button>
          ))}
        </div>

        <div className="card editor">
          {selected === null ? (
            <p className="muted">Select a note, or create a new one.</p>
          ) : (
            <>
              <input className="title-input" placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
              <textarea placeholder="Write your note…" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
              <div className="row2">
                <input placeholder="Tags (comma separated)" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} />
                <label className="check"><input type="checkbox" checked={form.pinned} onChange={(e) => setForm({ ...form, pinned: e.target.checked })} /> Pin to top</label>
              </div>
              <div className="toolbar">
                <button className="btn" onClick={save}>Save</button>
                <button className="btn ghost" onClick={printCurrent}>Print / PDF</button>
                {typeof selected === "number" && (
                  <button className="btn ghost danger" onClick={remove}>{confirmDel ? "Click again to confirm" : "Delete"}</button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
      {printItems && <PrintArea items={printItems} />}
    </>
  );
}
