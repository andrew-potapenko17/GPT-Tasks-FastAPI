from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = input("[+] Plain Passowrd: ")

def get_password_hash(password : str):
    return pwd_context.hash(password)

print(f"[+] Password Hash >> {get_password_hash(password)}")