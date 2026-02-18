import streamlit as st
from PIL import Image
import gemini_handler
import re
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="レシピ提案AI",
    layout="wide",
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

# ナビゲーションのインデックスを取得（CSSでのハイライト用）
nav_index = ["作る", "確認", "保存"].index(st.session_state.page) + 1

# --- CSS設定（下部固定を確実に復元） ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    
    html, body {{
        font-family: 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
    }}

    /* コンテンツエリアの余白 */
    .main .block-container {{
        padding-bottom: 120px !important;
        padding-top: 10px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    /* 【重要】下部ナビゲーションを画面最下部に完全固定 */
    /* Streamlitのメインビューコンテナ内の最後の要素（st.columns部分）を狙いうち */
    div[data-testid="stAppViewContainer"] section.main div.block-container [data-testid="stVerticalBlock"] > div:last-child {{
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        background-color: #FFFFFF !important;
        border-top: 1px solid #DDDDDD !important;
        padding: 10px 0 25px 0 !important;
        z-index: 100000 !important;
    }}

    /* 横一列の並びをモバイルでも強制固定 */
    div[data-testid="stAppViewContainer"] section.main div.block-container [data-testid="stVerticalBlock"] > div:last-child div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        justify-content: space-around !important;
    }}

    /* 各カラムを均等な幅に */
    div[data-testid="stAppViewContainer"] section.main div.block-container [data-testid="stVerticalBlock"] > div:last-child [data-testid="column"] {{
        flex: 1 1 0% !important;
        min-width: 0 !important;
    }}

    /* ナビゲーションボタンのフラット表示 */
    div[data-testid="stVerticalBlock"] > div:last-child button {{
        background-color: transparent !important;
        color: #666666 !important;
        border: none !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: none !important;
    }}

    /* アクティブなナビゲーションを強調 */
    div[data-testid="stVerticalBlock"] > div:last-child div[data-testid="column"]:nth-child({nav_index}) button {{
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        border-radius: 0 !important;
    }}

    /* メインオレンジボタン */
    .primary-btn button {{
        background-color: #FF9900 !important;
        color: white !important;
        height: 52px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }}

    .recipe-card {{
        background-color: #FFFFFF !important;
        padding: 15px !important;
        border-radius: 12px !important;
        border: 1px solid #DDDDDD !important;
        color: #000000 !important;
    }}
    
    h1 {{
        font-size: 22px !important;
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        padding-bottom: 5px !important;
    }}
</style>
""", unsafe_allow_html=True)

def change_page(p):
    st.session_state.page = p

# --- メインコンテンツ表示 ---
if st.session_state.page == "作る":
    st.markdown("<h1>レシピを作る</h1>", unsafe_allow_html=True)
    st.caption("写真を解析して献立をご提案します")

    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("ジャンル", ["一般的な料理", "離乳食(5-6ヶ月)", "離乳食(7-8ヶ月)", "離乳食(9-11ヶ月)", "離乳食(12-18ヶ月)"])
    with c2:
        num_dishes = st.radio("品数", (1, 2, 3), format_func=lambda x: f"{x}品", horizontal=True)

    files = st.file_uploader("写真をアップロード", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
    
    if files:
        cols = st.columns(min(len(files), 4))
        for i, f in enumerate(files):
            with cols[i % 4]: st.image(Image.open(f), use_column_width=True)
        
        if st.button("1. 食材を読み取る", use_container_width=True):
            with st.spinner("解析中..."):
                stream = gemini_handler.identify_ingredients([Image.open(f) for f in files])
                st.session_state.ingredients_list = st.write_stream(stream)

    if st.session_state.ingredients_list:
        st.markdown("<br>### 2. 食材リスト（編集可）", unsafe_allow_html=True)
        edited = st.text_area("食材リスト", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        is_choi = st.checkbox("ちょい足しモード", value=False)
        
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("3. レシピを生成", use_container_width=True):
            with st.status("レシピを考案中...", expanded=True) as status:
                placeholder = st.empty()
                stream = gemini_handler.generate_recipe(edited, mode, num_dishes, is_choi)
                with placeholder:
                    result = st.write_stream(stream)
                st.session_state.recipe_result = result
                st.session_state.ingredients_list = edited
                placeholder.empty()
                status.update(label="完成しました", state="complete")
            change_page("確認")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "確認":
    st.markdown("<h1>できたレシピ</h1>", unsafe_allow_html=True)
    
    if not st.session_state.recipe_result:
        st.info("食材を解析してください")
    else:
        text = st.session_state.recipe_result
        pattern = re.compile(r'##\s*案([A-C|Ａ-Ｃ])[:：]')
        matches = list(pattern.finditer(text))
        
        if matches:
            intro = text[:matches[0].start()].strip()
            if intro: st.warning(intro)
            
            labels = [text[m.start():].split('\n')[0].replace('#', '').strip().replace("案", "") for m in matches]
            tabs = st.tabs(labels)
            for i, tab in enumerate(tabs):
                start = matches[i].start()
                end = matches[i+1].start() if i+1 < len(matches) else len(text)
                with tab:
                    st.markdown(f"<div class='recipe-card'>{text[start:end]}</div>", unsafe_allow_html=True)
        
            st.markdown("---")
            if st.button("このレシピを保存する", use_container_width=True):
                st.session_state.saved_recipes.insert(0, {"date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"), "content": text})
                st.success("保存しました")
        else:
            st.markdown(f"<div class='recipe-card'>{text}</div>", unsafe_allow_html=True)

elif st.session_state.page == "保存":
    st.markdown("<h1>保存済みレシピ</h1>", unsafe_allow_html=True)
    
    if not st.session_state.saved_recipes:
        st.info("保存されたレシピはありません")
    else:
        for i, item in enumerate(st.session_state.saved_recipes):
            with st.expander(f"{item['date']} のレシピ"):
                st.markdown(f"<div class='recipe-card'>{item['content']}</div>", unsafe_allow_html=True)
                if st.button(f"削除", key=f"del_{i}"):
                    st.session_state.saved_recipes.pop(i)
                    st.rerun()

# --- フッター（画面最下部に固定・横並び強制） ---
# スクリプトの最後に st.columns を置くことで、CSSでの強制指定が効きやすくなります
nc1, nc2, nc3 = st.columns(3)

with nc1:
    if st.button("作る", key="btn_create", use_container_width=True):
        change_page("作る")
        st.rerun()

with nc2:
    if st.button("確認", key="btn_confirm", use_container_width=True):
        change_page("確認")
        st.rerun()

with nc3:
    if st.button("保存", key="btn_save", use_container_width=True):
        change_page("保存")
        st.rerun()
