import streamlit as st
from PIL import Image
import gemini_handler
import re
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="レシピ提案AI",
    layout="wide", # ワイド設定に変更して左右の余白を解放
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

# --- CSS設定（余白削減・フッター横並び物理固定） ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    
    html, body {
        font-family: 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
    }

    /* 左右の余白を大幅に削減 */
    .main .block-container {
        padding-bottom: 120px !important;
        padding-top: 10px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* 下部ナビゲーションの物理的固定 */
    div[data-testid="stVerticalBlock"] > div:last-child div[data-testid="stHorizontalBlock"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        background-color: #FFFFFF !important;
        border-top: 1px solid #DDDDDD !important;
        padding: 5px 0 25px 0 !important;
        z-index: 10000 !important;
        justify-content: space-around !important;
    }

    /* カラムの横並びを徹底強制 */
    div[data-testid="stVerticalBlock"] > div:last-child div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        width: 33% !important;
    }

    div[data-testid="stVerticalBlock"] > div:last-child button {
        background-color: transparent !important;
        color: #444444 !important;
        border: none !important;
        width: 100% !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }
    
    .active-nav button {
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        border-radius: 0 !important;
    }

    .primary-btn button {
        background-color: #FF9900 !important;
        color: white !important;
        height: 54px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }

    .recipe-card {
        background-color: #FFFFFF !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #DDDDDD !important;
        color: #000000 !important;
    }
    
    h1 {
        font-size: 22px !important;
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        padding-bottom: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

def change_page(page_name):
    st.session_state.page = page_name

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
        st.markdown("<br>### 2. 食材リスト", unsafe_allow_html=True)
        edited = st.text_area("食材リスト", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        is_choi = st.checkbox("ちょい足しモード（定番食材を追加）", value=False)
        
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
        st.info("食材を解析してください")
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

# --- フッター（横並び強制） ---
nc1, nc2, nc3 = st.columns(3)

with nc1:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "作る" else ""}">', unsafe_allow_html=True)
    if st.button("作る", key="b1", use_container_width=True):
        change_page("作る")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with nc2:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "確認" else ""}">', unsafe_allow_html=True)
    if st.button("確認", key="b2", use_container_width=True):
        change_page("確認")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with nc3:
    st.markdown(f'<div class="{"active-nav" if st.session_state.page == "保存" else ""}">', unsafe_allow_html=True)
    if st.button("保存", key="b3", use_container_width=True):
        change_page("保存")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
