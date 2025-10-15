import json
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime
import os  # ← 画像ファイルの存在チェックに使う

SPREADSHEET_NAME = "personality_test"  # スプレッドシート名に合わせる
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# =============================
# Google認証設定
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
# 画像を表示する関数
# =============================
def show_image_for_question(key):
    """質問キーに対応する画像を表示する（images/フォルダ内）"""
    image_path = f"images/{key}.jpg"  # 例: images/q1.jpg
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        # 画像がない場合はエラーメッセージを出さないようにスルー
        pass

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
# UI 初期化
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

# =============================
# 入力フォーム
# =============================
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
    node = question_tree[key]

    # 👇 ここで画像を表示
    show_image_for_question(key)

if isinstance(node, dict):
    # 質問の表示
    st.subheader(node["text"])

    # 質問に対応する画像を表示
    show_image_for_question(key)

    # 回答ボタンを表示
    for option_key, option_text in node["options"].items():
        if st.button(option_text, key=key + option_key):
            st.session_state.path.append(option_key)
            st.rerun()

else:
    # 結果の表示
    st.success(
        f"{st.session_state.nickname} さんの結果：\n\n{node}\n\n"
        "🎮 D棟3階のパソコン室Cで僕たちが作った3Dゲームが遊べます。ぜひプレイしてみてね！"
    )

    # 結果画像を1枚だけ表示
    show_image_for_question(key)
