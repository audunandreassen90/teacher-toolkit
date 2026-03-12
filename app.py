import streamlit as st
import json, os, random, math
from datetime import date

DATA_DIR = os.path.expanduser("~/.teacher_toolkit")
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="Teacher's Toolkit", page_icon="🎓", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0f1117; color: #e0e0e0; }
.card {
    background: #1a1d27; border-radius: 12px; padding: 20px;
    border: 1px solid #2a2d3a; margin-bottom: 12px;
}
.big-name {
    font-size: 2.8rem; font-weight: 700; text-align: center;
    background: linear-gradient(135deg, #4ade80, #22d3ee);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    padding: 16px 0;
}
.stat { font-size: 1.8rem; font-weight: 700; color: #4ade80; }
.stat-label { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
.grade-a { color: #4ade80; font-weight: 700; }
.grade-b { color: #86efac; font-weight: 600; }
.grade-c { color: #fde047; font-weight: 600; }
.grade-d { color: #fb923c; font-weight: 600; }
.grade-f { color: #f87171; font-weight: 600; }
.stButton>button {
    border-radius: 8px; border: 1px solid #2a2d3a;
    background: #1e2130; color: #e0e0e0; font-weight: 600;
    transition: all 0.15s;
}
.stButton>button:hover { background: #2a2d3a; border-color: #4ade80; color: #4ade80; }
div[data-testid="stMetricValue"] { color: #4ade80; font-size: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Data helpers ───────────────────────────────────────────────────────────────
def class_path(name): return os.path.join(DATA_DIR, f"{name}.json")

def list_classes():
    return sorted(f[:-5] for f in os.listdir(DATA_DIR) if f.endswith(".json"))

def load_class(name):
    p = class_path(name)
    if not os.path.exists(p): return None
    with open(p) as f: return json.load(f)

def save_class(name, data):
    with open(class_path(name), "w") as f: json.dump(data, f, indent=2)

def avg(lst): return sum(lst)/len(lst) if lst else None

def grade_letter(g):
    if g >= 90: return "A"
    if g >= 80: return "B"
    if g >= 70: return "C"
    if g >= 60: return "D"
    return "F"

def grade_class(g):
    if g >= 90: return "grade-a"
    if g >= 80: return "grade-b"
    if g >= 70: return "grade-c"
    if g >= 60: return "grade-d"
    return "grade-f"

def grade_color(g):
    if g >= 90: return "#4ade80"
    if g >= 80: return "#86efac"
    if g >= 70: return "#fde047"
    if g >= 60: return "#fb923c"
    return "#f87171"

# ── Session state ─────────────────────────────────────────────────────────────
if "current_class" not in st.session_state: st.session_state.current_class = None
if "picked"        not in st.session_state: st.session_state.picked = None
if "page"          not in st.session_state: st.session_state.page = "home"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Teacher's Toolkit")
    st.divider()

    classes = list_classes()
    if classes:
        st.markdown("**Your Classes**")
        for c in classes:
            cls = load_class(c)
            n = len(cls["students"]) if cls else 0
            if st.button(f"📚 {c}  `{n} students`", key=f"cls_{c}", use_container_width=True):
                st.session_state.current_class = c
                st.session_state.page = "class"
                st.session_state.picked = None
        st.divider()

    st.markdown("**New Class**")
    new_name = st.text_input("Class name", key="new_class_input", label_visibility="collapsed", placeholder="e.g. Math 10A")
    if st.button("+ Create Class", use_container_width=True):
        if new_name and new_name not in classes:
            save_class(new_name, {"name": new_name, "students": [], "created": str(date.today())})
            st.session_state.current_class = new_name
            st.session_state.page = "class"
            st.rerun()

    st.divider()
    if st.button("⏱ Timer", use_container_width=True):
        st.session_state.page = "timer"

# ── Home ───────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown("# 🎓 Teacher's Toolkit")
    st.markdown("Create a class in the sidebar to get started.")

    if list_classes():
        st.markdown("### Your Classes")
        cols = st.columns(3)
        for i, c in enumerate(list_classes()):
            cls = load_class(c)
            n = len(cls["students"]) if cls else 0
            picks = sum(s["participation"] for s in cls["students"]) if cls else 0
            with cols[i % 3]:
                st.markdown(f"""
                <div class="card">
                  <div style="font-size:1.2rem;font-weight:700;color:#e0e0e0">{c}</div>
                  <div style="color:#666;margin-top:4px">{n} students · {picks} picks</div>
                </div>""", unsafe_allow_html=True)

# ── Timer ──────────────────────────────────────────────────────────────────────
elif st.session_state.page == "timer":
    st.markdown("# ⏱ Classroom Timer")
    col1, col2 = st.columns([1, 2])
    with col1:
        mins = st.number_input("Minutes", min_value=0, max_value=120, value=5)
        secs = st.number_input("Seconds", min_value=0, max_value=59, value=0)
        label = st.text_input("Label", value="Time is up!")
    with col2:
        total = int(mins * 60 + secs)
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:40px">
          <div class="big-name">{mins:02d}:{secs:02d}</div>
          <div style="color:#666">{label}</div>
          <div style="margin-top:20px;color:#888;font-size:0.9rem">
            Copy this into your browser for a real countdown:<br>
            <code style="color:#4ade80">https://www.bigtimer.net/?minutes={mins}&seconds={secs}</code>
          </div>
        </div>""", unsafe_allow_html=True)

# ── Class view ─────────────────────────────────────────────────────────────────
elif st.session_state.page == "class" and st.session_state.current_class:
    cname = st.session_state.current_class
    cls   = load_class(cname)
    if cls is None:
        st.error("Class not found."); st.stop()

    students = cls["students"]

    # Header row
    col_title, col_del = st.columns([5, 1])
    with col_title:
        st.markdown(f"# 📚 {cname}")
    with col_del:
        if st.button("🗑 Delete Class", type="secondary"):
            st.session_state["confirm_delete"] = True

    if st.session_state.get("confirm_delete"):
        st.warning(f'Delete "{cname}"? This cannot be undone.')
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, delete", type="primary"):
                os.remove(class_path(cname))
                st.session_state.current_class = None
                st.session_state.page = "home"
                st.session_state["confirm_delete"] = False
                st.rerun()
        with c2:
            if st.button("Cancel"):
                st.session_state["confirm_delete"] = False
                st.rerun()

    # Stats
    total_picks  = sum(s["participation"] for s in students)
    total_grades = sum(len(s["grades"]) for s in students)
    all_avgs     = [avg([g["score"] for g in s["grades"]]) for s in students if s["grades"]]
    class_avg    = avg(all_avgs) if all_avgs else None

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students",      len(students))
    m2.metric("Total Picks",   total_picks)
    m3.metric("Grade Entries", total_grades)
    m4.metric("Class Average", f"{class_avg:.1f}" if class_avg else "—")

    st.divider()

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎲 Pick Student", "📊 Grades", "👥 Seating", "📋 Students", "🏆 Participation", "📝 Enter Grades"
    ])

    # ── Tab 1: Pick ────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Random Student Picker")
        if not students:
            st.info("Add students in the Students tab first.")
        else:
            if st.button("🎲 Pick a Student!", type="primary", use_container_width=True):
                counts  = [s["participation"] for s in students]
                max_c   = max(counts) if counts else 0
                weights = [(max_c - c + 1)**1.5 for c in counts]
                chosen  = random.choices(students, weights=weights, k=1)[0]
                chosen["participation"] += 1
                save_class(cname, cls)
                st.session_state.picked = chosen["name"]

            if st.session_state.picked:
                s = next((x for x in students if x["name"] == st.session_state.picked), None)
                if s:
                    grades = [g["score"] for g in s["grades"]]
                    a      = avg(grades)
                    st.markdown(f'<div class="big-name">⭐ {s["name"]}</div>', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Participation", s["participation"])
                    c2.metric("Grade Average", f"{a:.1f}" if a else "—")
                    c3.metric("Assignments",   len(grades))
                    if s["notes"]:
                        st.info(f"📝 {s['notes']}")

    # ── Tab 2: Grades ──────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Grade Report")
        if not students or not any(s["grades"] for s in students):
            st.info("No grades recorded yet. Use the 'Enter Grades' tab.")
        else:
            # Class distribution
            all_letters = {"A":0,"B":0,"C":0,"D":0,"F":0}
            for s in students:
                g = avg([x["score"] for x in s["grades"]])
                if g is not None: all_letters[grade_letter(g)] += 1

            st.markdown("#### Grade Distribution")
            cols = st.columns(5)
            colors = {"A":"#4ade80","B":"#86efac","C":"#fde047","D":"#fb923c","F":"#f87171"}
            for i, (letter, cnt) in enumerate(all_letters.items()):
                with cols[i]:
                    st.markdown(f"""
                    <div class="card" style="text-align:center;border-color:{colors[letter]}">
                      <div style="font-size:2rem;font-weight:700;color:{colors[letter]}">{letter}</div>
                      <div style="font-size:1.4rem;color:#e0e0e0">{cnt}</div>
                    </div>""", unsafe_allow_html=True)

            st.divider()
            st.markdown("#### Student Averages")

            rows = []
            for s in sorted(students, key=lambda x: -(avg([g["score"] for g in x["grades"]]) or -1)):
                grades = [g["score"] for g in s["grades"]]
                if not grades: continue
                a = avg(grades)
                rows.append({
                    "Name": s["name"],
                    "Average": f"{a:.1f}",
                    "Grade": grade_letter(a),
                    "Assignments": len(grades),
                    "High": f"{max(grades):.1f}",
                    "Low":  f"{min(grades):.1f}",
                })
            if rows:
                import pandas as pd
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Assignment breakdown
            all_a = []
            seen  = set()
            for s in students:
                for g in s["grades"]:
                    if g["assignment"] not in seen:
                        all_a.append(g["assignment"])
                        seen.add(g["assignment"])

            if all_a:
                st.divider()
                st.markdown("#### Assignment Breakdown")
                selected = st.selectbox("Assignment", all_a)
                if selected:
                    arows = []
                    for s in students:
                        score = next((g["score"] for g in s["grades"] if g["assignment"]==selected), None)
                        if score is not None:
                            arows.append({"Name": s["name"], "Score": f"{score:.1f}", "Grade": grade_letter(score)})
                    if arows:
                        arows_sorted = sorted(arows, key=lambda x: -float(x["Score"]))
                        import pandas as pd
                        st.dataframe(pd.DataFrame(arows_sorted), use_container_width=True, hide_index=True)
                        scores = [float(r["Score"]) for r in arows]
                        c1,c2,c3 = st.columns(3)
                        c1.metric("Average", f"{avg(scores):.1f}")
                        c2.metric("Highest", f"{max(scores):.1f}")
                        c3.metric("Lowest",  f"{min(scores):.1f}")

    # ── Tab 3: Seating ─────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Random Seating Chart")
        if not students:
            st.info("Add students first.")
        else:
            cols_n = st.slider("Seats per row", 2, 8, 4)
            if st.button("🔀 Generate New Seating", type="primary"):
                st.session_state["seating"] = [s["name"] for s in random.sample(students, len(students))]

            names = st.session_state.get("seating", [s["name"] for s in students])
            st.markdown('<div style="text-align:center;color:#666;margin-bottom:8px;font-size:0.9rem">▼ FRONT ▼</div>', unsafe_allow_html=True)
            rows = math.ceil(len(names) / cols_n)
            for r in range(rows):
                row_names = names[r*cols_n:(r+1)*cols_n]
                cols_row  = st.columns(cols_n)
                for i, name in enumerate(row_names):
                    with cols_row[i]:
                        st.markdown(f"""
                        <div style="background:#1e2130;border:1px solid #2a2d3a;border-radius:8px;
                             padding:12px;text-align:center;font-weight:600;color:#e0e0e0;">
                          {name}
                        </div>""", unsafe_allow_html=True)
            st.markdown('<div style="text-align:center;color:#666;margin-top:8px;font-size:0.9rem">▲ BACK ▲</div>', unsafe_allow_html=True)

    # ── Tab 4: Students ────────────────────────────────────────────────────────
    with tab4:
        st.markdown("### Manage Students")
        col_add, col_list = st.columns([1, 2])

        with col_add:
            st.markdown("**Add Student**")
            new_student = st.text_input("Name", key="new_student_input", placeholder="Full name")
            if st.button("+ Add", type="primary", use_container_width=True):
                if new_student:
                    if any(s["name"].lower() == new_student.lower() for s in students):
                        st.warning("Already in class.")
                    else:
                        students.append({"name": new_student, "participation": 0, "grades": [], "notes": ""})
                        save_class(cname, cls)
                        st.rerun()

        with col_list:
            st.markdown("**Student List**")
            for i, s in enumerate(students):
                c1, c2, c3 = st.columns([3, 2, 1])
                with c1:
                    st.markdown(f"**{s['name']}**")
                    note = st.text_input("Note", value=s["notes"], key=f"note_{i}", label_visibility="collapsed", placeholder="Add note...")
                    if note != s["notes"]:
                        s["notes"] = note
                        save_class(cname, cls)
                with c2:
                    grades = [g["score"] for g in s["grades"]]
                    a = avg(grades)
                    st.caption(f"Avg: {f'{a:.1f}' if a else '—'}  |  Picks: {s['participation']}")
                with c3:
                    if st.button("✕", key=f"del_{i}"):
                        students.pop(i)
                        save_class(cname, cls)
                        st.rerun()
                st.divider()

    # ── Tab 5: Participation ───────────────────────────────────────────────────
    with tab5:
        st.markdown("### Participation Board")
        if not students:
            st.info("No students yet.")
        else:
            total_p = sum(s["participation"] for s in students) or 1
            sorted_s = sorted(students, key=lambda s: -s["participation"])
            for i, s in enumerate(sorted_s):
                share = s["participation"] / total_p * 100
                medal = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}."
                pct   = s["participation"] / (sorted_s[0]["participation"] or 1)
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"{medal} **{s['name']}**")
                    st.progress(pct)
                with c2:
                    st.metric("Picks", s["participation"])
                with c3:
                    st.metric("Share", f"{share:.0f}%")

    # ── Tab 6: Enter Grades ────────────────────────────────────────────────────
    with tab6:
        st.markdown("### Enter Grades")
        if not students:
            st.info("Add students first.")
        else:
            assignment = st.text_input("Assignment name", placeholder="e.g. Chapter 3 Quiz")
            if assignment:
                st.markdown(f"**Entering grades for: {assignment}**")
                grade_inputs = {}
                cols = st.columns(2)
                for i, s in enumerate(students):
                    with cols[i % 2]:
                        grade_inputs[s["name"]] = st.number_input(
                            s["name"], min_value=0.0, max_value=100.0,
                            value=None, step=0.5, key=f"grade_{s['name']}",
                            placeholder="Score (0–100)"
                        )

                if st.button("💾 Save Grades", type="primary"):
                    saved = 0
                    for s in students:
                        val = grade_inputs.get(s["name"])
                        if val is not None:
                            s["grades"].append({"assignment": assignment, "score": float(val), "date": str(date.today())})
                            saved += 1
                    save_class(cname, cls)
                    st.success(f"Saved {saved} grade(s) for '{assignment}'.")
