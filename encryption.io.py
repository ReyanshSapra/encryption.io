import streamlit as st
from minio import Minio
from minio.error import S3Error
from cryptography.fernet import Fernet
import string
import random
import io
from mailjet_rest import Client
import os

key = Fernet.generate_key()
fernet = Fernet(key)

client = Minio(
    endpoint="play.min.io",
    access_key="Q3AM3UQ867SPQQA43P2F",
    secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
    secure=True
)

if "bucketName" not in st.session_state:
    st.session_state.bucketName = "encryption-server"

if "mainEncryptButton" not in st.session_state:
    st.session_state.mainEncryptButton = None

if "currentScreen" not in st.session_state:
    st.session_state.currentScreen = "home"

if "mainRecieveButton" not in st.session_state:
    st.session_state.mainRecieveButton = None

if "encryptionMessage" not in st.session_state:
    st.session_state.encryptionMessage = None

if "encryptionEmail" not in st.session_state:
    st.session_state.encryptionEmail = None

if "encryptMessageConfirm" not in st.session_state:
    st.session_state.encryptMessageConfirm = None

if "code" not in st.session_state:
    st.session_state.code = None

if "mailjetApiKey" not in st.session_state:
    st.session_state.mailjetApiKey = "dc116c75f2d866b9fc613876c6b9c59c"   
    
if "mailjetApiSecret" not in st.session_state:
    st.session_state.mailjetApiSecret = "b5a310be3445395652cfc9ffb7a5c361"

if "decMessage" not in st.session_state:
    st.session_state.decMessage = None

hide_st_style = """
    <style>
        .stApp {background-color: #C5DFF8;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

MainHeading = """
    <h1 style='text-align: center; color: black;'>
        encryption
        <span style='color: #4A55A2; font-size: 1.3em'>
            .io
        </span>
        <hr style='padding:0; margin:0; width: 50%; left:25%; position:absolute; border: none; border-top: 2px solid black;'>
    </h1>"""
st.markdown(MainHeading, unsafe_allow_html=True)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.session_state.mainEncryptButton = st.button("Encrypt")
    if st.session_state.mainEncryptButton:
        st.session_state.currentScreen = "encrypt"
        st.experimental_rerun()

with col2:
    st.session_state.mainRecieveButton = st.button("Receive")
    if st.session_state.mainRecieveButton:
        st.session_state.currentScreen = "receive"
        st.experimental_rerun()

if st.session_state.currentScreen == "encrypt":
    st.session_state.encryptionMessage = st.text_input("Enter the message to encrypt")
    st.session_state.encryptionEmail = st.text_input("Enter your email address")
    encMessage = fernet.encrypt(st.session_state.encryptionMessage.encode())
    st.session_state.encryptMessageConfirm = st.button("Confirm Encryption")
    if st.session_state.encryptMessageConfirm:
        letters = string.ascii_uppercase
        st.session_state.code = ''.join(random.choices(letters, k=10))
        if client.bucket_exists(st.session_state.bucketName):
            client.put_object(st.session_state.bucketName, f"{st.session_state.code}/code", data=io.BytesIO(encMessage), length=len(encMessage))
            client.put_object(st.session_state.bucketName, f"{st.session_state.code}/key", data=io.BytesIO(key), length=len(key))
        st.session_state.currentScreen = "encryptConfirm"
        st.experimental_rerun()

if st.session_state.currentScreen == "encryptConfirm":
    st.subheader("Encryption Successful")
    

    mailjet = Client(auth=(st.session_state.mailjetApiKey, st.session_state.mailjetApiSecret), version='v3.1')


    data = {
        'Messages': [
            {
                "From": {
                    "Email": "encryption.io.server@gmail.com",
                    "Name": "encryption.io"
                },
                "To": [
                    {
                        "Email": st.session_state.encryptionEmail,
                    }
                ],
                "Subject": "Your encryption.io code",
                "TextPart": f"Your unique 10 letter code is: {st.session_state.code}.Please use this code to decrypt your message.",
            }
        ]
    }


    result = mailjet.send.create(data=data)


    if result.status_code == 200:
        st.subheader("Your code has been sent to your email. Please allow a few minutes for the email to arrive. It might be in your spam folder.")
    else:
        st.subheader(f"Failed to send email. Status code: {result.status_code}")
        print(result.json())

    if st.button("Home"):
        st.session_state.currentScreen = "home"
        st.experimental_rerun()



if st.session_state.currentScreen == "receive":
    st.session_state.encryptionMessage = st.text_input("Enter your code")
    st.session_state.encryptMessageConfirm = st.button("Confirm")
    if st.session_state.encryptMessageConfirm:
        if client.bucket_exists(st.session_state.bucketName):
            obj = client.get_object(st.session_state.bucketName, f"{st.session_state.encryptionMessage}/key")
            key = obj.read()
            fernet = Fernet(key)
            obj = client.get_object(st.session_state.bucketName, f"{st.session_state.encryptionMessage}/code")
            encMessage = obj.read()
            st.session_state.decMessage = fernet.decrypt(encMessage)
            st.session_state.currentScreen = "receiveConfirm"
            st.experimental_rerun()

if st.session_state.currentScreen == "receiveConfirm":
    st.subheader("Decryption Successful")
    st.subheader(st.session_state.decMessage.decode())