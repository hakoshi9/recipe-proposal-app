import os
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please set it.")

genai.configure(api_key=GOOGLE_API_KEY)

# --- 設定: モデルをグローバルで初期化 ---
# システムプロンプトを事前に設定し、役割を明確化
vision_model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="あなたは画像解析のエキスパートです。余計な会話はせず、結果のみを出力します。"
)

recipe_model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="あなたはプロの料理研究家兼管理栄養士です。"
)

# --- 高速化のための画像リサイズ関数 ---
def resize_image_for_api(image, max_size=1024):
    """
    画像をAIに適したサイズにリサイズします。
    画質を維持しつつ、長辺をmax_size以下にします。
    """
    if not isinstance(image, Image.Image):
         return image

    width, height = image.size
    if max(width, height) <= max_size:
        return image

    ratio = max_size / max(width, height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def identify_ingredients(images):
    """
    Analyzes images and lists visible ingredients.
    """
    
    # 1. 画像の前処理（リサイズによる高速化）
    processed_images = [resize_image_for_api(img) for img in images]

    prompt = """
    写っている食材をすべてリストアップしてください。
    
    出力フォーマット:
    - [食材名]
    - [食材名]
    
    余計な文章は含めず、箇条書きのリストのみを出力してください。
    """
    
    # 2. 生成設定（トークン制限でレスポンスを早く切る & 決定論的にする）
    generation_config = genai.types.GenerationConfig(
        max_output_tokens=300,
        temperature=0.0
    )

    try:
        content = [prompt] + processed_images
        
        # vision_modelを使用
        response = vision_model.generate_content(
            content, 
            stream=True,
            generation_config=generation_config
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except ResourceExhausted:
         yield "⚠️ APIの利用制限（1分間の回数制限）に達しました。1分ほど時間を空けてから、もう一度ボタンを押してください。☕"
    except Exception as e:
        yield f"エラー: {str(e)}"

def generate_recipe(ingredients_text, mode, num_dishes, is_choi_tashi=False):
    """
    Generates recipes based on the provided ingredients list, mode, and number of dishes.
    Always generates 3 patterns (Plan A, B, C).
    """
    
    # ベースプロンプト
    base_prompt = f"""
    【使用する食材リスト】
    {ingredients_text}
    """

    if is_choi_tashi:
        base_prompt += f"""
        上記の食材リストに加え、**一般家庭によくある食材（卵、牛乳、玉ねぎ、各種調味料など）**から2〜3品を「ちょい足し」して、
        より美味しく、満足度の高いレシピ・献立にグレードアップしてください。
        """
    else:
        base_prompt += f"""
        上記の食材（すべてでなくてもよい、調味料は適宜追加可）を使って、
        美味しくて作りやすいレシピを提案してください。
        """
        
    # 共通の出力指示（3パターン提案 & 調理時間）
    base_prompt += f"""
    【重要なお願い】
    全く異なるアプローチの献立を**3パターン（案A, 案B, 案C）**提案してください。
    （例: 案Aは和風、案Bは洋風、案Cは中華風など、味付けやジャンルを変えてください）
    各案はそれぞれ【{num_dishes}品】構成にしてください。
    
    出力フォーマット:
    
    ---
    ## 案A: [コンセプト/料理名]
    **調理時間:** [約〇分]
    (以下、{num_dishes}品のレシピ詳細)
    - 材料: ...
    - 手順: ...
    - ポイント: ...
    
    ---
    ## 案B: [コンセプト/料理名]
    **調理時間:** [約〇分]
    (以下、{num_dishes}品のレシピ詳細)
    
    ---
    ## 案C: [コンセプト/料理名]
    **調理時間:** [約〇分]
    (以下、{num_dishes}品のレシピ詳細)
    """

    # 離乳食などの条件
    if "離乳食" in mode:
        baby_food_stage = mode.replace("離乳食", "").strip("()")
        base_prompt += f"""
        
        【重要】
        今回は「{baby_food_stage}」向けの離乳食レシピです。
        以下の点に厳重に注意してください:
        1. 食材の大きさ、固さは{baby_food_stage}の赤ちゃんが安全に食べられるものにしてください。
        2. 味付けは月齢に合わせてごく薄味、または素材の味のみにしてください。
        3. アレルギー特定原材料が含まれる場合は注意書きをしてください。
        4. はちみつ、黒糖、刺身などの乳児ボツリヌス症や食中毒のリスクがある食材は絶対に使用しないでください。
        5. 必ず冒頭に以下の警告文を表示してください。
        「⚠️ アレルギーや窒息に注意し、初めての食材は少量から試してください。」
        """
    else:
        # General cooking mode
        base_prompt += f"""
        
        ターゲット: 忙しい人、家にある食材を使い切りたい人
        手軽に作れる家庭料理を提案してください。
        """

    try:
        # recipe_modelを使用
        response = recipe_model.generate_content(base_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except ResourceExhausted:
         yield "⚠️ APIの利用制限（1分間の回数制限）に達しました。1分ほど時間を空けてから、もう一度ボタンを押してください。☕"
    except Exception as e:
        yield f"エラーが発生しました: {str(e)}"
