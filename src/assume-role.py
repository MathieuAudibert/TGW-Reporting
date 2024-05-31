#!/usr/bin/env python 

import json
import logging
import click
import __pycache__.credentials

logger = logging.getLogger(__name__)

@click.command()
@click.argument("filename", nargs=1, required=True)

def decrypt_secrets(filename: str) -> dict:
    result = dict(AccessKeyId="", SecretAccessKey="")
    try:
        cred = credentials.get_credentials(filename)
        result["AccessKeyId"] = cred["key"]
        result["SecretAccessKey"] = cred["value"]
    
    except Exception as e:
        logger.exception(e)
        
    finally:
        print(json.dumps(result))

if __name__ == "__main__":
    decrypt_secrets()