from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from hashlib import sha256
import os


class OK(object):
    pass


X_ADL_KEY = APIKeyHeader(name='X-ADL-Key')
ADL_KEY = 'ADL_KEY'

adl_key = os.environ.get(ADL_KEY)
if not adl_key:
    print("WARNING:  Missing {} environment variable. API key protection is disabled".format(ADL_KEY))


def check_authorization_header(x_adl_key: str = Depends(X_ADL_KEY)) -> OK:

    if adl_key:
        b_x_adl_key = str.encode(x_adl_key)
        s256 = sha256()
        s256.update(b_x_adl_key)
        if s256.hexdigest() == adl_key:
            return OK()
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
            )
    else:
        return OK()
