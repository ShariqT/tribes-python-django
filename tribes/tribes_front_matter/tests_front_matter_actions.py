from tribes_front_matter.lib import actions

def test_read_jekyll_config():
    content = actions.read_jekyll_config()
    assert '# Welcome to Jekyll!' in content
    assert '# Build settings' in content
    assert 'theme: minima' in content

def test_save_jekyll_config():
    new_content = actions.read_jekyll_config()
    new_content += '# Welcome to SAVED JEKYLL'
    actions.save_jekyll_config(new_content)
    txt = actions.read_jekyll_config()
    assert '# Welcome to SAVED JEKYLL' in txt

