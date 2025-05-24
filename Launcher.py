# launcher.py
import os
import sys
from Db_Functions import setup_database, get_db_path, add_record, search_records, fetch_summary, parse_search_query, delete_record
from nicegui import ui


def check_environment():
    # Check if SQLite is functional
    try:
        import sqlite3
        test_conn = sqlite3.connect(':memory:')
        test_conn.close()
        print("SQLite is working correctly.")
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        sys.exit("SQLite is not working. Please check your environment.")

    # Check database path and permissions
    db_path = get_db_path()
    if not os.access(os.path.dirname(db_path), os.W_OK):
        sys.exit(f"No write access to the database directory: {os.path.dirname(db_path)}")

    # Check if the database is set up
    if not os.path.exists(db_path):
        print("Database not found. Setting it up...")
        setup_database()
    else:
        # Print this message only once
        print("Database is ready.")

def run_app():
    # Start the NiceGUI application
    
    

    def open_add_form():
        # Overlay for the add record form
        with ui.dialog() as dialog:
            dialog.open()  # Open the overlay immediately

            #with ui.row().classes('w-full flex flex-row top-4 align-top justify-center items-center'):
            #    ui.label('Add a New Record').classes('absolute top-4 text-lg font-bold mb-4 align-top justify-center items-center')
            #    ui.button(icon='close', on_click=lambda: overlay.set_visibility(False)).classes('absolute top-4 right-4 bg-red-500 text-white px-4 py-2 rounded justify-end')

            with ui.column(align_items='center').classes('bg-white').style("padding: 20px;"):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Detailed Records').classes('text-lg font-bold')
                    ui.button(icon='close', on_click=lambda: dialog.close()).classes('bg-red-500 text-white px-2 py-1 rounded')
            
            
                # Form fields container
                #with ui.grid(columns=2).classes('w-full'):
                with ui.row().classes('w-full flex flex-row top-4 align-top justify-center items-center'):
                    with ui.column().classes('justify-between w-1/2 pr-2'):
                        whom = ui.input(label='Whom').classes('w-full').style("width: 100%;")
                        why = ui.input(label='Why').classes('w-full')
                        amount = ui.input(label='Amount').classes('w-full')
                    
                    #with ui.column().classes('w-1/3 pl-2'):
                    #    pass
                        #amount = ui.input(label='Amount')
                    
                    with ui.column().classes('w-1/2'):
                        date = ui.date(mask='YYYY-MM-DD').classes('w-full')

                def submit():
                    if not (whom.value and date.value and why.value and amount.value):
                        ui.notify('All fields are required!', type='negative')
                        return
                    
                    try:
                        add_record(whom.value, date.value, why.value, float(amount.value))
                        ui.notify('Record added successfully!', type='positive')
                        whom.value, date.value, why.value, amount.value = '', '', '', ''  # Clear inputs
                        print("called refresh_summary from submit")
                        refresh_summary()
                        dialog.close()
                    except Exception as e:
                        ui.notify(f"Error: {e}", type='negative')

                # Submit button
                ui.button('Add', on_click=submit).classes('bg-blue-500 text-white px-4 py-2 rounded w-full mt-4')
    
    def open_record(List):
        # Create a standalone overlay for displaying detailed records
        with ui.dialog().classes('w-full') as dialog:
            dialog.open()  # Open the overlay immediately

            # Add a header row with a title and close button
            

            # Display the table with the detailed records
            if List:
                
                columns = [
                    {'name': 'Money_Owed', 'label': 'Money_Owed', 'field': 'Money_Owed'},
                    {'name': 'Why', 'label': 'Why', 'field': 'Why'},
                    {'name': 'Date', 'label': 'Date', 'field': 'Date'},
                    {'name': 'Name', 'label': 'Name', 'field': 'Name'},
                ]
                rows = [
                    {'Money_Owed': row[4], 'Date': row[3], 'Why' : row[2], 'Name': row[1], 'ID': row[0] } for row in List
                ]

                # Create the table
                table = ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='ID',
                    selection='multiple'
                ).classes('w-full text-center').style("padding: 10px;")


                # Add a slot for the top header
                with table.add_slot('top'):
                    with ui.row().classes('w-full justify-between items-center mb-4'):
                        ui.label('Detailed Records').classes('text-lg font-bold')
                        ui.button(icon='close', on_click=dialog.close).classes('bg-red-500 text-white px-2 py-1 rounded')
                
                def _delete_record(ids):
                    global rows
                    for id in ids:
                        delete_record(id=id["ID"])

                    # Fetch updated detailed records and update the detailed table
                    rows = [
                        {'Money_Owed': row[4], 'Date': row[3], 'Why' : row[2], 'Name': row[1], 'ID': row[0] } for row in search_records(whom=List[0][1], group_by_whom=False, like_whom=False)
                    ]

                    table.update()  # Update the detailed table dynamically

                    refresh_summary()  # Refresh the summary table to reflect changes




                with table.add_slot('bottom'):
                    #ui.label().bind_text_from(table, 'selected', lambda val: f'Current selection: {val}')
                    ui.button('Remove', on_click=lambda: _delete_record(ids=table.selected)) \
                        .bind_visibility_from(table, 'selected', backward=lambda val: bool(val)).style("margin: 10px;")


                

            else:
                ui.label('No detailed records available.') 


    def make_summary_table(List):
        summary_container.clear()
        
        def select_item(event_args):
            detailed_results = search_records(whom=event_args["Name"], group_by_whom=False, like_whom=False)
            open_record(detailed_results)

        if List:
            with summary_container:
                
                table = ui.table(rows=[
                    {'Total Money Owed': row[4], 'Date': row[3], 'Name': row[1] } for row in List
                ], row_key="Name").classes('w-full mx-auto h-64 overflow-auto mb-4')#.classes("w-full")

                table.on('rowClick', lambda e: select_item(e.args[1])) #print("something something :",e.args[1]))
        else:
            with summary_container:
                ui.label('No summary available.')

    def refresh_summary():
        # Refresh the summary table
        results = fetch_summary()
        make_summary_table(results)
    
    @ui.page('/')
    def main_page():
        ui.label('Expense Tracker BY YAHYA MATER').classes('text-2xl font-bold mb-4 text-center')

        # Search bar
        with ui.row().classes('w-3/4 mx-auto mb-4'):
            search_input = ui.input(placeholder='Search records...').classes('flex-grow')
            def search():
                #records_container.clear()
                #results = search_records(whom=search_input.value, start_date=None, end_date=None, why=None)

                #name, start_date, end_date, min_amount, max_amount = parse_search_query(search_input.value)
                results = search_records(*parse_search_query(search_input.value))
                make_summary_table(results)
            ui.button(icon='search', on_click=search).classes('ml-2')

        # Container for search results
        #records_container = ui.column().classes('w-3/4 mx-auto mb-4')

        # Summary table
        global summary_container
        summary_container = ui.card().classes('w-3/4 mx-auto h-64 mb-4')


        refresh_summary()

        # Add record button
        ui.button('Add Record', on_click=open_add_form).classes('fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded')

    #ui.run()
    ui.run(reload=False,native=True)




if __name__ in {"__main__", "__mp_main__"}:
    check_environment()
    run_app()
