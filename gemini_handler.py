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
vision_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-latest',
    system_instruction="あなたは画像解析のエキスパートです。余計な会話はせず、結果のみを出力します。"
)

recipe_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-latest',
    system_instruction="あなたはプロの料理研究家兼管理栄養士です。"
)

def resize_image_for_api(image, max_size=1024):
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
    processed_images = [resize_image_for_api(img) for img in images]
    prompt = """
    写っている食材をすべてリストアップしてください。
    出力フォーマット:
    - [食材名]
    - [食材名]
    余計な文章は含めず、箇条書きのリストのみを出力してください。
    """
    generation_config = genai.types.GenerationConfig(
        max_output_tokens=300,
        temperature=0.0
    )
    try:
        content = [prompt] + processed_images
        response = vision_model.generate_content(
            content, 
            stream=True,
            generation_config=generation_config
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except ResourceExhausted:
         yield "APIの利用制限（1分間の回数制限）に達しました。1分ほど時間を空けてから、もう一度ボタンを押してください。"
    except Exception as e:
        yield f"エラー: {str(e)}"

def generate_recipe(ingredients_text, mode, num_dishes, is_choi_tashi=False):
    base_prompt = f"""
    【使用する食材リスト】
    {ingredients_text}
    """
    if is_choi_tashi:
        base_prompt += """
        上記の食材リストに加え、一般家庭によくある食材（卵、牛乳、玉ねぎ、各種調味料など）から2〜3品を足して、
        より満足度の高いレシピ・献立にしてください。
        """
    else:
        base_prompt += """
        上記の食材を使って、レシピを提案してください。
        """
    base_prompt += f"""
    【重要なお願い】
    全く異なるアプローチの献立を3パターン（案A, 案B, 案C）提案してください。
    各案はそれぞれ【{num_dishes}品】構成にしてください。
    
    出力フォーマット:
    ---
    ## 案A: [コンセプト/料理名]
    調理時間: [約〇分]
    (以下、{num_dishes}品のレシピ詳細)
    - 材料: ...
    - 手順: ...
    - ポイント: ...
    ---
    ## 案B: ...
    ---
    ## 案C: ...
    """
    if "離乳食" in mode:
        baby_food_stage = mode.replace("離乳食", "").strip("()")
        base_prompt += f"""
        【重要】
        今回は「{baby_food_stage}」向けの離乳食レシピです。
        1. 食材の大きさ、固さは{baby_food_stage}の赤ちゃんが安全に食べられるものにしてください。
        2. 味付けは月齢に合わせてごく薄味、または素材の味のみにしてください。
        3. アレルギー特定原材料が含まれる場合は注意書きをしてください。
        4. はちみつ、黒糖、刺身等の危険な食材は絶対に使用しないでください。
        5. 必ず冒頭に以下の警告文を表示してください。
        「注意：アレルギーや窒息に注意し、初めての食材は少量から試してください。」
        """
    else:
        base_prompt += """
        ターゲット: 忙しい人、家にある食材を使い切りたい人
        手軽に作れる家庭料理を提案してください。
        """
    try:
        response = recipe_model.generate_content(base_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except ResourceExhausted:
         yield "APIの利用制限に達しました。1分ほど時間を空けてから再度お試しください。"
    except Exception as e:
        yield f"エラーが発生しました: {str(e)}"
