import requests
import time

API_KEY = "883d55b5-2ef6-473a-b404-733a0b5b228b"
INPUT_FILE = r"D:\MGEEMS\1.txt"
OUTPUT_FILE = r"D:\MGEEMS\3.txt"


def get_synset_ids(word):
    """Lấy Synset IDs tiếng Việt cho một từ"""
    url = "https://babelnet.io/v6/getSynsetIds"
    params = {"lemma": word, "searchLang": "VI", "key": API_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return [item["id"] for item in data]
    except Exception as e:
        print(f"  ❌ Lỗi getSynsetIds '{word}': {e}")
    return []


def get_vi_gloss(synset_id):
    """Lấy gloss tiếng Việt đầu tiên có được từ một synset"""
    url = "https://babelnet.io/v6/getSynset"
    params = {"id": synset_id, "targetLang": "VI", "key": API_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for g in data.get("glosses", []):
                if g.get("language") == "VI":
                    gloss = g.get("gloss", "").strip()
                    if gloss:
                        return gloss
    except Exception as e:
        print(f"  ❌ Lỗi getSynset {synset_id}: {e}")
    return None


def fetch_gloss_for_term(term):
    """Thử nhiều biến thể của term để tìm gloss tiếng Việt tốt nhất"""
    # Thử cả dạng có gạch dưới và dạng có dấu cách
    variants = [term, term.replace("_", " ")]
    # Loại trùng nhưng giữ thứ tự
    variants = list(dict.fromkeys(variants))

    for variant in variants:
        ids = get_synset_ids(variant)
        for sid in ids:
            gloss = get_vi_gloss(sid)
            time.sleep(0.1)
            if gloss:
                return gloss
        time.sleep(0.1)
    return None


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        terms = [line.strip() for line in f if line.strip()]

    print(f"📚 Tổng số thuật ngữ: {len(terms)}\n")
    results = []

    for i, term in enumerate(terms, 1):
        print(f"[{i}/{len(terms)}] 🔍 {term}")
        gloss = fetch_gloss_for_term(term)
        if gloss:
            results.append(f"{term}\t{gloss}")
            print(f"  ✅ {gloss[:80]}...")
        else:
            results.append(f"{term}\t[KHÔNG TÌM THẤY GLOSS]")
            print("  ⚠️ Không có gloss VI")
        time.sleep(0.2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"\n✅ Đã lưu: {OUTPUT_FILE}")
    print(f"📊 Tổng dòng: {len(results)}")


if __name__ == "__main__":
    main()