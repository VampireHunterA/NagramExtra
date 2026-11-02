import os, hashlib, base64
jks='temp_keystore.jks'; b64='key.b64'
print('1. jks exists:', os.path.exists(jks))
if os.path.exists(jks) and os.path.exists(b64):
    jhash=hashlib.md5(open(jks,'rb').read()).hexdigest()[:8]
    with open(b64) as f: dec=base64.b64decode(f.read())
    dec_hash=hashlib.md5(dec).hexdigest()[:8]
    print('   jks md5:', jhash)
    print('   decoded from b64 md5:', dec_hash)
    print('   MATCH:', jhash==dec_hash)
else:
    print('   FILES MISSING')
