def test_import_app():
    import app
    assert hasattr(app, 'app')
