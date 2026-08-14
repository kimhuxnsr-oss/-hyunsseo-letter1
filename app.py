import os
import sqlite3
import streamlit as st

# ==========================================
# 0. 기본 설정
# ==========================================

st.set_page_config(
    page_title="현서에게 전하는 이야기 💌",
    page_icon="💌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 관리자 비밀번호
# Replit에서는 Secrets에 ADMIN_PASSWORD를 추가하는 것을 권장
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "0000")

DB_FILE = "answers.db"

# ==========================================
# 1. CSS
# ==========================================

st.markdown(
    """
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    .stApp {
        background-color: #FDFBF7;
        font-family: 'Pretendard',
        -apple-system, BlinkMacSystemFont,
        system-ui, sans-serif;
        color: #4A403A;
    }

    .block-container {
        max-width: 700px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .stTextArea textarea,
    .stTextInput input {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E2D5 !important;
        border-radius: 12px !important;
        color: #333333 !important;
        font-family: 'Pretendard', sans-serif !important;
        font-size: 16px !important;
    }

    .stButton > button {
        background-color: #D8A47F !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #C38E69 !important;
        box-shadow: 0 4px 12px rgba(216, 164, 127, 0.3) !important;
    }

    h1, h2, h3 {
        color: #5C4B43 !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    .thankyou-box {
        background-color: #FFFFFF;
        border: 2px solid #F0E6D8;
        padding: 24px;
        border-radius: 16px;
        margin-top: 20px;
        line-height: 1.7;
        color: #5C4B43;
    }

    .answer-card {
        background-color: #FFFFFF;
        border: 1px solid #F0E6D8;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
    }

    @media (max-width: 600px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. 데이터베이스
# ==========================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            answers TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def save_response(name, answers):
    import json

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO responses (name, answers)
        VALUES (?, ?)
        """,
        (name, json.dumps(answers, ensure_ascii=False)),
    )

    conn.commit()
    conn.close()


def load_responses():
    import json

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, answers, created_at
        FROM responses
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    result = []

    for row in rows:
        result.append(
            {
                "id": row[0],
                "name": row[1],
                "answers": json.loads(row[2]),
                "created_at": row[3],
            }
        )

    return result


init_db()

# ==========================================
# 3. 질문
# ==========================================

QUESTIONS = [
    "당신의 이름은?",
    "당신이 생각하는 '김현서'에게 나란 존재란?",
    "당신이 '김현서'와 알고 지낸 기간은?",
    "그 시간은 당신에게 의미있는 시간이었나요?",
    "‘김현서’에게 상처받은 순간은? (솔직하게 말해줘야 나도 내 감정을 잘 표현할 수 있어!)",
    "‘김현서’의 첫인상은?",
    "‘김현서’란? (당신에게 어떤 친구인지)",
    "당신에게 ‘김현서’란 어떤 존재인가요?",
    "당신에게 ‘김현서’가 힘이 되었던 순간은? (구체적으로)",
    "‘김현서’랑 있으면 이런 게 좋다 (예: 행복했던 순간, 편했던 시간)",
    "‘김현서’의 장점과 단점",
    "졸업 전에 ‘김현서’에게 하고 싶은 말은?",
]

# ==========================================
# 4. 세션 초기화
# ==========================================

if "page" not in st.session_state:
    st.session_state.page = 0

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ==========================================
# 5. 메뉴
# ==========================================

st.sidebar.title("📌 메뉴")

menu = st.sidebar.radio(
    "이동하기",
    [
        "질문 답변하기 (친구용)",
        "답변 확인하기 (현서용)",
    ],
)

# ==========================================
# 6. 친구용 페이지
# ==========================================

if menu == "질문 답변하기 (친구용)":

    st.title("💌 현서에게 전하는 이야기")

    st.write(
        "질문에 차례대로 답해보며 "
        "현서와의 추억을 남겨주세요 🌿"
    )

    total_questions = len(QUESTIONS)
    current_page = st.session_state.page

    # ------------------------------------------
    # 제출 완료
    # ------------------------------------------

    if st.session_state.submitted:

        st.balloons()

        st.markdown(
            """
            <div class="thankyou-box">
                <h3 style="margin-top:0; color:#D8A47F;">
                    ✨ 답변이 전달되었습니다!
                </h3>

                <p style="font-size:16px;">
                    답변해줘서 고마워 💌
                </p>

                <p style="font-size:16px;">
                    여기에 질문해준 애들은 적게는 2장,
                    많으면 내가 원하는 만큼 5장 정도의
                    편지를 줄 거야!
                    <br>
                    졸업식날이나 졸업식 전에 줄게 🌿
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button("처음부터 다시 작성하기"):
            st.session_state.page = 0
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.rerun()

    # ------------------------------------------
    # 질문 페이지
    # ------------------------------------------

    elif current_page < total_questions:

        progress = (current_page + 1) / total_questions

        st.progress(progress)

        st.caption(
            f"질문 {current_page + 1} / {total_questions}"
        )

        question_text = QUESTIONS[current_page]

        st.markdown(
            f"""
            <h3 style="margin-bottom:20px;">
                Q{current_page + 1}. {question_text}
            </h3>
            """,
            unsafe_allow_html=True,
        )

        default_value = st.session_state.user_answers.get(
            question_text,
            "",
        )

        answer_key = f"answer_{current_page}"

        if current_page == 0:

            user_input = st.text_input(
                "답변을 입력해 주세요",
                value=default_value,
                key=answer_key,
                placeholder="예: 홍길동",
            )

        else:

            user_input = st.text_area(
                "답변을 입력해 주세요",
                value=default_value,
                key=answer_key,
                height=180,
                placeholder="편하게 솔직한 마음을 적어주세요...",
            )

        st.write("")

        col1, col2 = st.columns(2)

        # 이전
        with col1:

            if current_page > 0:

                if st.button("⬅️ 이전"):

                    st.session_state.user_answers[
                        question_text
                    ] = user_input

                    st.session_state.page -= 1

                    st.rerun()

        # 다음 / 제출
        with col2:

            if current_page < total_questions - 1:

                if st.button("다음 ➡️"):

                    if not user_input.strip():

                        st.warning(
                            "답변을 작성해 주세요!"
                        )

                    else:

                        st.session_state.user_answers[
                            question_text
                        ] = user_input

                        st.session_state.page += 1

                        st.rerun()

            else:

                if st.button("제출하기 💌"):

                    if not user_input.strip():

                        st.warning(
                            "답변을 작성해 주세요!"
                        )

                    else:

                        st.session_state.user_answers[
                            question_text
                        ] = user_input

                        name = st.session_state.user_answers.get(
                            QUESTIONS[0],
                            "이름 없음",
                        )

                        save_response(
                            name,
                            st.session_state.user_answers,
                        )

                        st.session_state.submitted = True

                        st.rerun()

# ==========================================
# 7. 관리자 페이지
# ==========================================

elif menu == "답변 확인하기 (현서용)":

    st.title("🔒 관리자 페이지")

    st.write(
        "현서만 볼 수 있는 페이지입니다."
    )

    password = st.text_input(
        "관리자 비밀번호",
        type="password",
    )

    if password:

        if password == ADMIN_PASSWORD:

            st.success("확인되었습니다! 💌")

            data = load_responses()

            st.subheader(
                f"📊 도착한 답변 ({len(data)}명)"
            )

            if not data:

                st.info(
                    "아직 제출된 답변이 없습니다."
                )

            else:

                for response in data:

                    friend_name = response["name"]

                    with st.expander(
                        f"💌 {friend_name} 친구의 답변"
                    ):

                        st.caption(
                            f"제출 번호: {response['id']}"
                        )

                        for question, answer in response[
                            "answers"
                        ].items():

                            st.markdown(
                                f"""
                                <p style="
                                    color:#D8A47F;
                                    font-weight:bold;
                                    margin-bottom:5px;
                                ">
                                    Q. {question}
                                </p>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.write(answer)

                            st.divider()

        else:

            st.error(
                "비밀번호가 올바르지 않습니다."
            )