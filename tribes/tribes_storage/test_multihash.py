from tribes_storage.lib import actions

def test_convert_to_multihash():
    multihash = actions.convert_to_multihash('http://localhost:5001')
    assert multihash == '/dns/localhost/tcp/5001/http'