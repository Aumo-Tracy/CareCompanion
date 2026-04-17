import os
from utils.demo import DEMO_MODE

if DEMO_MODE:
    class _FakeTable:
        def insert(self, data):
            return self
        def select(self, *args):
            return self
        def eq(self, *args):
            return self
        def order(self, *args, **kwargs):
            return self
        def limit(self, *args):
            return self
        def execute(self):
            return type("Result", (), {"data": [], "error": None})()

    class _FakeSupabase:
        def table(self, name):
            return _FakeTable()

    supabase = _FakeSupabase()
    print("[DEMO] Using fake Supabase client — no real DB calls")

else:
    from supabase import create_client
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY")
    )
    print("[LIVE] Connected to real Supabase")