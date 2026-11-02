with open('TMessagesProj/build.gradle') as f: text=f.read()
text=text.replace('temp_keystore.jks','nagramxturbo.jks')
with open('TMessagesProj/build.gradle','w') as f: f.write(text)
print('build.gradle restored to nagramxturbo.jks')
