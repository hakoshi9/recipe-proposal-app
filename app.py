import streamlit as st
from PIL import Image
import gemini_handler
import re
import datetime
import streamlit.components.v1 as components
import urllib.parse
import os
import json
import hashlib

# --- ページ設定 ---
st.set_page_config(
    page_title="レシピ提案AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- キャッシュファイルのパス ---
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".recipe_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def save_cache(key, data):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_cache(key):
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# --- セッション状態の初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = "作る"
if 'ingredients_list' not in st.session_state:
    st.session_state.ingredients_list = ""
if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = ""
if 'saved_recipes' not in st.session_state:
    st.session_state.saved_recipes = []
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'is_choi' not in st.session_state:
    st.session_state.is_choi = False
if 'use_all' not in st.session_state:
    st.session_state.use_all = False
if 'extra_request' not in st.session_state:
    st.session_state.extra_request = ""
if 'session_key' not in st.session_state:
    # セッションごとに一意なキーを生成
    import uuid
    st.session_state.session_key = str(uuid.uuid4())[:8]
if 'cache_loaded' not in st.session_state:
    st.session_state.cache_loaded = False

# --- キャッシュからの復元（初回のみ） ---
if not st.session_state.cache_loaded:
    # 最新のキャッシュファイルを探して復元
    cache_files = sorted(
        [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(CACHE_DIR, f)),
        reverse=True
    )
    if cache_files:
        latest = load_cache(cache_files[0].replace(".json", ""))
        if latest:
            if not st.session_state.recipe_result and latest.get("recipe_result"):
                st.session_state.recipe_result = latest["recipe_result"]
            if not st.session_state.ingredients_list and latest.get("ingredients_list"):
                st.session_state.ingredients_list = latest["ingredients_list"]
    st.session_state.cache_loaded = True

# --- URLパラメータでページ切り替え ---
params = st.query_params
if "nav" in params:
    nav_val = params["nav"]
    if nav_val in ["作る", "確認", "保存"] and st.session_state.page != nav_val:
        st.session_state.page = nav_val
        st.query_params.clear()
        st.rerun()

page = st.session_state.page
active_create  = "nav-active" if page == "作る" else ""
active_confirm = "nav-active" if page == "確認" else ""
active_save    = "nav-active" if page == "保存" else ""

# --- CSS + 固定フッター ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');

    html, body {{
        font-family: 'Noto Sans JP', sans-serif !important;
        background-color: #FFFFFF !important;
        height: 100%;
        margin: 0;
    }}

    header[data-testid="stHeader"] {{ display: none !important; }}
    footer {{ display: none !important; }}

    [data-testid="stAppViewContainer"] {{
        display: flex !important;
        flex-direction: column !important;
        min-height: 100vh !important;
    }}

    [data-testid="stAppViewContainer"] > section.main {{
        flex: 1 !important;
        overflow-y: auto !important;
    }}

    .main .block-container {{
        padding-bottom: 20px !important;
        padding-top: 15px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }}

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
        align-items: stretch;
        padding: 0;
        z-index: 999999;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.06);
        box-sizing: border-box;
    }}

    .nav-btn {{
        flex: 1;
        text-align: center;
        background: none;
        border: none;
        border-bottom: 3px solid transparent;
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 15px;
        font-weight: 700;
        color: #888888;
        padding: 12px 0 14px 0;
        cursor: pointer;
        transition: color 0.15s, border-color 0.15s;
        -webkit-tap-highlight-color: transparent;
    }}

    .nav-btn.nav-active {{
        color: #FF9900;
        border-bottom: 3px solid #FF9900;
    }}

    .content-spacer {{
        height: 80px;
    }}

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

<!-- 固定フッターナビゲーション -->
<div class="fixed-footer">
    <form method="get" style="flex:1;margin:0;display:flex;">
        <button class="nav-btn {active_create}" name="nav" value="作る" type="submit">作る</button>
    </form>
    <form method="get" style="flex:1;margin:0;display:flex;">
        <button class="nav-btn {active_confirm}" name="nav" value="確認" type="submit">確認</button>
    </form>
    <form method="get" style="flex:1;margin:0;display:flex;">
        <button class="nav-btn {active_save}" name="nav" value="保存" type="submit">保存</button>
    </form>
</div>
""", unsafe_allow_html=True)

# --- メインコンテンツ ---
if page == "作る":
    st.markdown("<h1>レシピを作る</h1>", unsafe_allow_html=True)
    st.caption("写真を解析して献立をご提案します")

    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("ジャンル", ["一般的な料理", "離乳食(5-6ヶ月)", "離乳食(7-8ヶ月)", "離乳食(9-11ヶ月)", "離乳食(12-18ヶ月)"])
    with c2:
        num_dishes = st.radio("品数", (1, 2, 3), format_func=lambda x: f"{x}品", horizontal=True)

    files = st.file_uploader("食材の写真をアップロード", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

    if files:
        cols = st.columns(min(len(files), 4))
        for i, f in enumerate(files):
            with cols[i % 4]:
                st.image(Image.open(f), use_column_width=True)

        # 画像選択後、「食材を読み取る」ボタンが見えるよう自動スクロール
        components.html("""
        <script>
        window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({
            top: 99999,
            behavior: 'smooth'
        });
        </script>
        """, height=0)

        if st.button("1. 食材を読み取る", use_container_width=True):
            with st.status("画像を解析中...", expanded=True) as status:
                st.write("AIが食材を識別しています。しばらくお待ちください。")
                stream = gemini_handler.identify_ingredients([Image.open(f) for f in files])
                st.session_state.ingredients_list = st.write_stream(stream)
                status.update(label="読み取り完了", state="complete", expanded=False)
            # 読み取り完了後、画面を下にスクロールして結果を表示
            components.html("""
            <script>
            window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({
                top: 99999,
                behavior: 'smooth'
            });
            </script>
            """, height=0)

    if st.session_state.ingredients_list:
        st.markdown("### 2. 食材リスト（編集可）")
        edited = st.text_area("食材リスト", value=st.session_state.ingredients_list, height=100, label_visibility="collapsed")
        if st.session_state.is_generating:
            st.info("レシピを考案中です。しばらくお待ちください...")
        else:
            is_choi = st.checkbox("ちょい足しモード（画像に無い食材も２～３品使う）", value=False)
            use_all = st.checkbox("全食材を使うモード（すべての食材種類をレシピに含める）", value=False)

            with st.expander("追加の要望（任意）", expanded=False):
                extra_request = st.text_area(
                    "追加要望",
                    value="",
                    height=80,
                    placeholder="例: 辛いものは避けて、和食でまとめてください、こどもが喘気なのでアレルギーに注意して...",
                    label_visibility="collapsed"
                )

            if st.button("3. レシピを生成", use_container_width=True):
                st.session_state.is_generating = True
                st.session_state.is_choi = is_choi
                st.session_state.use_all = use_all
                st.session_state.extra_request = extra_request
                st.rerun()


    # 生成フラグが立っている場合に実際の処理を実行
    if st.session_state.get('is_generating') and st.session_state.ingredients_list:
        edited = st.session_state.ingredients_list
        is_choi = st.session_state.is_choi
        use_all = st.session_state.use_all
        extra_request = st.session_state.extra_request
        with st.spinner("レシピを考案中..."):
            accumulated = "".join(
                chunk for chunk in gemini_handler.generate_recipe(edited, mode, num_dishes, is_choi, use_all=use_all, extra_request=extra_request)
            )
        st.session_state.recipe_result = accumulated
        st.session_state.ingredients_list = edited
        st.session_state.is_generating = False
        save_cache(st.session_state.session_key, {
            "recipe_result": accumulated,
            "ingredients_list": edited
        })
        st.session_state.page = "確認"
        st.rerun()

elif page == "確認":
    # ページ表示時に最上部へスクロール
    components.html("""
    <script>
    window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTo({
        top: 0,
        behavior: 'instant'
    });
    </script>
    """, height=0)
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
                    section = text[start:end]
                    # 栄養素概算セクションを切り出す
                    nutrition_pattern = re.compile(r'###\s*栄養素概算')
                    nutrition_match = nutrition_pattern.search(section)
                    if nutrition_match:
                        recipe_body = section[:nutrition_match.start()].strip()
                        nutrition_body = section[nutrition_match.start():].strip()
                    else:
                        recipe_body = section.strip()
                        nutrition_body = None

                    st.markdown(f"<div class='recipe-card'>{recipe_body}</div>", unsafe_allow_html=True)

                    if nutrition_body:
                        with st.expander("栄養素概算を見る", expanded=False):
                            st.markdown(nutrition_body)


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

# フッターに隠れないためのスペーサー
st.markdown("<div class='content-spacer'></div>", unsafe_allow_html=True)
