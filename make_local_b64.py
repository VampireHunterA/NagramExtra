import base64
with open('local.properties') as f: data=f.read()
with open('local_for_secret.b64','w') as f: f.write(base64.b64encode(data.encode()).decode('ascii'))
print('local_for_secret.b64 created', len(open('local_for_secret.b64').read()))
