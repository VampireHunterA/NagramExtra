with open('final_keystore.b64') as f: s=f.read()
print('Length:', len(s))
print('Underscore:', '_' in s)
print('First 20:', s[:20])
