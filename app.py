import streamlit as st
import json, os, random, math, time
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client

# ── Storage (Supabase) ─────────────────────────────────────────────────────────
SUPABASE_URL = "https://rsqlheptlhmfeamemvsn.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def get_db():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def list_classes():
    res = get_db().table("classes").select("id").execute()
    return sorted(r["id"] for r in res.data)

def load_class(name):
    res = get_db().table("classes").select("data").eq("id", name).execute()
    return res.data[0]["data"] if res.data else None

def save_class(name, data):
    get_db().table("classes").upsert({"id": name, "data": data}).execute()

def delete_class(name):
    get_db().table("classes").delete().eq("id", name).execute()

def new_student(name):
    return {"name": name, "participation": 0, "grades": [], "notes": ""}

def avg(lst):         return sum(lst)/len(lst) if lst else None
def grade_letter(g):  return "A" if g>=90 else "B" if g>=80 else "C" if g>=70 else "D" if g>=60 else "F"
def grade_color(g):   return "#22c55e" if g>=90 else "#86efac" if g>=80 else "#eab308" if g>=70 else "#f97316" if g>=60 else "#ef4444"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Teacher's Toolkit", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.stApp { background: #f8fafc; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px; }

section[data-testid="stSidebar"] { background: #18212f !important; }
section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] strong { color: #f1f5f9 !important; }

.card {
    background: #fff; border-radius: 14px; padding: 22px 24px;
    border: 1px solid #e2e8f0; margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.picked-name {
    font-size: 3.2rem; font-weight: 800; text-align: center;
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; padding: 20px 0 8px; line-height: 1.15;
}
.rolling-name {
    font-size: 2rem; font-weight: 700; text-align: center;
    color: #94a3b8; padding: 24px 0; letter-spacing: -0.5px;
}
.timer-display {
    font-size: 6.5rem; font-weight: 800; text-align: center;
    font-variant-numeric: tabular-nums; letter-spacing: -4px;
    line-height: 1; padding: 12px 0;
}
.desk {
    background: #fff; border: 2px solid #e2e8f0; border-radius: 10px;
    padding: 10px 6px; text-align: center; font-weight: 600;
    font-size: 0.8rem; color: #1e293b; min-height: 50px;
    display: flex; align-items: center; justify-content: center;
}
.empty-state {
    background: #fff; border-radius: 14px; border: 2px dashed #e2e8f0;
    text-align: center; padding: 48px 24px; color: #94a3b8;
}

/* Metrics */
div[data-testid="stMetricValue"] { font-size: 1.9rem !important; font-weight: 700 !important; color: #6366f1 !important; }
div[data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #94a3b8 !important; text-transform: uppercase; letter-spacing: .5px; }

/* Buttons */
.stButton > button { border-radius: 9px !important; font-weight: 600 !important; border: 1.5px solid #e2e8f0 !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    border: none !important; color: #fff !important;
    box-shadow: 0 2px 8px rgba(99,102,241,.25) !important;
}
.stButton > button[kind="primary"]:hover { opacity:.9 !important; transform:translateY(-1px) !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: #243044 !important; border-color: #334155 !important; color: #cbd5e1 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover { background: #6366f1 !important; border-color: #6366f1 !important; color:#fff !important; }

/* Progress */
.stProgress > div > div { background: linear-gradient(90deg,#6366f1,#8b5cf6) !important; border-radius: 99px !important; }
.stProgress > div { background: #e2e8f0 !important; border-radius: 99px !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background:#f1f5f9; border-radius:12px; padding:4px; gap:2px; }
.stTabs [data-baseweb="tab"] { border-radius:8px !important; font-weight:600; color:#64748b; }
.stTabs [aria-selected="true"] { background:white !important; color:#6366f1 !important; box-shadow:0 1px 3px rgba(0,0,0,.1) !important; }

/* Forms */
.stForm { border: 1px solid #e2e8f0 !important; border-radius: 14px !important; padding: 16px !important; }
div[data-testid="stForm"] { border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; background: white; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {"page": "home", "current_class": None, "picked": None, "seating": None}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
def go(page, cls=None):
    st.session_state.page = page
    if cls is not None:
        st.session_state.current_class = cls
        st.session_state.picked = None
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    if st.button("🎓 Teacher's Toolkit", use_container_width=True):
        go("home")
    st.divider()

    classes = list_classes()
    if classes:
        st.markdown("**My Classes**")
        for c in classes:
            d = load_class(c)
            n = len(d["students"]) if d else 0
            label = f"{'▸ ' if st.session_state.current_class == c else ''}{c}  ·  {n}"
            if st.button(label, key=f"sb_{c}", use_container_width=True):
                go("class", c)
        st.divider()

    with st.form("new_class_form", clear_on_submit=True):
        st.markdown("**New Class**")
        nc_name = st.text_input("Class name", placeholder="e.g.  Math 10A", label_visibility="collapsed")
        if st.form_submit_button("＋  Create class", type="primary", use_container_width=True):
            nc_name = nc_name.strip()
            if nc_name and nc_name not in list_classes():
                save_class(nc_name, {"name": nc_name, "students": [], "created": str(date.today())})
                go("class", nc_name)
            elif nc_name in list_classes():
                st.warning("Already exists.")

    st.divider()
    if st.button("⏱  Timer", use_container_width=True): go("timer")

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    st.markdown("# 🎓 Teacher's Toolkit")
    st.caption("Manage classes, track grades and participation, generate seating charts.")
    st.divider()

    classes = list_classes()
    if not classes:
        st.markdown("""
        <div class="empty-state">
          <div style="font-size:2.5rem">📚</div>
          <div style="font-size:1.2rem;font-weight:700;color:#475569;margin:12px 0 6px">No classes yet</div>
          <div>Create your first class in the sidebar.</div>
        </div>""", unsafe_allow_html=True)
    else:
        cols = st.columns(min(3, len(classes)))
        for i, c in enumerate(classes):
            d = load_class(c)
            students = d["students"] if d else []
            n = len(students)
            picks = sum(s["participation"] for s in students)
            avgs  = [avg([g["score"] for g in s["grades"]]) for s in students if s["grades"]]
            ca    = avg(avgs)
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class="card" style="cursor:pointer">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start">
                        <div>
                          <div style="font-size:1.1rem;font-weight:700;color:#1e293b">{c}</div>
                          <div style="color:#94a3b8;font-size:.83rem;margin-top:3px">{n} students · {picks} picks</div>
                        </div>
                        <div style="text-align:right">
                          <div style="font-size:1.7rem;font-weight:800;color:{grade_color(ca) if ca else '#cbd5e1'}">{f"{ca:.1f}" if ca else "—"}</div>
                          <div style="font-size:.7rem;color:#94a3b8">avg</div>
                        </div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Open →", key=f"open_{c}", use_container_width=True):
                        go("class", c)

# ══════════════════════════════════════════════════════════════════════════════
# TIMER
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "timer":
    st.markdown("# ⏱  Classroom Timer")
    left, right = st.columns([1, 2])

    with left:
        with st.form("timer_form"):
            mins  = st.number_input("Minutes", 0, 120, 5)
            secs  = st.number_input("Seconds", 0, 59,  0)
            label = st.text_input("Done message", "⏰  Time is up!")
            start = st.form_submit_button("▶  Start", type="primary", use_container_width=True)

    with right:
        slot = st.empty()
        total = int(mins * 60 + secs)

        def show_time(rem, tot, lbl, done=False):
            if done:
                slot.markdown(f'<div class="card" style="text-align:center;padding:40px"><div class="timer-display" style="color:#ef4444;font-size:2rem">{lbl}</div></div>', unsafe_allow_html=True)
                return
            pct = rem / tot if tot else 0
            col = "#22c55e" if pct > .5 else "#eab308" if pct > .2 else "#ef4444"
            m, s = divmod(rem, 60)
            slot.markdown(f"""
            <div class="card" style="text-align:center;padding:40px 24px">
              <div class="timer-display" style="color:{col}">{m:02d}:{s:02d}</div>
              <div style="background:#f1f5f9;border-radius:99px;height:10px;margin:16px 0 12px">
                <div style="background:{col};width:{pct*100:.1f}%;height:100%;border-radius:99px;transition:width .8s ease"></div>
              </div>
              <div style="color:#94a3b8;font-size:.9rem">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        show_time(total, total, label)
        if start and total > 0:
            for rem in range(total, -1, -1):
                show_time(rem, total, label)
                time.sleep(1)
            show_time(0, total, label, done=True)

# ══════════════════════════════════════════════════════════════════════════════
# CLASS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "class" and st.session_state.current_class:
    cname    = st.session_state.current_class
    cls      = load_class(cname)
    if not cls: st.error("Class not found."); st.stop()
    students = cls["students"]

    # ── Header ─────────────────────────────────────────────────────────────────
    h1, h2 = st.columns([5, 1])
    with h1: st.markdown(f"# 📚  {cname}")
    with h2:
        if st.button("🗑  Delete class", key="del_cls"):
            st.session_state["confirm_del"] = True

    if st.session_state.get("confirm_del"):
        st.warning(f"**Delete {cname}?** This cannot be undone.")
        y, n = st.columns(2)
        with y:
            if st.button("Yes, delete", type="primary"):
                delete_class(cname)
                st.session_state.confirm_del = False
                go("home")
        with n:
            if st.button("Cancel"):
                st.session_state.confirm_del = False
                st.rerun()

    # ── Stats ──────────────────────────────────────────────────────────────────
    total_picks = sum(s["participation"] for s in students)
    all_avgs    = [avg([g["score"] for g in s["grades"]]) for s in students if s["grades"]]
    class_avg   = avg(all_avgs)
    grade_count = sum(len(s["grades"]) for s in students)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students",      len(students))
    m2.metric("Total Picks",   total_picks)
    m3.metric("Grade Entries", grade_count)
    m4.metric("Class Average", f"{class_avg:.1f}" if class_avg else "—")
    st.divider()

    # ── Tabs ───────────────────────────────────────────────────────────────────
    t_students, t_pick, t_grades_in, t_report, t_seating, t_participation = st.tabs([
        "👤 Students", "🎲 Pick", "📝 Enter Grades", "📊 Report", "🪑 Seating", "🏆 Participation"
    ])

    # ══ STUDENTS ══════════════════════════════════════════════════════════════
    with t_students:
        left, right = st.columns([1, 2])

        with left:
            # ── Add students (form prevents reactive issues) ──────────────────
            with st.form("add_students_form", clear_on_submit=True):
                st.markdown("**Add students**")
                st.caption("One name per line, or just one name.")
                bulk = st.text_area("Names", height=140, placeholder="Alice Johnson\nBob Smith\nCarla Lee", label_visibility="collapsed")
                submitted = st.form_submit_button("＋  Add students", type="primary", use_container_width=True)
                if submitted:
                    added = 0
                    for line in bulk.strip().splitlines():
                        name = line.strip()
                        if name and not any(s["name"].lower() == name.lower() for s in students):
                            students.append(new_student(name))
                            added += 1
                    if added:
                        save_class(cname, cls)
                        st.success(f"Added {added} student(s)!")
                        st.rerun()
                    elif bulk.strip():
                        st.info("All those names are already in the class.")

            st.divider()
            st.download_button(
                "⬇  Export as JSON",
                data=json.dumps(cls, indent=2),
                file_name=f"{cname}.json",
                mime="application/json",
                use_container_width=True,
            )

        with right:
            if not students:
                st.markdown('<div class="empty-state"><div style="font-size:2rem">👈</div><div style="font-weight:600;color:#475569;margin:8px 0 4px">Add students on the left</div><div>Type one name per line and click Add.</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f"**{len(students)} students**")
                for i, s in enumerate(students):
                    g_vals = [g["score"] for g in s["grades"]]
                    a      = avg(g_vals)
                    with st.expander(f"**{s['name']}** — avg {f'{a:.1f} ({grade_letter(a)})' if a else 'no grades'} · {s['participation']} picks"):
                        col_note, col_del = st.columns([4, 1])
                        with col_note:
                            with st.form(f"note_form_{i}", clear_on_submit=False):
                                note_val = st.text_input("Note", value=s.get("notes",""), placeholder="e.g. sits at front, needs extra help", label_visibility="collapsed")
                                if st.form_submit_button("Save note"):
                                    s["notes"] = note_val
                                    save_class(cname, cls)
                                    st.success("Saved.")
                        with col_del:
                            if st.button("Remove", key=f"rm_{i}"):
                                students.pop(i)
                                save_class(cname, cls)
                                st.rerun()
                        if g_vals:
                            st.caption(f"High: {max(g_vals):.1f}  ·  Low: {min(g_vals):.1f}  ·  {len(g_vals)} assignments")

    # ══ PICK STUDENT ══════════════════════════════════════════════════════════
    with t_pick:
        if not students:
            st.info("Add students in the Students tab first.")
        else:
            col_ctrl, col_out = st.columns([1, 2])
            with col_ctrl:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("#### 🎲 Random Picker")
                st.caption("Students with fewer picks have higher odds of being chosen.")
                do_pick = st.button("Pick a student!", type="primary", use_container_width=True, key="do_pick")
                if st.session_state.picked:
                    if st.button("Pick again ↺", use_container_width=True, key="pick_again"):
                        do_pick = True
                    if st.button("Clear", use_container_width=True, key="pick_clear"):
                        st.session_state.picked = None
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col_out:
                slot = st.empty()

                if do_pick:
                    counts  = [s["participation"] for s in students]
                    max_c   = max(counts) if any(c > 0 for c in counts) else 0
                    weights = [(max_c - c + 1) ** 1.5 for c in counts]
                    chosen  = random.choices(students, weights=weights, k=1)[0]
                    names   = [s["name"] for s in students]

                    for i in range(24):
                        slot.markdown(f'<div class="card" style="text-align:center"><div class="rolling-name">🎲 {random.choice(names)}</div></div>', unsafe_allow_html=True)
                        time.sleep(0.04 + (i / 24) ** 2.2 * 0.28)

                    chosen["participation"] += 1
                    save_class(cname, cls)
                    st.session_state.picked = chosen["name"]

                if st.session_state.picked:
                    s = next((x for x in students if x["name"] == st.session_state.picked), None)
                    if s:
                        g_vals = [g["score"] for g in s["grades"]]
                        a      = avg(g_vals)
                        slot.markdown(f"""
                        <div class="card" style="text-align:center;padding:28px">
                          <div style="font-size:.8rem;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:#94a3b8">Selected</div>
                          <div class="picked-name">{s["name"]}</div>
                          <div style="display:flex;justify-content:center;gap:36px;padding:8px 0 4px">
                            <div>
                              <div style="font-size:1.6rem;font-weight:700;color:#6366f1">{s["participation"]}</div>
                              <div style="font-size:.75rem;color:#94a3b8">times picked</div>
                            </div>
                            <div>
                              <div style="font-size:1.6rem;font-weight:700;color:{grade_color(a) if a else '#cbd5e1'}">{f"{a:.1f}" if a else "—"}</div>
                              <div style="font-size:.75rem;color:#94a3b8">grade avg</div>
                            </div>
                            <div>
                              <div style="font-size:1.6rem;font-weight:700;color:#6366f1">{len(g_vals)}</div>
                              <div style="font-size:.75rem;color:#94a3b8">assignments</div>
                            </div>
                          </div>
                          {f'<div style="margin-top:12px;background:#f8fafc;border-radius:8px;padding:8px 14px;color:#64748b;font-size:.88rem">📝 {s["notes"]}</div>' if s.get("notes") else ""}
                        </div>""", unsafe_allow_html=True)

    # ══ ENTER GRADES ══════════════════════════════════════════════════════════
    with t_grades_in:
        if not students:
            st.info("Add students in the Students tab first.")
        else:
            top_l, top_r = st.columns([1, 1])
            with top_l:
                asgn_name  = st.text_input("Assignment name", placeholder="e.g.  Chapter 3 Quiz")
            with top_r:
                max_pts = st.number_input("Max points", 1, 10000, 100)

            if not asgn_name:
                st.info("Enter an assignment name above to start.")
            else:
                st.markdown(f"**Scores for: {asgn_name}** *(out of {max_pts})*")
                with st.form("grade_entry_form", clear_on_submit=True):
                    grade_inputs = {}
                    cols2 = st.columns(2)
                    for i, s in enumerate(students):
                        with cols2[i % 2]:
                            grade_inputs[s["name"]] = st.number_input(
                                s["name"], 0.0, float(max_pts),
                                value=None, step=0.5, key=f"gi_{s['name']}",
                                placeholder="leave blank to skip"
                            )
                    if st.form_submit_button("💾  Save grades", type="primary", use_container_width=True):
                        saved = 0
                        for s in students:
                            val = grade_inputs.get(s["name"])
                            if val is not None:
                                s["grades"].append({
                                    "assignment": asgn_name,
                                    "score":  round(val / max_pts * 100, 1),
                                    "raw":    val,
                                    "max":    max_pts,
                                    "date":   str(date.today()),
                                })
                                saved += 1
                        save_class(cname, cls)
                        st.success(f"Saved {saved} grade(s) for **{asgn_name}**.")
                        st.rerun()

    # ══ GRADE REPORT ══════════════════════════════════════════════════════════
    with t_report:
        if not any(s["grades"] for s in students):
            st.info("No grades recorded yet. Use the Enter Grades tab.")
        else:
            # Distribution
            buckets = {"A":0,"B":0,"C":0,"D":0,"F":0}
            for s in students:
                a = avg([g["score"] for g in s["grades"]])
                if a: buckets[grade_letter(a)] += 1

            col_chart, col_table = st.columns([1, 2])
            with col_chart:
                colors = {"A":"#22c55e","B":"#86efac","C":"#eab308","D":"#f97316","F":"#ef4444"}
                fig = go.Figure(go.Bar(
                    x=list(buckets.keys()), y=list(buckets.values()),
                    marker_color=[colors[l] for l in buckets],
                    text=list(buckets.values()), textposition="outside",
                ))
                fig.update_layout(
                    title="Grade Distribution", plot_bgcolor="white", paper_bgcolor="white",
                    font_family="Inter", height=260, margin=dict(t=40,b=0,l=0,r=0),
                    showlegend=False, xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="#f1f5f9", rangemode="tozero"),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_table:
                rows = []
                for s in sorted(students, key=lambda x: -(avg([g["score"] for g in x["grades"]]) or -1)):
                    gs = [g["score"] for g in s["grades"]]
                    if not gs: continue
                    a = avg(gs)
                    rows.append({"Name":s["name"], "Avg":f"{a:.1f}", "Grade":grade_letter(a),
                                 "Assignments":len(gs), "Best":f"{max(gs):.1f}", "Lowest":f"{min(gs):.1f}"})
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=260)

            # Per-assignment breakdown
            all_asgns = list(dict.fromkeys(g["assignment"] for s in students for g in s["grades"]))
            if all_asgns:
                st.divider()
                st.markdown("#### Assignment breakdown")
                sel = st.selectbox("Assignment", all_asgns)
                if sel:
                    arows = sorted(
                        [{"Name":s["name"],"Score":next((g["score"] for g in s["grades"] if g["assignment"]==sel),None)} for s in students],
                        key=lambda x: -(x["Score"] or -1)
                    )
                    arows = [r for r in arows if r["Score"] is not None]
                    scores = [r["Score"] for r in arows]
                    names_asgn = [r["Name"] for r in arows]
                    fig2 = px.bar(
                        x=names_asgn, y=scores, text=[f"{s:.0f}" for s in scores],
                        color=scores, color_continuous_scale=["#ef4444","#eab308","#22c55e"],
                        range_color=[0,100], title=sel, labels={"x":"","y":"Score (%)"},
                    )
                    fig2.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
                        height=280, margin=dict(t=40,b=0,l=0,r=0), showlegend=False,
                        coloraxis_showscale=False, xaxis=dict(showgrid=False),
                        yaxis=dict(range=[0,112], showgrid=True, gridcolor="#f1f5f9"),
                    )
                    fig2.update_traces(textposition="outside")
                    st.plotly_chart(fig2, use_container_width=True)
                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("Average",   f"{avg(scores):.1f}")
                    c2.metric("Highest",   f"{max(scores):.1f}")
                    c3.metric("Lowest",    f"{min(scores):.1f}")
                    c4.metric("Submitted", len(scores))

    # ══ SEATING CHART ══════════════════════════════════════════════════════════
    with t_seating:
        if not students:
            st.info("Add students first.")
        else:
            ctrl, chart = st.columns([1, 3])
            with ctrl:
                cols_n = st.slider("Columns", 2, 8, min(4, len(students)), key="sc_cols")
                if st.button("🔀  Shuffle seats", type="primary", use_container_width=True):
                    st.session_state.seating = [s["name"] for s in random.sample(students, len(students))]
                    st.rerun()
            with chart:
                names = st.session_state.seating or [s["name"] for s in students]
                st.markdown('<p style="text-align:center;color:#94a3b8;font-size:.78rem;font-weight:600;letter-spacing:2px">▼ &nbsp; FRONT &nbsp; ▼</p>', unsafe_allow_html=True)
                for r in range(math.ceil(len(names) / cols_n)):
                    row = names[r*cols_n:(r+1)*cols_n]
                    rcols = st.columns(cols_n)
                    for i, name in enumerate(row):
                        with rcols[i]:
                            st.markdown(f'<div class="desk">{name}</div>', unsafe_allow_html=True)
                    st.write("")
                st.markdown('<p style="text-align:center;color:#94a3b8;font-size:.78rem;font-weight:600;letter-spacing:2px">▲ &nbsp; BACK &nbsp; ▲</p>', unsafe_allow_html=True)

    # ══ PARTICIPATION ══════════════════════════════════════════════════════════
    with t_participation:
        if not students:
            st.info("No students yet.")
        else:
            board, pie_col = st.columns([2, 1])
            total_p  = sum(s["participation"] for s in students) or 1
            sorted_s = sorted(students, key=lambda s: -s["participation"])
            max_p    = sorted_s[0]["participation"] or 1

            with board:
                for i, s in enumerate(sorted_s):
                    medal = ["🥇","🥈","🥉"][i] if i < 3 else f"**#{i+1}**"
                    share = s["participation"] / total_p * 100
                    bc1, bc2 = st.columns([5, 1])
                    with bc1:
                        st.markdown(f"{medal} &nbsp; **{s['name']}**  <span style='color:#94a3b8;font-size:.8rem'>{share:.0f}%</span>", unsafe_allow_html=True)
                        st.progress(s["participation"] / max_p)
                    with bc2:
                        st.markdown(f"<div style='text-align:right;padding-top:6px;font-weight:700;color:#6366f1'>{s['participation']}</div>", unsafe_allow_html=True)

            with pie_col:
                picked_students = [s for s in students if s["participation"] > 0]
                if picked_students:
                    fig3 = px.pie(
                        names=[s["name"] for s in picked_students],
                        values=[s["participation"] for s in picked_students],
                        hole=0.45,
                    )
                    fig3.update_layout(font_family="Inter", height=280, margin=dict(t=10,b=0,l=0,r=0), showlegend=False)
                    fig3.update_traces(textinfo="label+percent", textfont_size=11)
                    st.plotly_chart(fig3, use_container_width=True)

                if st.button("↺  Reset all pick counts"):
                    for s in students: s["participation"] = 0
                    save_class(cname, cls)
                    st.rerun()
