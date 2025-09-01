from schema.auth_input 


def test_sign_up_input_schema():
    sign_up_input = SignUpInputSchema(email="test@test.com", password="password")
    assert sign_up_input.email == "test@test.com"
    assert sign_up_input.password == "password"

def test_sign_in_input_schema():
    sign_in_input = SignInInputSchema(email="test@test.com", password="password")
    assert sign_in_input.email == "test@test.com"
    assert sign_in_input.password == "password"fa