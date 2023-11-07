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
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Flet app"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.ElevatedButton("Visit Store", on_click=lambda _: page.go("/store")),
                ],
            )
        )
        if page.route == "/store":
            page.views.append(
                ft.View(
                    "/store",
                    [
                        ft.AppBar(title=ft.Text("Store"), bgcolor=ft.colors.SURFACE_VARIANT),
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
