"""Cliente Supabase singleton."""

import os
from dotenv import load_dotenv
from supabase import Client, create_client
import streamlit as st

load_dotenv()


def _get_secret(key: str) -> str | None:
    """Busca em st.secrets (Streamlit Cloud) primeiro, depois em env (.env local)."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key)


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client:
    url = _get_secret("SUPABASE_URL")
    key = _get_secret("SUPABASE_ANON_KEY") or _get_secret("SUPABASE_PUBLISHABLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL e SUPABASE_ANON_KEY devem estar definidos (.env local ou st.secrets na nuvem)")
    return create_client(url, key)
