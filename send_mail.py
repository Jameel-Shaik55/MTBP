import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
def connect_smtp():
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('srinivasaraoch506@gmail.com','lraz tzfd mmad rmmu')
    return server
def sendmail(email,subject,body):
    try:
        server = connect_smtp()
        msg=MIMEMultipart()
        msg['From']='srinivasaraoch506@gmail.com'
        msg['To']=email
        msg['Subject']=subject
        msg.attach(MIMEText(body,'html'))
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print('Error in sendionmg mail',e)
        return False