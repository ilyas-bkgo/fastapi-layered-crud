import bcrypt


def hash_password(password: str) -> str:

    # 1. Convert the plain text string to bytes
    pwd_bytes = password.encode("utf-8")

    # 2. generate a random salt and mix it with the pws bytes
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt)

    # 3. decode the bytes string back into python string for sqlite storage
    return hashed_pwd.decode("utf-8")
