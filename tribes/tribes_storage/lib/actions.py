from urllib.parse import urlparse
from tribes_django import settings
import ipfshttpclient

def convert_to_multihash(url=None):
    if url is None:
        url = settings.IPFS_URL
    result = urlparse(url)
    return '/dns/{}/tcp/{}/{}'.format(result.hostname, result.port, result.scheme)


def view_mfs_directory(path):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.files.ls(path)

def view_mfs_file_info(filepath):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.files.stat(filepath)

def create_mfs_directory(path):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.files.mkdir(path)

def create_mfs_file(filepath, file_data, create=True, truncate=True):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.files.write(filepath, file_data, create=create, truncate=truncate)

def create_mfs_move_file(source, dest):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.files.mv(source, dest)

def copy_mfs_file(source, dest):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.files.cp(source, dest)

def pin_new_file(multihash):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.pin.add(multihash)

def remove_pin_from_file(multihash):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.pin.rm(multihash)


def update_pin(starting_multihash, ending_multihash):
    with ipfshttpclient.connect(convert_to_multihash()) as client:
        return client.pin.update(starting_multihash, ending_multihash)