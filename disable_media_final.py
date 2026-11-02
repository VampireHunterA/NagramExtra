with open('settings.gradle') as f: lines=f.read().splitlines()
start=None; end=None
for i,l in enumerate(lines):
    if 'androidxMediaLibraries.each' in l: start=i
    if start is not None and "file('TMessagesProj_Modules/media3').mkdirs()" in l: end=i; break
if start is not None and end is not None:
    new=lines[:start]+['/* media disabled */']+lines[end+1:]
    with open('settings.gradle','w') as f: f.write('\n'.join(new))
    print('Disabled')
