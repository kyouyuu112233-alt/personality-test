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
    """質問や結果に対応する画像を表示する"""
    for ext in [".jpg", ".png", ".jpeg", ".gif"]:
        image_path = f"images/{key}{ext}"
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
            break  # 最初に見つけた1枚だけ表示

# =============================
# 質問ツリー
# =============================
question_tree = {
    "start": {"text": "あなたはよく外出をするほうですか？", "yes": "q1", "no": "q2"},
    "q1": {"text": "コミュ力があると思う？", "yes": "q3", "no": "q4"},
    "q2": {"text": "思考力があるほうだと思う？", "yes": "q4", "no": "q5"},
    "q3": {"text": "仲間が失敗しても許してあげる?", "yes": "q6", "no": "q7"},
    "q4": {"text": "自分は聞き上手だと思う？", "yes": "q8", "no": "q9"},
    "q5": {"text": "自分には特別な力があると思う", "yes": "j", "no": "i"},
    "q6": {"text": "自分より他人のことを優先する", "yes": "a", "no": "b"},
    "q7": {"text": "失敗してしまったら落ち込むよりもイライラする", "yes": "c", "no": "d"},
    "q8": {"text": "一人よりも大人数のほうがいい", "yes": "e", "no": "f"},
    "q9": {"text": "感情的になりやすいと思う？", "yes": "g", "no": "h"},
    "a": "🌟 あなたは **ポジティブタイプ** です！",
    "b": "🌸 あなたは **優しいタイプ** です！",
    "c": "🌧 あなたは **ネガティブタイプ** です！",
    "d": "🔥 あなたは **怒りっぽいタイプ** です！",
    "e": "❄️ あなたは **クールタイプ** です！",
    "f": "🌙 あなたは **おとなしいタイプ** です！",
    "g": "🎭 あなたは **感情豊かなタイプ** です！",
    "h": "💪 あなたは **熱血タイプ** です！",
    "i": "🌼 あなたは **天然タイプ** です！",
    "j": "🌀 あなたは **変人タイプ** です！",
}

# =============================
# 結果の説明
# =============================
result_descriptions = {
    "a": "前向きでエネルギッシュ。仲間を元気づけ、いつも明るい雰囲気を作るムードメーカー！",
    "b": "優しくて思いやりがあり、周囲から信頼されるタイプ。誰かが困っているとすぐに助けたくなる。",
    "c": "慎重で物事を深く考えるタイプ。少しネガティブに見えるけど、実はとても繊細で真面目！",
    "d": "情熱的で負けず嫌い。怒ることもあるけれど、それは本気で向き合っている証拠！",
    "e": "冷静沈着で頭の回転が速い。どんなときも落ち着いていて、周りから頼られるタイプ。",
    "f": "おとなしくてマイペース。自分の世界を大切にしていて、無理に合わせない芯の強さがある。",
    "g": "感情豊かで表現力が高い。人の気持ちを察するのが得意で、周りを和ませる存在。",
    "h": "熱血で努力家！どんなことにも一生懸命取り組み、仲間を引っ張っていくリーダー気質。",
    "i": "マイペースで天真爛漫。周囲を癒す不思議な魅力があり、みんなを笑顔にする。",
    "j": "独創的で発想力抜群！少し変わってるけど、そのユニークさがあなたの最大の武器！"
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
    st.warning("※ニックネームは後で確認できるようにメモしておいてください。")
    nick = st.text_input("ニックネーム")
    pw = st.text_input("パスワード", type="password")
    if st.button("診断スタート") and nick and pw:
        st.session_state.nickname = nick
        st.session_state.password = pw
        st.rerun()
else:
    key = st.session_state.current
    node = question_tree.get(key)

    if node is None:
        st.error("質問データが見つかりません。")
    elif isinstance(node, dict):
        show_image_for_question(key)
        st.subheader(node["text"])
        col1, col2 = st.columns(2)
        if col1.button("はい"):
            st.session_state.current = node["yes"]
            st.rerun()
        if col2.button("いいえ"):
            st.session_state.current = node["no"]
            st.rerun()
    else:
        # 結果の表示
        st.success(
            f"{st.session_state.nickname} さんの結果：\n\n{node}\n\n"
            "🎮 診断結果を用いてD棟3階で僕たちが作った3Dゲームが遊べます。ぜひプレイしてみてね！"
        )
        show_image_for_question(key)

        if not st.session_state.sent:
            if st.button("📤 完了"):
                try:
                    send_to_sheet(
                        st.session_state.nickname,
                        st.session_state.password,
                        node
                    )
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
