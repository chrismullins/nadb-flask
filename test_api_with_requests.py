#####
# Test deleting a user!
#####

url = 'http://localhost:5000'
delete_endpoint = '/users'
# you'll need to get this from the local storage in your web browser
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MTY1MDI4OTksImlhdCI6MTUxMzkxMDg5OSwic3ViIjo0fQ.p06Lt-QYmbFBvHZtJzPlTxGAWIpXuWiaoOfOhcxdv0g'
headers = {
    'Authorization': 'Bearer {}'.format(token),
    'content_type': 'application/json',
    'data': {}
}

r = requests.delete(url + delete_endpoint + '/3', headers=headers)
print(r.text)



#####
# Test adding a user!
#####
add_user_endpoint = '/users' # same as above
data = {
    'email': 'test@test.com',
    'password': 'test',
    'username': 'test'
}
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MTY1MDI4OTksImlhdCI6MTUxMzkxMDg5OSwic3ViIjo0fQ.p06Lt-QYmbFBvHZtJzPlTxGAWIpXuWiaoOfOhcxdv0g'
headers = {
    'Authorization': 'Bearer {}'.format(token),
    'content_type': 'application/json'
}
# !!NOTE: data must be type 'str' hence json.dumps while headers can be dict
r = requests.post(url + add_user_endpoint, data=json.dumps(data), headers=headers)
print(r.text)


####
# Test modifying a user!
####
modify_user_endpoint = '/users' # same as above
data = {
    'username': 'chris',
    'email': 'chris@newdomain.com' # this is the change we're making
}
headers = {
    'Authorization': 'Bearer {}'.format(token)
    'content_type': 'application/json'
}
# user's id = 1
r = requests.put(url + modify_user_endpoint + '/1', data=json.dumps(data), headers=headers)
print(r.text)