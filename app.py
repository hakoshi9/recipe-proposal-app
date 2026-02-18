import streamlit as st
from PIL import Image
import gemini_handler
import re
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="レシピ提案AI",
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

# --- CSS設定（絵文字排除・フッター横並び強制） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    
    html, body {
        font-family: 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
    }

    .main .block-container {
        padding-bottom: 120px !important;
        padding-top: 20px !important;
    }

    /* フッターナビゲーションの強制横並び */
    div[data-testid="stVerticalBlock"] > div:last-child {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        background-color: #FFFFFF !important;
        border-top: 1px solid #DDDDDD !important;
        padding: 10px 0 20px 0 !important;
        z-index: 10000 !important;
    }

    /* モバイルでの縦並びを徹底的に上書き */
    div[data-testid="stVerticalBlock"] > div:last-child div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 0 !important;
    }
    
    div[data-testid="stVerticalBlock"] > div:last-child div[data-testid="stHorizontalBlock"] > div {
        flex: 1 !important;
        min-width: 0 !important;
        width: 33.33% !important;
    }

    /* ナビゲーションボタン */
    div[data-testid="stVerticalBlock"] > div:last-child button {
        background-color: transparent !important;
        color: #444444 !important;
        border: none !important;
        height: auto !important;
        padding: 5px !important;
        font-size: 15px !important;
        width: 100% !important;
    }
    
    .active-nav button {
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        border-radius: 0 !important;
    }

    /* オレンジボタン（生成など） */
    .primary-btn button {
        background-color: #FF9900 !important;
        color: white !important;
        height: 54px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }

    .recipe-card {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 12px !important;
        border: 1px solid #DDDDDD !important;
        color: #000000 !important;
    }
    
    h1 {
        font-size: 24px !important;
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        padding-bottom: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

def change_page(page_name):
    st.session_state.page = page_name

# --- 各画面のコンテンツ ---
if st.session_state.page == "作る":
    st.markdown("<h1>レシピを作る</h1>", unsafe_allow_html=True)
    st.caption("食材の写真を解析して献立をご提案します")

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
        
        if st.button("1. 食材を読み取る", use_container_width=True):
            with st.spinner("解析中..."):
                stream = gemini_handler.identify_ingredients([Image.open(f) for f in uploaded_files])
                st.session_state.ingredients_list = st.write_stream(stream)

    if st.session_state.ingredients_list:
        st.markdown("<br>### 2. 食材リスト（編集可）", unsafe_allow_html=True)
        edited = st.text_area("食材リスト", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        is_choi = st.checkbox("ちょい足しモード（定番食材を追加して提案）", value=False)
        
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("3. この食材でレシピ生成", use_container_width=True):
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
        st.info("「作る」画面からレシピを生成してください")
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
            if st.button("このレシピを保存する", use_container_width=True):
                new_entry = {"date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"), "content": result_text}
                st.session_state.saved_recipes.insert(0, new_entry)
                st.success("保存しました")
        else:
            st.markdown(f"<div class='recipe-card'>{result_text}</div>", unsafe_allow_html=True)

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

# --- フッターナビゲーション ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "作る" else ""}">', unsafe_allow_html=True)
    if st.button("作る", key="nav1", use_container_width=True):
        change_page("作る")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "確認" else ""}">', unsafe_allow_html=True)
    if st.button("確認", key="nav2", use_container_width=True):
        change_page("確認")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "保存" else ""}">', unsafe_allow_html=True)
    if st.button("保存", key="nav3", use_container_width=True):
        change_page("保存")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
