import smtplib
from email.message import EmailMessage


class Message():
    def __init__(self):
        self.sender='jashansinghmalhi129304@outlook.com'
        self.password='JashanMalhi123'
        #self.reciver=''
        self.subject ='jj'
        self.body ='jjj'
        self.newMessage = EmailMessage()
        #self.newMessage['Subject'] = self.subject #Defining email subject
        self.newMessage['From'] = self.sender  #Defining sender email
        #self.newMessage['To'] = self.reciver  #Defining reciever email
        #self.newMessage.set_content(self.body) #Defining email body

class Email():
    def __init__(self):
        pass
    def sendEmail(self,message):
        with smtplib.SMTP(host='smtp-mail.outlook.com', port=587) as self.smtp:
            self.smtp.ehlo()     #Identify ourselves with the mail server we are using.
            self.smtp.starttls() #Encrypt our connection
            self.smtp.ehlo()
            self.smtp.login(message.sender, message.password)
            self.smtp.send_message(message.newMessage)
        print('email sent')