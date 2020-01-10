import smtplib

def sendMail(subject, body, mailconfigfile):
       
    try:
        f = open(mailconfigfile, "r")
        mail_user = f.readline()
        mail_password = f.readline()
    except:
        return {'result': False, 'message': 'Keine Mail-Konfiguration gefunden unter ' + str(mailconfigfile)} 
    
    sent_from = mail_user
    to = mail_user
    server = 'smtp.mail.yahoo.com'       
    email_text = '\ \nFrom: %s \nTo: %s \nSubject: %s\n\n%s' % (sent_from, to, subject, body)
    
    
    try:
        server = smtplib.SMTP_SSL(server, 465)
        server.ehlo()
        server.login(mail_user, mail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
    
        return {'result': True, 'message': 'Mail versendet'}
        
    except Exception as e:
        
        print(e)
        return {'result': False, 'message': 'Mail konnte nicht versendet werden. Grund: ' + str(e)}

if __name__ == "__main__":
    a=sendMail("myButlerTest","sent by kodi", 'mail.jpg')
    print(a)