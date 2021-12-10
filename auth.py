from authlib.integrations.starlette_client import OAuth
from settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

oauth = OAuth()

# Register Google OAuth2 client
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri=GOOGLE_REDIRECT_URI,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    scope="openid email profile",
)
