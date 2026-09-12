"""Task model and interactive state for the demo app.

This is the proof that the framework loop works end to end on Railway:
browser event -> Reflex state handler -> SQLModel/SQLite write -> UI refresh.
Swap this module out for your own app (see README: "Replace the demo app").
"""

import reflex as rx
import sqlmodel
from sqlmodel import select


class Task(sqlmodel.SQLModel, table=True):
    """A single task, persisted in the container's SQLite database.

    (rx.Model is deprecated since 0.9.2; SQLModel is used directly.)
    """

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    title: str
    done: bool = False


class TaskState(rx.State):
    """Holds the task list and all event handlers that touch the database."""

    tasks: list[Task] = []
    new_title: str = ""

    def _refresh(self):
        with rx.session() as session:
            self.tasks = session.exec(select(Task).order_by(Task.id)).all()

    @rx.event
    def on_load(self):
        self._refresh()

    @rx.event
    def set_new_title(self, value: str):
        self.new_title = value

    @rx.event
    def handle_key(self, key: str):
        if key == "Enter":
            self.add_task()

    @rx.event
    def add_task(self):
        title = self.new_title.strip()
        if not title:
            return
        with rx.session() as session:
            session.add(Task(title=title))
            session.commit()
        self.new_title = ""
        self._refresh()

    @rx.event
    def toggle_task(self, task_id: int):
        with rx.session() as session:
            task = session.get(Task, task_id)
            if task:
                task.done = not task.done
                session.add(task)
                session.commit()
        self._refresh()

    @rx.event
    def delete_task(self, task_id: int):
        with rx.session() as session:
            task = session.get(Task, task_id)
            if task:
                session.delete(task)
                session.commit()
        self._refresh()


def _task_item(task: Task) -> rx.Component:
    return rx.hstack(
        rx.cond(
            task.done,
            rx.icon("circle-check", color="green"),
            rx.icon("circle", color="gray"),
        ),
        rx.text(task.title, decoration=rx.cond(task.done, "line-through", "none")),
        rx.spacer(),
        rx.button(
            "Toggle",
            on_click=lambda: TaskState.toggle_task(task.id),
            size="1",
            variant="soft",
        ),
        rx.button(
            "Delete",
            on_click=lambda: TaskState.delete_task(task.id),
            size="1",
            variant="soft",
            color_scheme="red",
        ),
        width="100%",
        padding="0.5em",
        border="1px solid #eee",
        border_radius="6px",
    )


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Reflex on Railway", size="6"),
            rx.text(
                "Full-stack web app in pure Python — events round-trip to the "
                "backend and persist to SQLite.",
                color="gray",
                text_align="center",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Add a task…",
                    value=TaskState.new_title,
                    on_change=TaskState.set_new_title,
                    on_key_down=TaskState.handle_key,
                    width="100%",
                ),
                rx.button("Add", on_click=TaskState.add_task()),
                width="100%",
            ),
            rx.foreach(TaskState.tasks, _task_item),
            rx.text(
                TaskState.tasks.length(), " task(s)",
                color="gray",
                size="1",
            ),
            spacing="4",
            width="min(480px, 90vw)",
            padding_y="2em",
        ),
        height="100vh",
    )
