import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurações do e-mail
seu_email = "codigosecreto2025@gmail.com"
senha = "bpij xclh mwqr sofe"
destinatario = "laladg18@gmail.com"


# Criando a mensagem
msg = MIMEMultipart()
msg["From"] = seu_email
msg["To"] = destinatario
msg["Subject"] = "Fim do Job"

corpo = "Script script.sh concluido fim do Job!"
msg.attach(MIMEText(corpo, "plain"))


# Simulação de envio (print antes de enviar)
print("De:", seu_email)
print("Para:", destinatario)
print("Assunto:", msg["Subject"])
print("Corpo:\n", corpo)

# Descomente a linha abaixo para enviar o e-mail após testar
try:
     servidor = smtplib.SMTP("smtp.gmail.com", 587)
     servidor.starttls()
     servidor.login(seu_email, senha)
     servidor.sendmail(seu_email, destinatario, msg.as_string())
     servidor.quit()
     print("E-mail enviado com sucesso!")
except Exception as e:
     print(f"Erro ao enviar e-mail: {e}")
