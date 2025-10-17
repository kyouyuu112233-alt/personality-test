import json
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime
import os

SPREADSHEET_NAME = "personality_test"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# =============================
# Google認証
# =============================
def get_gspread_client():
    raw = st.secrets["gcp"]["gcp_service_account"]
    info = json.loads(raw)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)

def send_to_sheet(nickname, password, result_text):
    client = get_gspread_client()
    sheet = client.open(SPREADSHEET_NAME).sheet1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, nickname, password, result_text], value_input_option="USER_ENTERED")

# =============================
# 画像表示関数
# =============================
def show_image_for_question(key):
    for ext in [".jpg", ".png", ".jpeg", ".gif"]:
        image_path = f"images/{key}{ext}"
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
            break

# =============================
# 質問ツリー & 結果データ
# =============================
question_tree = {
    "start": {"text": "あなたはよく外出をするほうですか？", "yes": "q1", "no": "q2"},
    "q1": {"text": "コミュ力があると思う？", "yes": "q3", "no": "q4"},
    "q2": {"text": "思考力があるほうだと思う？", "yes": "q4", "no": "q5"},
    "q3": {"text": "仲間が失敗しても許してあげる?", "yes": "q6", "no": "q7"},
    "q4": {"text": "自分は聞き上手だと思う？", "yes": "q8", "no": "q9"},
    "q5": {"text": "自分には特別な力があると思う", "yes": "j", "no": "i"},
    "q6": {"text": "自分より他人のことを優先する", "yes": "a", "no": "b"},
    "q7": {"text": "失敗してしまったらイライラするより落ち込む", "yes": "c", "no": "d"},
    "q8": {"text": "一人よりも大人数のほうがいい", "yes": "e", "no": "f"},
    "q9": {"text": "感情的になりやすいと思う？", "yes": "g", "no": "h"},
}

results = {
    "a": {"title": "🌟 あなたは **ポジティブタイプ** です！", "desc": "いつも明るく前向きで、周りの人を元気にするムードメーカー！"},
    "b": {"title": "🌸 あなたは **優しいタイプ** です！", "desc": "思いやりがあり、人の気持ちを大切にする優しさあふれる人です。"},
    "c": {"title": "🌧 あなたは **ネガティブタイプ** です！", "desc": "少し心配性だけど、その慎重さが大きな失敗を防いでくれます。"},
    "d": {"title": "🔥 あなたは **怒りっぽいタイプ** です！", "desc": "感情表現が豊かで正義感が強い、熱いハートの持ち主！"},
    "e": {"title": "❄️ あなたは **クールタイプ** です！", "desc": "冷静で落ち着いた性格。どんな状況でも焦らず判断できます。"},
    "f": {"title": "🌙 あなたは **おとなしいタイプ** です！", "desc": "マイペースで穏やか。周りを安心させる存在です。"},
    "g": {"title": "🎭 あなたは **感情豊かなタイプ** です！", "desc": "喜怒哀楽をはっきり表現できる魅力的な人です。"},
    "h": {"title": "💪 あなたは **熱血タイプ** です！", "desc": "努力家で仲間思い。目標にまっすぐ突き進む力強さを持っています。"},
    "i": {"title": "🌼 あなたは **天然タイプ** です！", "desc": "自由でマイペース。周りをほっこりさせる癒し系です。"},
    "j": {"title": "🌀 あなたは **変人タイプ** です！", "desc": "独創的で発想力抜群！誰にも真似できない個性の持ち主です。"},
}

# =============================
# UI
# =============================
st.set_page_config(page_title="性格診断テスト", page_icon="🧠")
st.title("🧠 性格診断テスト")

if "nickname" not in st.session_state:
    st.session_state.update({
        "nickname": None,
        "password": None,
        "current": "start",
        "sent": False
    })

if not st.session_state.nickname or not st.session_state.password:
    st.warning("※ニックネームとパスワードは後で確認できるようにメモ等しておくことをおすすめします。")
    nick = st.text_input("ニックネーム")
    pw = st.text_input("パスワード", type="password")
    if st.button("診断スタート") and nick and pw:
        st.session_state.nickname = nick
        st.session_state.password = pw
        st.rerun()
else:
    key = st.session_state.current

    if key in question_tree:
        node = question_tree[key]
        show_image_for_question(key)
        st.subheader(node["text"])
        col1, col2 = st.columns(2)
        if col1.button("はい"):
            st.session_state.current = node["yes"]
            st.rerun()
        if col2.button("いいえ"):
            st.session_state.current = node["no"]
            st.rerun()

    elif key in results:
        result = results[key]
        st.success(
            f"""
            {st.session_state.nickname} さんの結果：  
            {result['title']}  

            💬 {result['desc']}
            """
        )
        show_image_for_question(key)

        st.info("🎮 D棟三階でこの結果を用いて僕たちが作った3Dゲームが遊べます。ぜひプレイしてみてね！")

        if not st.session_state.sent:
            if st.button("📤 完了"):
                try:
                    send_to_sheet(st.session_state.nickname, st.session_state.password, result["title"])
                    st.success("送信しました ✅")
                    st.session_state.sent = True
                except Exception as e:
                    st.error(f"送信に失敗しました: {e}")

        if st.button("もう一度やる"):
            st.session_state.update({
                "nickname": None,
                "password": None,
                "current": "start",
                "sent": False
            })
            st.rerun()
    else:
        st.error("質問または結果データが見つかりません。")
