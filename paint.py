import flet as ft
import flet.canvas as cv
import asyncio
import random
from color_picker import ColorPicker
from grid_model import GridModel, StoppingCondition
from chart import ScatterChart

def random_grid_position(side, max_val):
    """Generate a random position that aligns with the grid size."""
    return random.randint(0, max_val // side - 1) * side

interval = 0.05

GRID_WIDTH_MAX = 200
GRID_WIDTH_MIN = 10
GRID_HEIGHT_MIN = 10
GRID_HEIGHT_MAX = 100
grid_width = GRID_WIDTH_MIN
grid_height = GRID_HEIGHT_MIN

def check_dimensions():
    global grid_width, grid_height
    return (GRID_HEIGHT_MIN <= grid_height <= GRID_HEIGHT_MAX) and (GRID_WIDTH_MIN <= grid_width <= GRID_WIDTH_MAX)

stopping_labels = {StoppingCondition.ALL_FILLED: 'Canvas All Painted',
                   StoppingCondition.SECOND_DROP: 'Any Square Painted Twice'}

# Define a global variable to hold the selected stopping condition
selected_stopping_condition = StoppingCondition.ALL_FILLED

# Initialize the grid_model as None outside of the route_change function
grid_model = None

async def add_rectangle_every_interval(page: ft.Page, content_section: ft.Column, cp: cv.Canvas):
    """Add a rectangle to the canvas at a fixed interval."""
    global color_pickers
    global grid_width, grid_height
    global interval
    width = 600
    height = 400

    while True:
        cell_width_side = width/grid_width
        cell_height_side = height/grid_height

        i = random_grid_position(cell_width_side, width)
        j = random_grid_position(cell_height_side, height)

        color_idx = random.randint(0, NUM_COLORS-1)

        rect = cv.Rect(i, j, cell_width_side, cell_height_side, 0, ft.Paint(color=ft.colors.with_opacity(0.2, color_pickers[color_idx].icon_color)))
        cp.shapes.append(rect)

        # updage the GridModel
        x, y = int(i // cell_width_side), int(j // cell_height_side)
        stopping_condition = grid_model.paint(x, y, color_pickers[color_idx].icon_color)
        print(stopping_condition)
        if stopping_condition:
            # Break out of the loop if a stopping condition is met
            break

        await page.update_async()
        await asyncio.sleep(interval)

    # If the loop is broken, add a text field indicating the simulation is complete
    if stopping_condition:
        completion_text = f"The simulation is complete: {stopping_labels[selected_stopping_condition]}"
        content_section.controls.append(ft.Text(completion_text, color=ft.colors.BLACK))

        # Create the "Continue" button
        continue_button = ft.ElevatedButton(
            "Continue",
            on_click=lambda _: page.go("/experiment")  # Navigate to the "/experiment" route when clicked
        )
        # Add the "Continue" button to the page's controls
        content_section.controls.append(continue_button)

        await page.update_async()


drawing_task = None

def new_color_icon():
    async def open_color_picker(e):
        e.control.page.dialog = d
        d.open = True
        await e.control.page.update_async()

    color_picker = ColorPicker(color="#c8df6f", width=300)
    color_icon = ft.IconButton(icon=ft.icons.BRUSH, on_click=open_color_picker)

    async def change_color(e):
        global visit_simulator_button
        color_icon.icon_color = color_picker.color
        d.open = False
        visit_simulator_button.disabled = not (check_color_pickers() and check_dimensions())  # Update the button's disabled state
        await e.control.page.update_async()

    async def close_dialog(e):
        d.open = False
        await d.update_async()

    d = ft.AlertDialog(
        content=color_picker,
        actions=[
            ft.TextButton("OK", on_click=change_color),
            ft.TextButton("Cancel", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=change_color,
    )

    return color_icon

NUM_COLORS = 3
color_pickers = [new_color_icon() for _ in range(NUM_COLORS)]

def check_color_pickers():
    global color_pickers
    # Check if all color pickers have a color selected
    return all(color_picker.icon_color != None for color_picker in color_pickers)

visit_simulator_button = ft.ElevatedButton(
    "Visit Simulator",
    disabled=True  # Disable the button initially if not all colors are chosen
)


# Constants for experiment limits
MAX_VALUES = 5  # Justification: This limit ensures manageable computation time and clear visualization in graphs.
MIN_DIMENSION = 1
MAX_DIMENSION = 100
MIN_REPETITIONS = 1
MAX_REPETITIONS = 100


results = []
independent_variable = 'D'
# Function to create the form for the experiment page
def create_experiment_form(page):
    global results
    # Placeholder for dynamic controls
    dynamic_controls_view = ft.Column()
    repetitions_input = ft.TextField(label="Repetitions:", hint_text="Enter number of repetitions")
    x_dimension_input = ft.TextField(label="X:", hint_text="Enter X dimension")
    y_dimension_input = ft.TextField(label="Y:", hint_text="Enter Y dimension")
    # Define the event handler for the independent variable dropdown change
    def handle_independent_variable_change(e):
        # Clear existing dynamic controls
        dynamic_controls_view.controls.clear()

        # Add new controls based on the selected independent variable
        if e.control.value == "D":
            # If 'D' is selected, only ask for the number of repetitions
            dynamic_controls_view.controls.append(repetitions_input)
        elif e.control.value == "X":
            # If 'X' is selected, ask for Y dimension and number of repetitions
            dynamic_controls_view.controls.extend([y_dimension_input, repetitions_input])
        elif e.control.value == "R":
            # If 'R' is selected, ask for both X and Y dimensions
            dynamic_controls_view.controls.extend([x_dimension_input, y_dimension_input])
        page.update()

    def handle_values_input_change(e):
        # Logic to validate and handle the input values
        pass
    # Create controls for selecting the independent variable
    independent_variable_label = ft.Text("Select Independent Variable:")
    independent_variable_dropdown = ft.Dropdown(
        label="Independent Variable",
        options=[ft.dropdown.Option("D"),
                 ft.dropdown.Option("X"),
                 ft.dropdown.Option("R")],
        on_change=handle_independent_variable_change
    )

    # Create controls for inputting values
    values_label = ft.Text("Enter values for the Independent Variable (comma-separated):")
    values_input = ft.TextField(
        label="Values",
        hint_text="e.g., 2, 4, 8, 16",
        on_change=handle_values_input_change
    )

    async def run_simulations(e):
        global results, independent_variable
        values = list(map(int, values_input.value.split(',')))
        total_simulations = 0
        independent_variable = independent_variable_dropdown.value
        color1, color2, color3 = [color_pickers[color_idx].icon_color for color_idx in range(3)]
        simulations_run = 0
        results = []
        if independent_variable == "D":
            repetitions = int(repetitions_input.value)
            total_simulations = len(values) * repetitions
            for x in values:
                for _ in range(repetitions):
                    result = await PAINT_ONCE(x, x, color1, color2, color3, selected_stopping_condition)
                    simulations_run += 1
                    progress_indicator.value = simulations_run / total_simulations
                    await progress_indicator.update_async()
                    results.append(result)
        elif independent_variable == "X":
            y_dimension = int(y_dimension_input.value)
            repetitions = int(repetitions_input.value)
            total_simulations = len(values) * repetitions
            for x in values:
                for _ in range(repetitions):
                    result = await PAINT_ONCE(x, y_dimension, color1, color2, color3, selected_stopping_condition)
                    simulations_run += 1
                    progress_indicator.value = simulations_run / total_simulations
                    await progress_indicator.update_async()
                    results.append(result)
        elif independent_variable == "R":
            x_dimension = int(x_dimension_input.value)
            y_dimension = int(y_dimension_input.value)
            for r in values:
                total_simulations += r
                for _ in range(r):
                    result = await PAINT_ONCE(x_dimension, y_dimension, color1, color2, color3, selected_stopping_condition)
                    simulations_run += 1
                    progress_indicator.value = simulations_run / total_simulations
                    await progress_indicator.update_async()
                    results.append(result)

        page.go("/results")


    continue_button = ft.ElevatedButton("Continue", on_click=run_simulations)
    progress_indicator = ft.ProgressBar(value=0)

    async def PAINT_ONCE(x, y, c1, c2, c3, s):
        # Instantiate a new GridModel with the given dimensions and stopping condition
        grid_model = GridModel(x, y, s)

        # Continue painting until the stopping condition is met
        while True:
            # Generate random positions for the raindrop
            i = random.randint(0, x - 1)
            j = random.randint(0, y - 1)

            # Randomly choose one of the three colors
            color = random.choice([c1, c2, c3])

            # Paint the grid cell and check the result
            result = grid_model.paint(i, j, color)

            # If the stopping condition is met, return the result
            if result:
                return result

            # Sleep briefly to simulate time passing (adjust as needed)
            await asyncio.sleep(0.01)

    return ft.Column(
                    [
                        independent_variable_label,
                        independent_variable_dropdown,
                        values_label,
                        values_input,
                        dynamic_controls_view,
                        continue_button,
                        progress_indicator
                    ],
                    alignment=ft.MainAxisAlignment.START, expand=8
                )

selected_graph_vars = []
def create_results_page(page: ft.Page):
    global results
    A1_color, A2_color, A3_color = [color_pickers[color_idx].icon_color for color_idx in range(3)]
    rows = []
    columns=[
                ft.DataColumn(ft.Text("X"), numeric=True),
                ft.DataColumn(ft.Text("Y"), numeric=True),
                ft.DataColumn(ft.Text("A"), numeric=True),
                ft.DataColumn(ft.Text("A1"), numeric=True),
                ft.DataColumn(ft.Text("A2"), numeric=True),
                ft.DataColumn(ft.Text("A3"), numeric=True),
                ft.DataColumn(ft.Text("B"), numeric=True),
                ft.DataColumn(ft.Text("C"), numeric=True),
            ]

    for result in results:
        result['A1'] = result['drops_by_color'].get(A1_color, 0)
        result['A2'] = result['drops_by_color'].get(A2_color, 0)
        result['A3'] = result['drops_by_color'].get(A3_color, 0)
        rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(result['X']))),
            ft.DataCell(ft.Text(str(result['Y']))),
            ft.DataCell(ft.Text(str(result['A']))),
            ft.DataCell(ft.Text(str(result['A1']))),
            ft.DataCell(ft.Text(str(result['A2']))),
            ft.DataCell(ft.Text(str(result['A3']))),
            ft.DataCell(ft.Text(str(result['B']))),
            ft.DataCell(ft.Text(f"{result['C']:.2f}"))  # Format to 2 decimal places
        ]))
    data_table = ft.DataTable(
            columns=columns,
            rows=rows, expand=True
        )

    # Function to handle button toggle
    def toggle_button(e):
        global selected_graph_vars
        if e.control.text in selected_graph_vars:
            selected_graph_vars.remove(e.control.text)
            e.control.bgcolor = ft.colors.BLACK  # Set to default color when unselected
        else:
            if len(selected_graph_vars) >= 2:
                # Unselect the first selected button
                first_selected = selected_graph_vars.pop(0)
                # Find the button control and reset its bgcolor
                for control in button_row.controls:
                    if control.text == first_selected:
                        control.bgcolor = ft.colors.BLACK
                        break
            selected_graph_vars.append(e.control.text)
            e.control.bgcolor = ft.colors.BLUE  # Set to selected color
        continue_button.visible = len(selected_graph_vars) > 0
        page.update()

    # Create buttons for A, A1, A2, A3, B, and C
    button_labels = ['A', 'A1', 'A2', 'A3', 'B', 'C']
    button_row = ft.Row(
        controls=[
            ft.ElevatedButton(text=label, on_click=toggle_button) for label in button_labels],
        alignment=ft.MainAxisAlignment.START
    )

    # Create the "Continue" button
    continue_button = ft.ElevatedButton(
        "Continue",
        on_click=lambda _: page.go("/graph"),
        visible=False  # Initially hidden until a button is toggled on
    )
    return ft.Column(
        [
            button_row,
            continue_button,
            data_table
        ],
        alignment=ft.MainAxisAlignment.START, expand=8, height=800, scroll=ft.ScrollMode.AUTO
    )
    
def create_graph_page():
    global results, selected_graph_vars

    if not selected_graph_vars:
        return ft.Column([ft.Text("Please select at least one variable to plot.")])

    # 'X' is used for the x-axis
    x_var = 'X'
    # The selected variables are used for the y-axis
    y_vars = selected_graph_vars

    scatter_chart = ScatterChart(data=results, x_var=x_var, y_vars=y_vars)

    return ft.Column(
        [
            scatter_chart
        ],
        alignment=ft.MainAxisAlignment.START, expand=8
    )

async def main(page: ft.Page):
    global color_pickers, results
    visit_simulator_button.on_click = lambda _: page.go("/simulator")
    page.title = "RandomPainter.xyz"
    page.bgcolor = ft.colors.WHITE
    cp = cv.Canvas(
        [],  # Start with an empty list of shapes
        width=600,
        height=400
    )


    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        # extended=True,
        min_width=30,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.HOME, label="Home"),
            ft.NavigationRailDestination(icon=ft.icons.GAMEPAD, label="Simulator"),
            ft.NavigationRailDestination(icon=ft.icons.SCIENCE_ROUNDED, label="Experiment"),
            # Do not add a destination for "/results" as it should not be directly navigable
        ],
        on_change=lambda e: handle_navigation(e, page),
        height=600,
        expand=2
    )

    # Define the event handler for the NavigationRail
    def handle_navigation(event, page):
        # Map the index to routes
        index_to_route = {
            0: "/",
            1: "/simulator",
            2: "/experiment",
        }
        # Navigate to the selected page
        selected_route = index_to_route.get(event.control.selected_index)
        if selected_route:
            page.go(selected_route)






    t = ft.Text()
    def slider_changed(e):
        global interval
        t.value = f"Slider changed to {e.control.value}"
        interval = e.control.value
        page.update()

    def route_change(route):
        global drawing_task, grid_model, selected_stopping_condition
#        page.views.insert(0, navigation_rail)

        if page.route == "/simulator":
            content_section = ft.Column(
                    [
#                        ft.AppBar(title=ft.Text("Simulator"), bgcolor=ft.colors.SURFACE_VARIANT),
#                        ft.ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                        ft.Text("Painting Speed:"),
                        ft.Slider(min=0.001, max=2, label="{value}%", on_change=slider_changed),
                        cp
                    ],
                    alignment=ft.MainAxisAlignment.START, expand=8
                )            # Initialize the GridModel when navigating to the simulator
            grid_model = GridModel(grid_width, grid_height, selected_stopping_condition)  # or StoppingCondition.SECOND_DROP based on your logic

            # Start drawing only when on the /simulator page
            if drawing_task is None or drawing_task.done():
                cp.shapes.clear()
                drawing_task = asyncio.create_task(add_rectangle_every_interval(page, content_section, cp))
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
                    value=GRID_HEIGHT_MIN,
                    max_length=len(str(GRID_HEIGHT_MAX)),
                    keyboard_type=ft.KeyboardType.NUMBER,
                    error_text=None,
                    on_change=lambda e: handle_change(e, height_error_text),
                )
        tf_grid_width = ft.TextField(
                    label="Grid Width",
                    value=GRID_WIDTH_MIN,
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
                visit_simulator_button.disabled = not (check_color_pickers() and check_dimensions())
                page.update()
            except ValueError:
                error_text_control.visible = True

        # Define the function to handle the change in the radio group selection
        def stopping_condition_changed(e):
            global selected_stopping_condition
            if e.control.value == "Canvas All Painted":
                selected_stopping_condition = StoppingCondition.ALL_FILLED
            elif e.control.value == "Any Square Painted Twice":
                selected_stopping_condition = StoppingCondition.SECOND_DROP

        stopping_condition_label = ft.Text("Stopping Condition:")

        # Create the radio group with the stopping conditions
        stopping_condition_radio_group = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="Canvas All Painted", label="Canvas All Painted"),
                ft.Radio(value="Any Square Painted Twice", label="Any Square Painted Twice")
            ]),
            on_change=stopping_condition_changed,
            value="Canvas All Painted"  # Default selected value
        )

        if page.route == "/simulator":
            pass
        elif page.route == "/results":
            content_section = create_results_page(page)
        elif page.route == "/experiment":
            content_section = create_experiment_form(page)
        elif page.route == "/graph":
            content_section = create_graph_page()
        else: # page.route == "/":
            content_section = ft.Column(
                    [
                        height_error_text,
                        tf_grid_height,
                        width_error_text,
                        tf_grid_width,
                        ft.Row(controls=color_pickers),
                        stopping_condition_label,
                        stopping_condition_radio_group,
                        visit_simulator_button,
                    ],
                    alignment=ft.MainAxisAlignment.START, expand=8, scroll=ft.ScrollMode.ALWAYS
                )

        row = ft.Row(
                [
                    navigation_rail,
                    ft.VerticalDivider(width=1),
                    content_section,
                ],
                height=800, expand=True,
                alignment=ft.MainAxisAlignment.START
            )

            # Wrap the column in a container to set the background color
        container_with_bgcolor = ft.Container(
            content=row,
            bgcolor=ft.colors.WHITE,  # Set the background color here
        )

        page.views.append(container_with_bgcolor)
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, view=ft.AppView.WEB_BROWSER)
