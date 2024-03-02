import json
import bpy
import os

def load_translations(language_code):
    # 根据语言代码加载相应的翻译文件
    file_path = os.path.join(os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "lang"),str(f"{language_code}.json"))
    print(file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        translations = json.load(file)
    return translations

def translate(key):
    language_code=bpy.app.translations.locale
    translations = load_translations(language_code)
    # 检查是否存在对应的键名，如果存在则返回对应的翻译文本，否则返回空字符串
    if key in translations:
        return translations[key]
    else:
        return ""

