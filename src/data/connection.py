"""Cliente Supabase singleton."""

import os
from dotenv import load_dotenv
from supabase import Client, create_client
import streamlit as st

load_dotenv()


@st.cache_resource(show_spinner=False)
def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL e SUPABASE_ANON_KEY devem estar definidos no .env")
    return create_client(url, key)
