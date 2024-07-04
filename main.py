from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing_extensions import Annotated
import requests
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Criptografia de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração do token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

User = {
    "user": {
        "username": "user",
        "password": "$2b$12$jDODvqMQ4R.yhb4yI7nr7u/FU.BHn3HhRQ3dFxzbOFeQf8wTR81UG",
    }
}

def authenticate_user(username: str, password: str):
    user = User.get(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return False
    return user


class UserList(BaseModel):                                                                       # Definindo listas de usuários
    users: List[str]

@app.post("/reset-password")
async def reset_password(lista: UserList, user = Depends(oauth2_scheme)):                         # variável referenciada o modelo de lista da classe acima

    valid_users = []                                                                              # Armazena usuarios  vlaidos
    invalid_users = []                                                                            # Armazena usuarios não vlaidos
    url = "https://hml-link-de-exemplo/forgot"                       # Endpoint

    for user in lista.users:
        Try_valid = False
        cont = 0
        user_no_space = str.strip(user)                             # Remove os espaços no incio e no fim. Será usado apenas ele na condição
        while not Try_valid:
            print(f"lista.users: {user_no_space}")                   # Debug do nome de cada interação
            response = requests.put(url, user_no_space)
            print(f"Strip User: {user_no_space}########")            # PUT que envia o link e nome por nome
            print(response)                                          # Depuração do response
            if response.status_code == 200:                          # Checar se o statos do envio (endpoint + usuario)
                valid_users.append(user_no_space)                    # Adiciona a lista de usuarios válidos
                Try_valid = True
            else:                                                    # Verifica o status caso negativo
                cont += 1
                print(f"Try: {cont}.")
                if cont == 3:                                        # Checa se o já foi tentado 3 vezes antes de encerrar as tentativas
                    invalid_users.append(user_no_space)
                    break

    print(f"\nUsuarios cadastrados {valid_users}")
    print(f"Usuarios NAO cadastrados {invalid_users}")
    return {"success": valid_users, "error": invalid_users}      # Retorna a lista dos validos e inválidos


@app.post("/token", include_in_schema=False)
async def Verify_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}
