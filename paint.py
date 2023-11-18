import flet as ft
import flet.canvas as cv
import asyncio
import random

COLORS = ['#33ff0000', '#3300ff00', '#330000ff']

def random_grid_position(side, max_val):
    """Generate a random position that aligns with the grid size."""
    return random.randint(0, max_val // side - 1) * side

interval = 0.05

GRID_WIDTH_MAX = 200
GRID_WIDTH_MIN = 10
GRID_HEIGHT_MIN = 10
GRID_HEIGHT_MAX = 100
grid_width = GRID_WIDTH_MAX
grid_height = GRID_HEIGHT_MAX

async def add_rectangle_every_interval(page: ft.Page, cp: cv.Canvas):
    """Add a rectangle to the canvas at a fixed interval."""
    global grid_width, grid_height
    global interval
    width = 600
    height = 400

    while True:
        cell_width_side = width/grid_width
        cell_height_side = height/grid_height

        i = random_grid_position(cell_width_side, width)
        j = random_grid_position(cell_height_side, height)

        if i < width and j < height:
            rect = cv.Rect(i, j, cell_width_side, cell_height_side, 0, ft.Paint(color=random.choice(COLORS)))
            cp.shapes.append(rect)

            await page.update_async()
            await asyncio.sleep(interval)
        else:
            break  # Once we fill the canvas, we stop adding rectangles

drawing_task = None

async def main(page: ft.Page):
    page.title = "Routes Example"
    page.bgcolor = ft.colors.WHITE
    cp = cv.Canvas(
        [],  # Start with an empty list of shapes
        width=600,
        height=400
    )

    t = ft.Text()
    def slider_changed(e):
        global interval
        t.value = f"Slider changed to {e.control.value}"
        interval = e.control.value
        page.update()

    def route_change(route):
        global drawing_task
        if page.route == "/simulator":
            # Start drawing only when on the /simulator page
            if drawing_task is None or drawing_task.done():
                cp.shapes.clear()
                drawing_task = asyncio.create_task(add_rectangle_every_interval(page, cp))
        else:
            # Cancel the drawing task if we navigate away from the /simulator page
            if drawing_task and not drawing_task.done():
                drawing_task.cancel()
                drawing_task = None

        page.views.clear()

        page.update()

        height_error_text = ft.Text("Invalid input for Grid Height!", visible=False, color=ft.colors.RED)
        width_error_text = ft.Text("Invalid input for Grid Width!", visible=False, color=ft.colors.RED)
        tf_grid_height = ft.TextField(
                    label="Grid Height",
                    value=GRID_HEIGHT_MAX,
                    max_length=len(str(GRID_HEIGHT_MAX)),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    error_text=None,
                    on_change=lambda e: handle_change(e, height_error_text),
                )
        tf_grid_width = ft.TextField(
                    label="Grid Width",
                    value=GRID_WIDTH_MAX,
                    max_length=len(str(GRID_WIDTH_MAX)),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    error_text=None,
                    on_change=lambda e: handle_change(e, width_error_text),
                )

        def handle_change(e, error_text_control):
            global grid_width, grid_height
            ranges = {height_error_text: {'min': GRID_HEIGHT_MIN, 'max': GRID_HEIGHT_MAX},
                      width_error_text: {'min': GRID_WIDTH_MIN, 'max': GRID_WIDTH_MAX}}
            try:
                value = int(e.control.value)
                if not (ranges[error_text_control]['min'] <= value <= ranges[error_text_control]['max']):
                    error_text_control.visible = True
                else:
                    error_text_control.visible = False
                    if error_text_control == height_error_text:
                        grid_height = int(tf_grid_height.value)
                    else:
                        grid_width = int(tf_grid_width.value)
            except ValueError:
                error_text_control.visible = True

        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("RandomPainter.xyz"), bgcolor=ft.colors.SURFACE_VARIANT),
                    height_error_text,
                    tf_grid_height,
                    width_error_text,
                    tf_grid_width,
                    ft.ElevatedButton("Visit Simulator", on_click=lambda _: page.go("/simulator")),

                ],
            )
        )
        if page.route == "/simulator":
            page.views.append(
                ft.View(
                    "/simulator",
                    [
                        ft.AppBar(title=ft.Text("Simulator"), bgcolor=ft.colors.SURFACE_VARIANT),
                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                        ft.Text("Slider with 'on_change' event:"),
                        ft.Slider(min=0.001, max=2, label="{value}%", on_change=slider_changed),
                        cp
                    ],
                    bgcolor=ft.colors.WHITE
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
