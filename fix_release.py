with open('.github/workflows/release.yml') as f: text=f.read()
old = 'echo "$KEYSTORE" | base64 -d > TMessagesProj/nagramxturbo.jks'
new = "printf '%s' \"$KEYSTORE\" | base64 -d > TMessagesProj/nagramxturbo.jks"
if old in text:
    text=text.replace(old,new)
    with open('.github/workflows/release.yml','w') as f: f.write(text)
    print('Fixed decode line')
else:
    print('Line not found, checking...')
    for i,line in enumerate(text.splitlines()):
        if 'base64 -d' in line and 'nagramxturbo' in line:
            print(i+1, line)
