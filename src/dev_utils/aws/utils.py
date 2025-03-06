import logging
import boto3

LOGGER = logging.getLogger(__name__)

class MFABoto:
    
    def __init__(self, access_key_id=None, secret_access_key=None, mfa_code=None):
        LOGGER.info("Starting up!")
        
        self._mfa_serial = None
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._session_token = None
        
        if mfa_code:
            LOGGER.info("Instantiateed with an MFA code!")
            self.authenticate(mfa_code)
        LOGGER.info("Successfully instantiated an MFABoto object")

    def client(self, client_type):
        LOGGER.info("Getting client type %s", client_type)
        if self._session_token is None:
            raise ValueError("Please authenticate before you call a client!")
        authed_client = boto3.client(
            client_type,
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
            aws_session_token=self._session_token
        )
        return authed_client
        
    @property
    def mfa_serial(self):
        LOGGER.debug("Retrieving MFA serial for user.")
        if self._mfa_serial:
            return self._mfa_serial
        
        iam_client = boto3.client('iam')

        mfa_device_info = iam_client.list_mfa_devices()
        mfa_devices = mfa_device_info['MFADevices']

        for device in mfa_devices:
            if mfa_device_arn:= device.get('SerialNumber'):
                if 'mfa' not in mfa_device_arn:
                    continue
                self._mfa_serial = mfa_device_arn
        LOGGER.debug("Retrieved mfa %s", self._mfa_serial)
        return self._mfa_serial
        
    def authenticate(self, mfa_code):
        LOGGER.info("Authenticating with MFA code %s against device %s", mfa_code, self.mfa_serial)
        sts_client = boto3.client('sts')
        response = sts_client.get_session_token(
            SerialNumber=self.mfa_serial,
            TokenCode=mfa_code
        )

        self._access_key_id = response['Credentials']['AccessKeyId']
        self._secret_access_key = response['Credentials']['SecretAccessKey']
        self._session_token = response['Credentials']['SessionToken']
        LOGGER.info("New session token set.")
