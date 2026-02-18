import streamlit as st
from PIL import Image
import gemini_handler
import re
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="レシピ提案AI",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- セッション状態の初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = "作る"
if 'ingredients_list' not in st.session_state:
    st.session_state.ingredients_list = ""
if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = ""
if 'saved_recipes' not in st.session_state:
     st.session_state.saved_recipes = []

# --- CSS設定（下部ナビゲーションを横並びに固定） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    
    html, body {
        font-family: 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
    }

    /* メメインコンテンツエリアの余白（フッターとヘッダー用） */
    .main .block-container {
        padding-bottom: 120px !important;
        padding-top: 20px !important;
    }

    /* 【重要】下部ナビゲーションバーの固定と横並び強制 */
    div[data-testid="stVerticalBlock"] > div:last-child {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #FFFFFF;
        border-top: 1px solid #EEEEEE;
        z-index: 9999;
        padding: 5px 0 15px 0; /* 下に少し余裕を持たせる（iPhoneのホームバー対策） */
    }
    
    /* StreamlitのColumnsが縦に並ぶのを阻止して横に固定 */
    div[data-testid="stVerticalBlock"] > div:last-child [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: space-around !important;
        align-items: center !important;
    }
    
    /* ボタンを中央に寄せ、枠を消す */
    div[data-testid="stVerticalBlock"] > div:last-child [data-testid="stHorizontalBlock"] > div {
        flex: 1 !important;
        min-width: 0 !important;
        text-align: center !important;
    }

    /* ナビゲーション用ボタンのスタイル */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        border: none !important;
        background-color: transparent !important;
        color: #666666 !important;
        font-size: 14px !important;
        padding: 5px 0 !important;
    }
    
    /* 選択中のボタン強調（オレンジの下線） */
    .active-nav button {
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        border-radius: 0 !important;
    }

    /* 生成ボタンなどの目立つボタン */
    .primary-btn button {
        background-color: #FF9900 !important;
        color: white !important;
        height: 52px !important;
        font-size: 18px !important;
        box-shadow: 0 4px 6px rgba(255,153,0,0.2) !important;
    }

    .recipe-card {
        background-color: #FFFFFF !important;
        padding: 24px !important;
        border-radius: 12px !important;
        border: 1px solid #EEEEEE !important;
        color: #000000 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
    }
    
    h1 {
        font-size: 24px !important;
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        padding-bottom: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ページ切り替え関数 ---
def change_page(page_name):
    st.session_state.page = page_name

# ==========================================
# メインコンテンツ表示
# ==========================================

if st.session_state.page == "作る":
    st.markdown("<h1>レシピを作る</h1>", unsafe_allow_html=True)
    st.caption("食材の写真を撮って、AIに献立をまかせましょう")

    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("ジャンル", ["一般的な料理", "離乳食(5-6ヶ月)", "離乳食(7-8ヶ月)", "離乳食(9-11ヶ月)", "離乳食(12-18ヶ月)"])
    with c2:
        num_dishes = st.radio("品数", (1, 2, 3), format_func=lambda x: f"{x}品", horizontal=True)

    uploaded_files = st.file_uploader("写真をアップロードしてください", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    
    if uploaded_files:
        cols = st.columns(min(len(uploaded_files), 4))
        for i, f in enumerate(uploaded_files):
            img = Image.open(f)
            with cols[i % 4]: st.image(img, use_column_width=True)
        
        if st.button("① 食材を読み取る", use_container_width=True):
            with st.spinner("解析中..."):
                stream = gemini_handler.identify_ingredients([Image.open(f) for f in uploaded_files])
                st.session_state.ingredients_list = st.write_stream(stream)

    if st.session_state.ingredients_list:
        st.markdown("<br>### 2. 食材リスト", unsafe_allow_html=True)
        edited = st.text_area("食材", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        is_choi = st.checkbox("🥕 ちょい足しモード（定番食材をプラス）", value=False)
        
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("② この食材でレシピ生成！", use_container_width=True):
            with st.status("Geminiシェフが考案中...", expanded=True) as status:
                placeholder = st.empty()
                stream = gemini_handler.generate_recipe(edited, mode, num_dishes, is_choi)
                with placeholder:
                    result = st.write_stream(stream)
                st.session_state.recipe_result = result
                st.session_state.ingredients_list = edited
                placeholder.empty()
                status.update(label="完成しました！", state="complete")
            change_page("確認")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "確認":
    st.markdown("<h1>できたレシピ</h1>", unsafe_allow_html=True)
    
    if not st.session_state.recipe_result:
        st.info("「作る」画面からレシピを作ってください")
    else:
        result_text = st.session_state.recipe_result
        pattern = re.compile(r'##\s*案([A-C|Ａ-Ｃ])[:：]')
        matches = list(pattern.finditer(result_text))
        
        if matches:
            intro = result_text[:matches[0].start()].strip()
            if intro: st.warning(intro)
            
            tab_labels = [result_text[m.start():].split('\n')[0].replace('#', '').strip().replace("案", "") for m in matches]
            tabs = st.tabs(tab_labels)
            for i, tab in enumerate(tabs):
                start = matches[i].start()
                end = matches[i+1].start() if i+1 < len(matches) else len(result_text)
                with tab:
                    st.markdown(f"<div class='recipe-card'>{result_text[start:end]}</div>", unsafe_allow_html=True)
        
            st.markdown("---")
            if st.button("⭐ このレシピをお気に入り保存", use_container_width=True):
                new_entry = {"date": datetime.datetime.now().strftime("%m/%d %H:%M"), "content": result_text}
                st.session_state.saved_recipes.insert(0, new_entry)
                st.success("「保存」画面に追加しました")
        else:
            st.markdown(f"<div class='recipe-card'>{result_text}</div>", unsafe_allow_html=True)

elif st.session_state.page == "保存":
    st.markdown("<h1>保存済みレシピ</h1>", unsafe_allow_html=True)
    
    if not st.session_state.saved_recipes:
        st.info("まだ保存されたレシピはありません")
    else:
        for i, item in enumerate(st.session_state.saved_recipes):
            with st.expander(f"📅 {item['date']} のレシピ"):
                st.markdown(f"<div class='recipe-card'>{item['content']}</div>", unsafe_allow_html=True)
                if st.button(f"削除", key=f"del_{i}"):
                    st.session_state.saved_recipes.pop(i)
                    st.rerun()

# ==========================================
# 下部ナビゲーション（フッター）
# ==========================================

# 画面の最後に置くことで、CSSで固定されたバーを生成する
nc1, nc2, nc3 = st.columns(3)

with nc1:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "作る" else ""}">', unsafe_allow_html=True)
    if st.button("🧑‍🍳 作る", key="b1", use_container_width=True):
        change_page("作る")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with nc2:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "確認" else ""}">', unsafe_allow_html=True)
    if st.button("📓 確認", key="b2", use_container_width=True):
        change_page("確認")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with nc3:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "保存" else ""}">', unsafe_allow_html=True)
    if st.button("⭐ 保存", key="b3", use_container_width=True):
        change_page("保存")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
