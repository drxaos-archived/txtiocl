import os
import urllib
import urllib2
import cookielib
import re
import getpass



# Your accounts

user_gmail_email   = "your-gmail-email@gmail.com"
user_txtio_account = "your-txtio-account"






txtio_app_name = "txt.io"
txtio_domain = "txt.io"

target_authenticated_google_app_engine_uri = 'http://'+txtio_domain+'/'+user_txtio_account+'/m'



# Asking for password
user_gmail_password=getpass.getpass("Gmail password: ")

# we use a cookie to authenticate with Google App Engine
#  by registering a cookie handler here, this will automatically store the 
#  cookie returned when we use urllib2 to open http://currentcost.appspot.com/_ah/login
cookiejar = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
urllib2.install_opener(opener)

#
# get an AuthToken from Google accounts
#
auth_uri = 'https://www.google.com/accounts/ClientLogin'
authreq_data = urllib.urlencode({ "Email":   user_gmail_email,
                                  "Passwd":  user_gmail_password,
                                  "service": "ah",
                                  "source":  txtio_app_name,
                                  "accountType": "HOSTED_OR_GOOGLE" })
auth_req = urllib2.Request(auth_uri, data=authreq_data)
auth_resp = urllib2.urlopen(auth_req)
auth_resp_body = auth_resp.read()
#print auth_resp_body
# auth response includes several fields - we're interested in 
#  the bit after Auth= 
auth_resp_dict = dict(x.split("=")
                      for x in auth_resp_body.split("\n") if x)
authtoken = auth_resp_dict["Auth"]

#
# get a cookie
# 
#  the call to request a cookie will also automatically redirect us to the page
#   that we want to go to
#  the cookie jar will automatically provide the cookie when we reach the 
#   redirected location

# this is where I actually want to go to
serv_uri = target_authenticated_google_app_engine_uri

serv_args = {}
serv_args['continue'] = serv_uri
serv_args['auth']     = authtoken

full_serv_uri = "http://"+txtio_domain+"/_ah/login?%s" % (urllib.urlencode(serv_args))

serv_req = urllib2.Request(full_serv_uri)
serv_resp = urllib2.urlopen(serv_req)
serv_resp_body = serv_resp.read()

# serv_resp_body should contain the contents of the 
#  target_authenticated_google_app_engine_uri page - as we will have been 
#  redirected to that page automatically 
#
# to prove this, I'm just gonna print it out
#print serv_resp_body


# Extracting verify code
matcher = re.search( ur"name=\"verify\" value=\"([a-z0-9]+)\"", serv_resp_body )
verify_code = matcher.group(1)

print "Got verification code: " + verify_code
print

# Get user message
control = True
user_input = []
while control:
    if not user_input:
        entry = raw_input("Enter text, '.' on its own line to quit: \n")
        user_input.append(entry)
    else:
        entry = raw_input("")
        user_input.append(entry)
        if entry == ".":
            del user_input[-1]
            control = False
user_input = '\n'.join(user_input)

print

# Posting message
txtio_post_uri = "http://"+txtio_domain+"/txtcreate.do"
txtio_post_data = urllib.urlencode({ "action": "- post -",
                                  "next":   user_txtio_account+"/m",
                                  "txt":    user_input,
                                  "verify": verify_code })
txtio_post_req = urllib2.Request(txtio_post_uri, data=txtio_post_data)
txtio_post_resp = urllib2.urlopen(txtio_post_req)
txtio_post_resp_body = txtio_post_resp.read()

#print txtio_post_resp_body


# Extracting post uri
matcher = re.search( ur"<div style=\"border:none;\"><a href=\"/([a-z0-9-]+)\" />", serv_resp_body )
prev_post_uri = matcher.group(1)

matcher = re.search( ur"<div style=\"border:none;\"><a href=\"/([a-z0-9-]+)\" />", txtio_post_resp_body )
post_uri = matcher.group(1)

if post_uri == prev_post_uri:
	print "!!! Not posted !!!"
	print "Check: " + "http://"+txtio_domain+"/"+user_txtio_account
else:
	print "Posted: " + "http://"+txtio_domain+"/"+post_uri

