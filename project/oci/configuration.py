from decouple import config
from oci.config import validate_config

oci_config = {
    'user': config('USER_OCID'),
    'key_file': config('KEY_FILE'),
    'fingerprint': config('FINGERPRINT'),
    'tenancy': config('TENANCY'),
    'region': config('REGION'),
    'pass_phrase': config('PASS_PHRASE')
}

validate_config(oci_config)