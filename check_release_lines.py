with open('.github/workflows/release.yml') as f: lines=f.read().splitlines()
for i in range(50,65):
    print(i+1, lines[i] if i<len(lines) else '')
