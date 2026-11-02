with open('TMessagesProj/build.gradle') as f: text=f.read()
old = "    api project(\"TMessagesProj_Modules:media3:media-lib-exoplayer\")\n    api project(\"TMessagesProj_Modules:media3:media-lib-exoplayer-dash\")\n    api project(\"TMessagesProj_Modules:media3:media-lib-exoplayer-hls\")\n    api project(\"TMessagesProj_Modules:media3:media-lib-decoder-ffmpeg\")\n    api project(\"TMessagesProj_Modules:media3:media-lib-session\")"
new = "    // media disabled\n    // api project(\"TMessagesProj_Modules:media3:media-lib-exoplayer\")\n    // api project(\"TMessagesProj_Modules:media3:media-lib-exoplayer-dash\")\n    // api project(\"TMessagesProj_Modules:media3:media-lib-exoplayer-hls\")\n    // api project(\"TMessagesProj_Modules:media3:media-lib-decoder-ffmpeg\")\n    // api project(\"TMessagesProj_Modules:media3:media-lib-session\")"
text = text.replace(old, new)
with open('TMessagesProj/build.gradle','w') as f: f.write(text)
print('Deps disabled')
