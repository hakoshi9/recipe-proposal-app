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

page = st.session_state.page

# --- CSS + HTMLフッター（Streamlitの構造に依存しない純粋なHTML固定フッター） ---
active_create  = "nav-active" if page == "作る" else ""
active_confirm = "nav-active" if page == "確認" else ""
active_save    = "nav-active" if page == "保存" else ""

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');

    html, body {{
        font-family: 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
    }}

    /* Streamlitのデフォルトヘッダー・フッターを非表示 */
    header[data-testid="stHeader"] {{ display: none !important; }}
    footer {{ display: none !important; }}

    /* コンテンツエリア：フッター分の余白を確保 */
    .main .block-container {{
        padding-bottom: 100px !important;
        padding-top: 15px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }}

    /* 固定フッターナビゲーション */
    .fixed-footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #FFFFFF;
        border-top: 1px solid #DDDDDD;
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        align-items: center;
        padding: 10px 0 env(safe-area-inset-bottom, 15px);
        z-index: 999999;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.06);
    }}

    .nav-btn {{
        flex: 1;
        text-align: center;
        background: none;
        border: none;
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 15px;
        font-weight: 700;
        color: #888888;
        padding: 8px 0;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        transition: color 0.2s, border-color 0.2s;
    }}

    .nav-btn.nav-active {{
        color: #FF9900;
        border-bottom: 3px solid #FF9900;
    }}

    /* メインアクションボタン */
    div.stButton > button {{
        background-color: #FF9900 !important;
        color: #FFFFFF !important;
        height: 52px !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
    }}

    /* サブボタン（食材読み取りなど）は白背景 */
    div.stButton > button[kind="secondary"] {{
        background-color: #F5F5F5 !important;
        color: #333333 !important;
    }}

    .recipe-card {{
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #DDDDDD;
        color: #000000;
        line-height: 1.7;
        margin-bottom: 12px;
    }}

    h1 {{
        font-size: 22px !important;
        color: #FF9900 !important;
        border-bottom: 3px solid #FF9900 !important;
        padding-bottom: 5px !important;
        margin-bottom: 15px !important;
    }}
</style>

<!-- 固定フッターナビゲーション（純粋なHTML） -->
<div class="fixed-footer">
    <form method="get" style="flex:1;margin:0;">
        <button class="nav-btn {active_create}" name="nav" value="作る" type="submit">作る</button>
    </form>
    <form method="get" style="flex:1;margin:0;">
        <button class="nav-btn {active_confirm}" name="nav" value="確認" type="submit">確認</button>
    </form>
    <form method="get" style="flex:1;margin:0;">
        <button class="nav-btn {active_save}" name="nav" value="保存" type="submit">保存</button>
    </form>
</div>
""", unsafe_allow_html=True)

# --- URLパラメータでページ切り替え ---
params = st.query_params
if "nav" in params:
    nav_val = params["nav"]
    if nav_val in ["作る", "確認", "保存"] and st.session_state.page != nav_val:
        st.session_state.page = nav_val
        st.query_params.clear()
        st.rerun()

page = st.session_state.page

# --- メインコンテンツ ---
if page == "作る":
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
            with cols[i % 4]:
                st.image(Image.open(f), use_column_width=True)

        if st.button("1. 食材を読み取る", use_container_width=True):
            with st.spinner("解析中..."):
                stream = gemini_handler.identify_ingredients([Image.open(f) for f in files])
                st.session_state.ingredients_list = st.write_stream(stream)

    if st.session_state.ingredients_list:
        st.markdown("### 2. 食材リスト（編集可）")
        edited = st.text_area("食材リスト", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        is_choi = st.checkbox("ちょい足しモード（定番食材を追加）", value=False)

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
            st.session_state.page = "確認"
            st.rerun()

elif page == "確認":
    st.markdown("<h1>できたレシピ</h1>", unsafe_allow_html=True)

    if not st.session_state.recipe_result:
        st.info("食材を解析してください")
    else:
        text = st.session_state.recipe_result
        pattern = re.compile(r'##\s*案([A-C|Ａ-Ｃ])[:：]')
        matches = list(pattern.finditer(text))

        if matches:
            intro = text[:matches[0].start()].strip()
            if intro:
                st.warning(intro)

            labels = [text[m.start():].split('\n')[0].replace('#', '').strip().replace("案", "") for m in matches]
            tabs = st.tabs(labels)
            for i, tab in enumerate(tabs):
                start = matches[i].start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                with tab:
                    st.markdown(f"<div class='recipe-card'>{text[start:end]}</div>", unsafe_allow_html=True)

            st.markdown("---")
            if st.button("このレシピを保存する", use_container_width=True):
                st.session_state.saved_recipes.insert(0, {
                    "date": datetime.datetime.now().strftime("%Y/%m/%d %H:%M"),
                    "content": text
                })
                st.success("保存しました")
        else:
            st.markdown(f"<div class='recipe-card'>{text}</div>", unsafe_allow_html=True)

elif page == "保存":
    st.markdown("<h1>保存済みレシピ</h1>", unsafe_allow_html=True)

    if not st.session_state.saved_recipes:
        st.info("保存されたレシピはありません")
    else:
        for i, item in enumerate(st.session_state.saved_recipes):
            with st.expander(f"{item['date']} のレシピ"):
                st.markdown(f"<div class='recipe-card'>{item['content']}</div>", unsafe_allow_html=True)
                if st.button("削除", key=f"del_{i}"):
                    st.session_state.saved_recipes.pop(i)
                    st.rerun()
