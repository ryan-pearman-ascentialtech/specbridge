import re

with open('specbridge.html', 'r', encoding='utf-8') as f:
    content = f.read()

original = content
changes = []

# FIX 1 — Gap panel: add max-height and overflow so flags scroll not clip
old1 = 'position: sticky; top: 72px; }'
new1 = 'position: sticky; top: 72px; max-height: calc(100vh - 120px); overflow-y: auto; }'
if old1 in content:
    content = content.replace(old1, new1)
    changes.append('Fix 1 DONE: gap panel scroll added')
else:
    changes.append('Fix 1 SKIP: gap-panel rule not found exactly - check manually')

# FIX 2 — Labour rates: replace wrong placeholder rates with 2025 ERP actuals
rates = [
    ('| \ |', '| \.69 |'),
    ('| \ |', '| \.73 |'),
    ('| \ |', '| \.93 |'),
    ('| \ |', '| \.51 |'),
    ('| \ |', '| \.22 |'),
    ('| \ |', '| \.28 |'),
]
for old, new in rates:
    if old in content:
        content = content.replace(old, new)
        changes.append(f'Fix 2 DONE: {old.strip()} -> {new.strip()}')
    else:
        changes.append(f'Fix 2 SKIP: {old.strip()} not found')

# FIX 3 — Add confirmed rate note to RFQ prompt
rate_note = 'BEP GR 2025 confirmed ERP labour rates: PM \.69/hr, ME \.73/hr, EE \.93/hr, SE \.51/hr, Fab \.80/hr, Machine Build \.22/hr, Panel Build \.94/hr, Field Service \.28/hr. Use these exact rates in the labour table.'
if rate_note not in content:
    # Find the RFQ function and inject before the prompt closing
    marker = 'Generate a professional RFQ'
    if marker in content:
        content = content.replace(marker, rate_note + ' ' + marker)
        changes.append('Fix 3 DONE: rate note injected into RFQ prompt')
    else:
        marker2 = 'rfq' 
        changes.append('Fix 3 SKIP: RFQ prompt marker not found')
else:
    changes.append('Fix 3 SKIP: rate note already present')

if content != original:
    with open('specbridge.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('FILE SAVED')
else:
    print('NO CHANGES MADE')

for c in changes:
    print(c)
