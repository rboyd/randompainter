import flet as ft
import flet.canvas as cv
import asyncio
import random

COLORS = ['#33ff0000', '#3300ff00', '#330000ff']

def random_grid_position(side, max_val):
    """Generate a random position that aligns with the grid size."""
    return random.randint(0, max_val // side - 1) * side

interval = 0.05

async def add_rectangle_every_interval(page: ft.Page, cp: cv.Canvas):
    """Add a rectangle to the canvas at a fixed interval."""
    global interval
    side = 20
    width = 600
    height = 400
    
    while True:
        i = random_grid_position(side, width)
        j = random_grid_position(side, height)

        if i < width and j < height:
            rect = cv.Rect(i, j, side, side, 0, ft.Paint(color=random.choice(COLORS)))
            cp.shapes.append(rect)
            await page.update_async()
            await asyncio.sleep(interval)
        else:
            break  # Once we fill the canvas, we stop adding rectangles

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
        page.views.clear()

        page.update()

        GRID_WIDTH_MAX = 200
        GRID_WIDTH_MIN = 10
        GRID_HEIGHT_MIN = 10
        GRID_HEIGHT_MAX = 100

        height_error_text = ft.Text("Invalid input for Grid Height!", visible=False, color=ft.colors.RED)
        width_error_text = ft.Text("Invalid input for Grid Width!", visible=False, color=ft.colors.RED)

        def handle_change(e, error_text_control):
            ranges = {height_error_text: {'min': GRID_HEIGHT_MIN, 'max': GRID_HEIGHT_MAX},
                      width_error_text: {'min': GRID_WIDTH_MIN, 'max': GRID_WIDTH_MAX}}
            try:
                value = int(e.control.value)
                if not (ranges[error_text_control]['min'] <= value <= ranges[error_text_control]['max']):
                    error_text_control.visible = True
                else:
                    error_text_control.visible = False
            except ValueError:
                error_text_control.visible = True

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

    #await page.add_async(cp)
    await add_rectangle_every_interval(page, cp)  # Add a rectangle every interval second

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
