from hashlib import sha256

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status


class OK(object):
    pass


def make_check_authorization_header(adl_key_hashed: str, x_adl_key_header: APIKeyHeader):
    def check_authorization_header(x_adl_key: str = Depends(x_adl_key_header)) -> OK:

        if adl_key_hashed:
            b_x_adl_key = str.encode(x_adl_key)
            s256 = sha256()
            s256.update(b_x_adl_key)
            if s256.hexdigest() == adl_key_hashed:
                return OK()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API Key",
                )
        else:
            return OK()
    return check_authorization_header
