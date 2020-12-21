from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT
from jwcrypto.jwe import JWE
from jwcrypto.common import json_encode, json_decode


def encrypt_raw_event(evt, public_key, is_dict=False):
    payload = evt.to_jsonld()
    if is_dict is True:
        if type(public_key) is str:

            public_key = JWK.from_json(json_encode(eval(public_key)))
        else:
            public_key = JWK.from_json(json_encode(public_key))
    protected_header = {
        "alg": "RSA-OAEP-256",
        "enc": "A256CBC-HS512",
        "typ": "JWE",
        "kid": public_key.thumbprint(),
    }
    data = JWE(
        payload.encode('utf-8'),
        recipient=public_key,
        protected=protected_header
    )

    return data.serialize()