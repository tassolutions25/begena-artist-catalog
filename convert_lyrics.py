import json
import docx
import os
import re

def normalize_amharic(text):
    if not text: return ""
    replacements = {
        'ሐ': 'ሀ', 'ሑ': 'ሁ', 'ሒ': 'ሂ', 'ሓ': 'ሃ', 'ሔ': 'ሄ', 'ሕ': 'ህ', 'ሖ': 'ሆ',
        'ኀ': 'ሀ', 'ኁ': 'ሁ', 'ኂ': 'ሂ', 'ኃ': 'ሃ', 'ኄ': 'ሄ', 'ኅ': 'ህ', 'ኆ': 'ሆ',
        'ሠ': 'ሰ', 'ሡ': 'ሱ', 'ሢ': 'ሲ', 'ሣ': 'ሳ', 'ሤ': 'ሴ', 'ሥ': 'ስ', 'ሦ': 'ሶ',
        'ዐ': 'አ', 'ዑ': 'ኡ', 'ዒ': 'ኢ', 'ዓ': 'አ', 'ዔ': 'ኤ', 'ዕ': 'እ', 'ዖ': 'ኦ',
        'ፀ': 'ጸ', 'ፁ': 'ጹ', 'ጺ': 'ጺ', 'ፃ': 'ጻ', 'ፄ': 'ጼ', 'ፅ': 'ጽ', 'ፆ': 'ጾ'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[\.\,\;\:\?\*\!]', ' ', text)
    return ' '.join(text.split()).strip()

def is_tuning_numbers(text):
    text_strip = text.strip()
    if not text_strip: return False
    cleaned = re.sub(r'[\d\s\-\(\)\/xX+]', '', text_strip)
    norm_cleaned = normalize_amharic(cleaned)
    if not norm_cleaned.strip() or norm_cleaned.strip() == "በበገና":
        return True
    return False

def is_tuning_header(text):
    text_strip = text.strip()
    norm_text = normalize_amharic(text_strip)
    if "ቅኝት" in norm_text: return True
    if re.search(r'ቅ\s*ኝ\s*ት', text_strip): return True
    return False

def clean_title(title):
    title = re.sub(r'\(.*?\)', '', title)
    return normalize_amharic(title)

def process_lyrics():
    print("Loading catalog...")
    with open('artist_catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)

    print("Loading document...")
    doc = docx.Document('የበገና መዝሙር ግጥሞች.docx')
    paragraphs = doc.paragraphs
    print(f"Loaded {len(paragraphs)} paragraphs.")

    catalog_songs = []
    for artist in catalog['artists']:
        for song in artist['songs']:
            rel_path = song['lyrics_asset_file']
            if 'assets/data/lyrics/' not in rel_path:
                rel_path = rel_path.replace('assets/lyrics/', 'assets/data/lyrics/')
            target_file = os.path.join(os.getcwd(), rel_path)
            catalog_songs.append({
                'title': song['title'],
                'clean_title': clean_title(song['title']),
                'artist': normalize_amharic(artist['name']),
                'target_file': target_file
            })

    print("Pre-calculating paragraph metadata...")
    para_info = []
    for i, p in enumerate(paragraphs):
        text = p.text.strip()
        norm_text = normalize_amharic(text)
        para_info.append({
            'text': text,
            'norm_text': norm_text,
            'is_tuning_header': is_tuning_header(text),
            'len': len(text)
        })

    print("Matching songs...")
    found_map = {}
    missing_songs = []

    for song in catalog_songs:
        search_title = song['clean_title']
        artist_name = song['artist']
        best_match = -1
        best_score = -1
        
        for i, info in enumerate(para_info):
            if info['len'] > 150 or not info['norm_text']: continue
            
            score = 0
            if search_title == info['norm_text']:
                score += 150
            elif search_title in info['norm_text']:
                score += 80
            
            if score > 0:
                has_tuning = False
                for j in range(1, 6):
                    if i + j < len(para_info) and para_info[i+j]['is_tuning_header']:
                        has_tuning = True
                        break
                if has_tuning: score += 100
                if artist_name in info['norm_text']: score += 50
                
                if score > best_score:
                    best_score = score
                    best_match = i
        
        # Threshold 100
        if best_match != -1 and best_score >= 100:
            found_map[song['title']] = best_match
        else:
            missing_songs.append(f"{song['artist']} - {song['title']}")

    print(f"Matched {len(found_map)} songs. Missing {len(missing_songs)}.")

    sorted_found = sorted(found_map.items(), key=lambda x: x[1])
    all_potential_boundaries = [i for i, p in enumerate(para_info) if p['is_tuning_header']]
    
    for i, (title, start_idx) in enumerate(sorted_found):
        next_possible = [idx for idx in all_potential_boundaries if idx > start_idx + 1]
        if i + 1 < len(sorted_found):
            next_possible.append(sorted_found[i+1][1])
        
        end_idx = min(next_possible) if next_possible else len(paragraphs)

        song_entry = next(s for s in catalog_songs if s['title'] == title)
        song_lines = []
        skip_mode = False
        
        for p_idx in range(start_idx + 1, end_idx):
            text = paragraphs[p_idx].text
            text_strip = text.strip()
            if not text_strip:
                if song_lines and song_lines[-1]['text'] != '':
                    song_lines.append({'text': '', 'indent': 0})
                skip_mode = False
                continue
            if is_tuning_header(text_strip):
                skip_mode = True
                continue
            if skip_mode:
                if is_tuning_numbers(text_strip): continue
                else:
                    norm = normalize_amharic(text_strip)
                    if not re.sub(r'[ቅኝትበበገና\d\s\-\(\)\/xX+]', '', norm).strip(): continue
                    skip_mode = False
            
            leading_spaces = 0
            for char in text:
                if char == ' ': leading_spaces += 1
                elif char == '\t': leading_spaces += 4
                else: break
            indent = 24 if leading_spaces >= 3 else 0
            song_lines.append({'text': text_strip, 'indent': indent})

        final_paragraphs = []
        if song_lines:
            curr_text = []
            curr_indent = song_lines[0]['indent']
            for line in song_lines:
                if line['text'] == '':
                    if curr_text:
                        final_paragraphs.append({'text': '\n'.join(curr_text), 'indent': curr_indent})
                        curr_text = []
                    continue
                if line['indent'] == curr_indent:
                    curr_text.append(line['text'])
                else:
                    if curr_text:
                        final_paragraphs.append({'text': '\n'.join(curr_text), 'indent': curr_indent})
                    curr_text = [line['text']]
                    curr_indent = line['indent']
            if curr_text:
                final_paragraphs.append({'text': '\n'.join(curr_text), 'indent': curr_indent})

        output = {"paragraphs": final_paragraphs}
        os.makedirs(os.path.dirname(song_entry['target_file']), exist_ok=True)
        with open(song_entry['target_file'], 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    with open('missing_songs.log', 'w', encoding='utf-8') as f:
        for song_str in missing_songs:
            f.write(song_str + '\n')

if __name__ == "__main__":
    process_lyrics()
