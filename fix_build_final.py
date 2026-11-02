with open('TMessagesProj/build.gradle') as f: text=f.read()
text=text.replace('nagramxturbo.jks','temp_keystore.jks')
with open('TMessagesProj/build.gradle','w') as f: f.write(text)
print('build.gradle -> temp_keystore.jks')
