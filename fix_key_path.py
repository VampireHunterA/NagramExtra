with open('TMessagesProj/build.gradle','r') as f: text=f.read()
text=text.replace('nagramxturbo.jks','temp_keystore.jks')
with open('TMessagesProj/build.gradle','w') as f: f.write(text)
print('OK')
