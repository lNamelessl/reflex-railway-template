"""Reflex app entrypoint (reflex_railway.reflex_railway). Pages are registered here."""

import reflex as rx

from reflex_railway.tasks import TaskState, index

app = rx.App()
app.add_page(index, route="/", on_load=TaskState.on_load)
