with open('.github/workflows/release.yml') as f: lines=f.read().splitlines()
new=[]
skipping=False
for l in lines:
    if '- name: Decode keystore' in l:
        skipping=True
        new.append('# SKIPPED: Decode keystore (embedded temp_keystore.jks in repo)')
        continue
    if skipping and 'run:' in l and 'base64' in l:
        new.append('# SKIPPED: KEYSTORE decode (embedded key in repo)')
        skipping=False
        continue
    if skipping and l.strip().startswith('-') and 'name:' not in l and 'run:' not in l:
        skipping=False
    new.append(l)
with open('.github/workflows/release.yml','w') as f: f.write('\n'.join(new))
print('Done')
