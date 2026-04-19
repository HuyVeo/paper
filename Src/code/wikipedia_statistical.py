import pandas as pd
import wikipedia
import time
import os

wikipedia.set_lang("vi")

input_file = r'D:\MGEEMS\dataset\concept.txt'
output_file = r'D:\MGEEMS\wikipedia_definitions2.csv'


with open(input_file, 'r', encoding='utf-8-sig') as f:
    concepts = [line.strip() for line in f if line.strip()]

# Remove duplicates while preserving order
seen = set()
unique_concepts = []
for c in concepts:
    if c not in seen:
        seen.add(c)
        unique_concepts.append(c)

print(f"Total unique concepts: {len(unique_concepts)}")

# Resume from existing results if any
results = []
done_concepts = set()
if os.path.exists(output_file):
    df_done = pd.read_csv(output_file, encoding='utf-8-sig')
    results = df_done.to_dict('records')
    done_concepts = set(df_done['concept'].tolist())
    print(f"Resuming: {len(done_concepts)} already done")

for i, concept in enumerate(unique_concepts):
    if concept in done_concepts:
        continue

    search_term = concept.replace('_', ' ')
    definition = ''
    status = ''

    try:
        page = wikipedia.page(search_term, auto_suggest=True)
        summary = page.summary
        # Take first 2 sentences as definition
        sentences = summary.split('. ')
        definition = '. '.join(sentences[:2])
        if not definition.endswith('.'):
            definition += '.'
        status = 'found'
    except wikipedia.exceptions.DisambiguationError as e:
        # Try first option
        try:
            page = wikipedia.page(e.options[0], auto_suggest=False)
            sentences = page.summary.split('. ')
            definition = '. '.join(sentences[:2])
            if not definition.endswith('.'):
                definition += '.'
            status = 'disambiguation_resolved'
        except Exception:
            definition = ''
            status = 'disambiguation_failed'
    except wikipedia.exceptions.PageError:
        definition = ''
        status = 'not_found'
    except Exception as e:
        definition = ''
        status = f'error: {str(e)[:50]}'

    results.append({
        'concept': concept,
        'search_term': search_term,
        'definition': definition,
        'status': status
    })

    if (i + 1) % 10 == 0 or i == len(unique_concepts) - 1:
        df_out = pd.DataFrame(results)
        df_out.to_csv(output_file, index=False, encoding='utf-8-sig')
        found = sum(1 for r in results if 'found' in r['status'])
        print(f"[{i+1}/{len(unique_concepts)}] Found: {found}/{len(results)}")

    time.sleep(0.5)  # Rate limiting

df_out = pd.DataFrame(results)
df_out.to_csv(output_file, index=False, encoding='utf-8-sig')
found = sum(1 for r in results if 'found' in r['status'])
print(f"\nDone! Found: {found}/{len(results)}")
print(f"Results saved to: {output_file}")
