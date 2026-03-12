import streamlit as st
import json, os, random, math, time
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Storage ────────────────────────────────────────────────────────────────────
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def class_path(name): return os.path.join(DATA_DIR, f"{name}.json")
def list_classes(): return sorted(f[:-5] for f in os.listdir(DATA_DIR) if f.endswith(".json"))
def load_class(name):
    p = class_path(name)
    return json.load(open(p)) if os.path.exists(p) else None
def save_class(name, data):
    with open(class_path(name), "w") as f: json.dump(data, f, indent=2)
def avg(lst): return sum(lst)/len(lst) if lst else None
def grade_letter(g):
    return "A" if g>=90 else "B" if g>=80 else "C" if g>=70 else "D" if g>=60 else "F"
def grade_color(g):
    return "#22c55e" if g>=90 else "#86efac" if g>=80 else "#eab308" if g>=70 else "#f97316" if g>=60 else "#ef4444"

# ── Config ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Teacher's Toolkit", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* Background */
.stApp { background: #f8fafc; }
section[data-testid="stSidebar"] { background: #1e293b !important; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* Cards */
.card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}
.card-dark {
    background: #1e293b;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #334155;
    margin-bottom: 16px;
}

/* Picked name display */
.picked-name {
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 24px 0 12px;
    line-height: 1.1;
}
.rolling-name {
    font-size: 2.2rem;
    font-weight: 700;
    text-align: center;
    color: #64748b;
    padding: 20px 0;
}

/* Timer */
.timer-display {
    font-size: 7rem;
    font-weight: 800;
    text-align: center;
    font-variant-numeric: tabular-nums;
    letter-spacing: -4px;
    padding: 20px 0;
    line-height: 1;
}
.timer-green { color: #22c55e; }
.timer-yellow { color: #eab308; }
.timer-red { color: #ef4444; }

/* Desk seats */
.desk {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 6px;
    text-align: center;
    font-weight: 600;
    font-size: 0.82rem;
    color: #1e293b;
    min-height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}

/* Metric overrides */
div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #6366f1 !important;
}
div[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.8rem !important; }

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    border: 1.5px solid #e2e8f0 !important;
    transition: all 0.15s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: #334155 !important;
    border-color: #475569 !important;
    color: #e2e8f0 !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #6366f1 !important;
    border-color: #6366f1 !important;
}

/* Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; border-radius: 99px; }
.stProgress > div { background: #e2e8f0 !important; border-radius: 99px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #f1f5f9; border-radius: 12px; padding: 4px; gap: 2px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-weight: 600; color: #64748b; }
.stTabs [aria-selected="true"] { background: white !important; color: #6366f1 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select {
    border-radius: 8px !important;
    border: 1.5px solid #e2e8f0 !important;
}

/* Dataframe */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Badge */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("current_class", None), ("page", "home"), ("picked", None),
             ("timer_running", False), ("seating", None)]:
    if k not in st.session_state: st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Teacher's Toolkit")
    st.markdown("---")

    classes = list_classes()
    if classes:
        st.markdown("**Classes**")
        for c in classes:
            cls = load_class(c)
            n = len(cls["students"]) if cls else 0
            active = "✦ " if st.session_state.current_class == c else "   "
            if st.button(f"{active}{c}  ·  {n} students", key=f"cls_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.page = "class"
                st.session_state.picked = None
                st.rerun()
        st.markdown("---")

    with st.expander("➕ New Class"):
        new_name = st.text_input("Name", key="new_class_input", placeholder="e.g. Math 10A", label_visibility="collapsed")
        if st.button("Create", type="primary", use_container_width=True, key="create_class"):
            if new_name and new_name not in classes:
                save_class(new_name, {"name": new_name, "students": [], "created": str(date.today())})
                st.session_state.current_class = new_name
                st.session_state.page = "class"
                st.session_state.picked = None
                st.rerun()

    st.markdown("---")
    if st.button("⏱  Timer", use_container_width=True):
        st.session_state.page = "timer"
        st.rerun()
    if st.button("🏠  Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    st.markdown("# 🎓 Teacher's Toolkit")
    st.markdown("A simple tool for managing your classes, grades, and participation.")
    st.divider()

    classes = list_classes()
    if not classes:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px">
            <div style="font-size:3rem">📚</div>
            <div style="font-size:1.3rem;font-weight:700;color:#1e293b;margin:12px 0 8px">No classes yet</div>
            <div style="color:#64748b">Create your first class using the sidebar.</div>
        </div>""", unsafe_allow_html=True)
    else:
        cols = st.columns(min(3, len(classes)))
        for i, c in enumerate(classes):
            cls = load_class(c)
            students = cls["students"] if cls else []
            n = len(students)
            picks = sum(s["participation"] for s in students)
            all_avgs = [avg([g["score"] for g in s["grades"]]) for s in students if s["grades"]]
            class_avg = avg(all_avgs)
            with cols[i % 3]:
                avg_str = f"{class_avg:.1f}" if class_avg else "—"
                color = grade_color(class_avg) if class_avg else "#94a3b8"
                if st.button(f"### {c}", key=f"home_cls_{c}", use_container_width=True):
                    st.session_state.current_class = c
                    st.session_state.page = "class"
                    st.rerun()
                st.markdown(f"""
                <div class="card" style="margin-top:-8px">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                      <div style="font-size:1.1rem;font-weight:700;color:#1e293b">{c}</div>
                      <div style="color:#64748b;font-size:0.85rem;margin-top:2px">{n} students · {picks} picks</div>
                    </div>
                    <div style="text-align:right">
                      <div style="font-size:1.6rem;font-weight:800;color:{color}">{avg_str}</div>
                      <div style="font-size:0.7rem;color:#94a3b8">class avg</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TIMER
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "timer":
    st.markdown("# ⏱ Classroom Timer")
    c1, _, c2 = st.columns([1, 0.1, 2])

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        mins = st.number_input("Minutes", 0, 120, 5, key="tmins")
        secs = st.number_input("Seconds", 0, 59,  0, key="tsecs")
        label = st.text_input("Message when done", "⏰ Time is up!")
        go_btn    = st.button("▶  Start", type="primary", use_container_width=True)
        stop_btn  = st.button("■  Stop",  use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        display = st.empty()
        total = int(mins * 60 + secs)

        def render_time(remaining, total, lbl, done=False):
            if done:
                display.markdown(f"""
                <div class="card" style="text-align:center;padding:32px">
                  <div class="timer-display timer-red">{lbl}</div>
                </div>""", unsafe_allow_html=True)
                return
            pct = remaining / total if total else 0
            color_cls = "timer-green" if pct > 0.5 else "timer-yellow" if pct > 0.2 else "timer-red"
            m, s = divmod(remaining, 60)
            bar_filled = int(pct * 20)
            bar_html = (
                f'<div style="background:#e2e8f0;border-radius:99px;height:8px;margin-top:16px">'
                f'<div style="background:{"#22c55e" if pct>0.5 else "#eab308" if pct>0.2 else "#ef4444"};'
                f'width:{pct*100:.1f}%;height:100%;border-radius:99px;transition:width 0.5s"></div></div>'
            )
            display.markdown(f"""
            <div class="card" style="text-align:center;padding:32px">
              <div class="timer-display {color_cls}">{m:02d}:{s:02d}</div>
              {bar_html}
              <div style="color:#94a3b8;margin-top:8px;font-size:0.9rem">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        render_time(total, total, label)

        if go_btn and total > 0:
            st.session_state.timer_running = True
            for remaining in range(total, -1, -1):
                if not st.session_state.timer_running: break
                render_time(remaining, total, label)
                time.sleep(1)
            else:
                render_time(0, total, label, done=True)
            st.session_state.timer_running = False

        if stop_btn:
            st.session_state.timer_running = False

# ══════════════════════════════════════════════════════════════════════════════
# CLASS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "class" and st.session_state.current_class:
    cname = st.session_state.current_class
    cls   = load_class(cname)
    if not cls: st.error("Class not found"); st.stop()
    students = cls["students"]

    # Header
    hc1, hc2 = st.columns([5, 1])
    with hc1:
        st.markdown(f"# 📚 {cname}")
    with hc2:
        if st.button("🗑 Delete", key="del_cls"):
            st.session_state["confirm_delete"] = True

    if st.session_state.get("confirm_delete"):
        st.warning(f'Delete **{cname}**? All data will be lost.')
        dc1, dc2 = st.columns(2)
        with dc1:
            if st.button("Yes, delete forever", type="primary"):
                os.remove(class_path(cname))
                st.session_state.current_class = None
                st.session_state.page = "home"
                st.session_state["confirm_delete"] = False
                st.rerun()
        with dc2:
            if st.button("Cancel"):
                st.session_state["confirm_delete"] = False
                st.rerun()

    # Stats bar
    total_picks  = sum(s["participation"] for s in students)
    all_avgs     = [avg([g["score"] for g in s["grades"]]) for s in students if s["grades"]]
    class_avg    = avg(all_avgs)
    total_grades = sum(len(s["grades"]) for s in students)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students",      len(students))
    m2.metric("Total Picks",   total_picks)
    m3.metric("Grade Entries", total_grades)
    m4.metric("Class Average", f"{class_avg:.1f}" if class_avg else "—")
    st.divider()

    # Tabs
    tabs = st.tabs(["🎲 Pick Student", "📝 Enter Grades", "📊 Grade Report", "👥 Seating Chart", "🏆 Participation", "👤 Students"])
    tab_pick, tab_enter, tab_grades, tab_seat, tab_part, tab_students = tabs

    # ── Pick ───────────────────────────────────────────────────────────────────
    with tab_pick:
        if not students:
            st.info("Add students in the Students tab first.")
        else:
            col_btn, col_result = st.columns([1, 2])
            with col_btn:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("#### Random Picker")
                st.caption("Students who haven't been picked recently get higher odds.")
                pick_btn = st.button("🎲 Pick!", type="primary", use_container_width=True, key="pick_btn")
                if st.session_state.picked and st.button("↺ Pick Again", use_container_width=True):
                    pick_btn = True
                st.markdown('</div>', unsafe_allow_html=True)

            with col_result:
                result_slot = st.empty()

                if pick_btn:
                    counts  = [s["participation"] for s in students]
                    max_c   = max(counts) if any(counts) else 0
                    weights = [(max_c - c + 1) ** 1.5 for c in counts]
                    chosen  = random.choices(students, weights=weights, k=1)[0]

                    # Spin animation
                    names = [s["name"] for s in students]
                    for i in range(22):
                        n = random.choice(names)
                        result_slot.markdown(f'<div class="card"><div class="rolling-name">🎲 {n}</div></div>', unsafe_allow_html=True)
                        time.sleep(0.04 + (i / 22) ** 2 * 0.25)

                    chosen["participation"] += 1
                    save_class(cname, cls)
                    st.session_state.picked = chosen["name"]

                if st.session_state.picked:
                    s = next((x for x in students if x["name"] == st.session_state.picked), None)
                    if s:
                        g_list = [g["score"] for g in s["grades"]]
                        a = avg(g_list)
                        result_slot.markdown(f"""
                        <div class="card" style="text-align:center">
                          <div style="color:#94a3b8;font-size:0.85rem;font-weight:600;letter-spacing:1px;text-transform:uppercase">Selected</div>
                          <div class="picked-name">{s["name"]}</div>
                          <div style="display:flex;justify-content:center;gap:32px;padding:12px 0">
                            <div><div style="font-size:1.5rem;font-weight:700;color:#6366f1">{s["participation"]}</div>
                                 <div style="font-size:0.75rem;color:#94a3b8">times picked</div></div>
                            <div><div style="font-size:1.5rem;font-weight:700;color:{grade_color(a) if a else "#94a3b8"}">{f"{a:.1f}" if a else "—"}</div>
                                 <div style="font-size:0.75rem;color:#94a3b8">grade avg</div></div>
                            <div><div style="font-size:1.5rem;font-weight:700;color:#6366f1">{len(g_list)}</div>
                                 <div style="font-size:0.75rem;color:#94a3b8">assignments</div></div>
                          </div>
                          {f'<div style="background:#f1f5f9;border-radius:8px;padding:8px 16px;color:#475569;font-size:0.9rem;margin-top:4px">📝 {s["notes"]}</div>' if s.get("notes") else ""}
                        </div>""", unsafe_allow_html=True)

    # ── Enter Grades ────────────────────────────────────────────────────────────
    with tab_enter:
        if not students:
            st.info("Add students in the Students tab first.")
        else:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("**Assignment**")
                assignment = st.text_input("Name", placeholder="e.g. Chapter 3 Quiz", label_visibility="collapsed", key="asgn_name")
                st.markdown("**Max Score**")
                max_score = st.number_input("Max", 1, 1000, 100, label_visibility="collapsed", key="max_score")
            with c2:
                if assignment:
                    st.markdown(f"**Scores for: {assignment}**")
                    grade_inputs = {}
                    cols2 = st.columns(2)
                    for i, s in enumerate(students):
                        with cols2[i % 2]:
                            grade_inputs[s["name"]] = st.number_input(
                                s["name"], 0.0, float(max_score), value=None,
                                step=0.5, key=f"g_{s['name']}", placeholder="—"
                            )
                    if st.button("💾 Save All Grades", type="primary", use_container_width=True):
                        saved = 0
                        for s in students:
                            val = grade_inputs.get(s["name"])
                            if val is not None:
                                normalized = val / max_score * 100
                                s["grades"].append({
                                    "assignment": assignment,
                                    "score": round(normalized, 1),
                                    "raw": val,
                                    "max": max_score,
                                    "date": str(date.today())
                                })
                                saved += 1
                        save_class(cname, cls)
                        st.success(f"Saved {saved} grade(s) for **{assignment}**.")
                else:
                    st.info("Enter an assignment name to start.")

    # ── Grade Report ────────────────────────────────────────────────────────────
    with tab_grades:
        if not any(s["grades"] for s in students):
            st.info("No grades recorded yet.")
        else:
            # Distribution chart
            all_letters = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            for s in students:
                a = avg([g["score"] for g in s["grades"]])
                if a is not None: all_letters[grade_letter(a)] += 1

            colors_map = {"A": "#22c55e", "B": "#86efac", "C": "#eab308", "D": "#f97316", "F": "#ef4444"}
            fig = go.Figure(go.Bar(
                x=list(all_letters.keys()),
                y=list(all_letters.values()),
                marker_color=[colors_map[l] for l in all_letters],
                text=list(all_letters.values()),
                textposition="outside",
            ))
            fig.update_layout(
                title="Grade Distribution", plot_bgcolor="white", paper_bgcolor="white",
                font_family="Inter", height=280, margin=dict(t=40, b=0, l=0, r=0),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Student table
            rows = []
            for s in sorted(students, key=lambda x: -(avg([g["score"] for g in x["grades"]]) or -1)):
                grades = [g["score"] for g in s["grades"]]
                if not grades: continue
                a = avg(grades)
                rows.append({"Name": s["name"], "Average": f"{a:.1f}", "Letter": grade_letter(a),
                             "Assignments": len(grades), "Highest": f"{max(grades):.1f}", "Lowest": f"{min(grades):.1f}"})
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Assignment breakdown
            all_a = list(dict.fromkeys(g["assignment"] for s in students for g in s["grades"]))
            if all_a:
                st.divider()
                st.markdown("#### Assignment Breakdown")
                selected = st.selectbox("Select assignment", all_a, key="asgn_select")
                if selected:
                    arows = [{"Name": s["name"], "Score": next((g["score"] for g in s["grades"] if g["assignment"]==selected), None)}
                             for s in students]
                    arows = [r for r in arows if r["Score"] is not None]
                    arows = sorted(arows, key=lambda x: -x["Score"])

                    scores = [r["Score"] for r in arows]
                    fig2 = px.bar(
                        x=[r["Name"] for r in arows], y=scores,
                        color=scores, color_continuous_scale=["#ef4444","#eab308","#22c55e"],
                        range_color=[0, 100], labels={"x": "", "y": "Score"},
                        title=selected, text=[f"{s:.0f}" for s in scores]
                    )
                    fig2.update_layout(
                        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
                        height=300, margin=dict(t=40,b=0,l=0,r=0), showlegend=False,
                        coloraxis_showscale=False, xaxis=dict(showgrid=False),
                        yaxis=dict(range=[0, 110], showgrid=True, gridcolor="#f1f5f9")
                    )
                    fig2.update_traces(textposition="outside")
                    st.plotly_chart(fig2, use_container_width=True)

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Average", f"{avg(scores):.1f}")
                    c2.metric("Highest", f"{max(scores):.1f}")
                    c3.metric("Lowest",  f"{min(scores):.1f}")
                    c4.metric("Submitted", len(scores))

    # ── Seating Chart ───────────────────────────────────────────────────────────
    with tab_seat:
        if not students:
            st.info("Add students first.")
        else:
            sc1, sc2 = st.columns([1, 3])
            with sc1:
                cols_n = st.slider("Columns", 2, 8, 4, key="seat_cols")
                if st.button("🔀 Shuffle", type="primary", use_container_width=True):
                    st.session_state.seating = [s["name"] for s in random.sample(students, len(students))]

            with sc2:
                names = st.session_state.seating or [s["name"] for s in students]
                st.markdown('<div style="text-align:center;color:#94a3b8;font-size:0.8rem;font-weight:600;letter-spacing:2px;margin-bottom:12px">▼  FRONT  ▼</div>', unsafe_allow_html=True)
                for r in range(math.ceil(len(names) / cols_n)):
                    row_names = names[r * cols_n:(r + 1) * cols_n]
                    row_cols  = st.columns(cols_n)
                    for i, name in enumerate(row_names):
                        with row_cols[i]:
                            st.markdown(f'<div class="desk">{name}</div>', unsafe_allow_html=True)
                    st.write("")
                st.markdown('<div style="text-align:center;color:#94a3b8;font-size:0.8rem;font-weight:600;letter-spacing:2px;margin-top:4px">▲  BACK  ▲</div>', unsafe_allow_html=True)

    # ── Participation ───────────────────────────────────────────────────────────
    with tab_part:
        if not students:
            st.info("No students yet.")
        else:
            rc1, rc2 = st.columns([2, 1])
            with rc1:
                total_p  = sum(s["participation"] for s in students) or 1
                sorted_s = sorted(students, key=lambda s: -s["participation"])
                for i, s in enumerate(sorted_s):
                    pct   = s["participation"] / (sorted_s[0]["participation"] or 1)
                    share = s["participation"] / total_p * 100
                    medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                    pc1, pc2 = st.columns([4, 1])
                    with pc1:
                        st.markdown(f"{medal} **{s['name']}**")
                        st.progress(float(pct))
                    with pc2:
                        st.markdown(f"<div style='text-align:right;padding-top:8px;color:#6366f1;font-weight:700'>{s['participation']} picks</div>", unsafe_allow_html=True)
            with rc2:
                # Pie chart
                names_p  = [s["name"] for s in students if s["participation"] > 0]
                counts_p = [s["participation"] for s in students if s["participation"] > 0]
                if names_p:
                    fig3 = px.pie(names=names_p, values=counts_p, title="Pick Distribution", hole=0.4)
                    fig3.update_layout(font_family="Inter", height=300, margin=dict(t=40,b=0,l=0,r=0), showlegend=False)
                    fig3.update_traces(textinfo="label+percent")
                    st.plotly_chart(fig3, use_container_width=True)
                if st.button("↺ Reset All Counts", key="reset_part"):
                    for s in students:
                        s["participation"] = 0
                    save_class(cname, cls)
                    st.rerun()

    # ── Students ────────────────────────────────────────────────────────────────
    with tab_students:
        sc1, sc2 = st.columns([1, 2])

        with sc1:
            st.markdown("**Add Students**")
            bulk = st.text_area("One name per line", height=150, placeholder="Alice\nBob\nCharlie", key="bulk_input", label_visibility="collapsed")
            if st.button("+ Add", type="primary", use_container_width=True, key="add_students"):
                added = 0
                for name in bulk.strip().splitlines():
                    name = name.strip()
                    if name and not any(s["name"].lower() == name.lower() for s in students):
                        students.append({"name": name, "participation": 0, "grades": [], "notes": ""})
                        added += 1
                if added:
                    save_class(cname, cls)
                    st.success(f"Added {added} student(s).")
                    st.rerun()

            st.divider()
            st.download_button(
                "⬇ Export Class JSON",
                data=json.dumps(cls, indent=2),
                file_name=f"{cname}.json",
                mime="application/json",
                use_container_width=True
            )

        with sc2:
            st.markdown(f"**{len(students)} Students**")
            for i, s in enumerate(students):
                with st.expander(f"{s['name']}  ·  {len(s['grades'])} grades  ·  {s['participation']} picks"):
                    nc1, nc2 = st.columns([3, 1])
                    with nc1:
                        note = st.text_input("Note", value=s.get("notes", ""), key=f"note_{i}", placeholder="Add a note...")
                        if note != s.get("notes", ""):
                            s["notes"] = note
                            save_class(cname, cls)
                    with nc2:
                        if st.button("Remove", key=f"del_{i}", type="secondary"):
                            students.pop(i)
                            save_class(cname, cls)
                            st.rerun()
                    if s["grades"]:
                        g_vals = [g["score"] for g in s["grades"]]
                        a = avg(g_vals)
                        st.caption(f"Average: **{a:.1f}** ({grade_letter(a)})  ·  High: {max(g_vals):.1f}  ·  Low: {min(g_vals):.1f}")
