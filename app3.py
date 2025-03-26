from shiny import reactive, req
import pandas as pd
from shiny.express import input, render, ui

# Load and prepare data
avg_list = pd.read_excel('AVG_converted.xlsx')
dom_list = pd.read_excel('DOM_converted.xlsx')
roto_list = pd.read_excel('DFO_converted.xlsx')

avg_list.set_index('Index', inplace=True)
roto_list = roto_list.fillna('')
dom_list["PTS"] = dom_list["PTS"].round(1)
dom_list["VORP"] = dom_list["VORP"].round(1)

len_avg = len(avg_list)
roto_list = roto_list[['RANK', 'PLAYER', 'POS', 'PTS', 'VORP', 'ADP']]
dom_list = dom_list[['RANK', 'PLAYER', 'POS', 'PTS', 'VORP', 'AVG', 'SOG', 'PPP']]

dom_list = dom_list.rename(columns={
    'RANK': 'DRANK', 'PLAYER': 'DPLAYER', 'PTS': 'DPTS', 'VORP': 'DVORP',
    'AVG': 'DAVG', 'SOG': 'DSOG', 'POS': 'DPOS', 'PPP': 'PPP'
})
roto_list = roto_list.rename(columns={
    'RANK': 'FRANK', 'PLAYER': 'FPLAYER', 'PTS': 'FPTS', 'VORP': 'FVORP',
    'ADP': 'FADP', 'POS': 'FPOS'
})

dom_list = dom_list[:len_avg]
roto_list = roto_list[:len_avg]

# Combine data for display
avg_list = pd.concat([avg_list, dom_list], axis=1, sort=False)
avg_list = pd.concat([avg_list, roto_list], axis=1, sort=False)
avg_list = reactive.value(avg_list)

# Initialize my_team
my_team = dom_list.copy()
my_team = my_team[0:0]
my_team['PICK_NO'] = 0
my_team['VALUE'] = 0
my_team_2 = pd.DataFrame(columns=['RANK', 'PLAYER', 'POS', 'VAL', 'YESNO'])

# Initialize counters
f = reactive.value(0)
d = reactive.value(0)
g = reactive.value(0)
tot_picked2 = reactive.value(0)
tot_val = reactive.value(0)

dom_list = reactive.value(dom_list)
roto_list = reactive.value(roto_list)
my_team_2 = reactive.value(my_team_2)

# Sidebar setup
with ui.sidebar(width='300px', position='right'):
    @render.text
    def highlighted_player():
        selected_rows = input.players_selected_rows()
        if selected_rows:
            player_name = avg_list().iloc[selected_rows[0], 1]
            return f"The highlighted player is: {player_name}"
        return ""

    ui.input_action_button("btn_remove", "Draft this player?")
    ui.input_radio_buttons("my_team_choice", "My Team:", {
        "No": ui.HTML("<span style='color:red;'>No</span>"),
        "Yes": "Yes"
    })


    @render.text
    def tot_picked():
        return f'F: {f()} D: {d()} G: {g()} Tot Picked: {tot_picked2()} Total val: {tot_val()}'

    @render.data_frame
    def my_team():
        return render.DataGrid(my_team_2(), filters=True, width='280px', height='600px')

# Main panel with player DataGrid
@render.data_frame
def players():
    return render.DataGrid(avg_list(), filters=True, selection_mode="row", width='1000px', height='780px')

# Define reactive effects
@reactive.effect
@reactive.event(input.btn_remove)
def remove_selected():
    """
    When input.btn_remove() is clicked, remove the rows in
    input.players_selected_rows()
    """
    row_nums = list(req(input.players_selected_rows()))

    if len(row_nums) == 0:
        return

    new_df = avg_list().copy()
    player_info = new_df.iloc[row_nums]
    pos = player_info.iloc[0, 2]
    pos = pos[0]
    player_name = player_info.iloc[0, 1]

    avg_list_2 = avg_list().copy()
    avg_list_2 = avg_list_2[['RANK', 'PLAYER', 'POS']]
    avg_list_2 = avg_list_2[avg_list_2.PLAYER != player_name]
    dom_list_2 = dom_list().copy()
    dom_list_2 = dom_list_2[['DRANK', 'DPLAYER', 'DPOS', 'DPTS', 'DVORP', 'DAVG', 'DSOG']]
    dom_list_2 = dom_list_2[dom_list_2.DPLAYER != player_name]
    roto_list_2 = roto_list().copy()
    roto_list_2 = roto_list_2[['FRANK', 'FPLAYER', 'FPOS', 'FPTS', 'FVORP', 'FADP']]
    roto_list_2 = roto_list_2[roto_list_2.FPLAYER != player_name]

    avg_list_2 = avg_list_2.sort_values(by=['RANK']).reset_index(drop=True)
    dom_list_2 = dom_list_2.sort_values(by=['DRANK']).reset_index(drop=True)
    roto_list_2 = roto_list_2.sort_values(by=['FRANK']).reset_index(drop=True)

    result = pd.concat([avg_list_2, dom_list_2], axis=1, sort=False)
    new_df_2 = pd.concat([result, roto_list_2], axis=1, sort=False)

    if pos == 'F':
        f.set(f.get() + 1)
    elif pos == 'D':
        d.set(d.get() + 1)
    elif pos == 'G':
        g.set(g.get() + 1)

    tot_picked2.set(tot_picked2.get() + 1)
    avg_list.set(new_df_2)
    dom_list.set(dom_list_2)
    roto_list.set(roto_list_2)

@reactive.effect
@reactive.event(input.my_team_choice)  # Updated ID
def update_my_team():
    selected_rows = list(req(input.players_selected_rows()))

    if not selected_rows:
        return

    yes_no = input.my_team_choice.get()  # Updated ID
    new_player_info = avg_list().iloc[selected_rows]

    my_team_3 = my_team_2().copy()

    if yes_no == 'Yes':
        for _, player_info in new_player_info.iterrows():
            rank = int(player_info['RANK'])
            tot_picked3 = f.get() + d.get() + g.get() + 1
            value = tot_picked3 - rank
            row = {
                'RANK': player_info['RANK'],
                'PLAYER': player_info['PLAYER'],
                'POS': player_info['POS'],
                'VAL': value,
                'YESNO': 'Yes'
            }
            my_team_3.loc[len(my_team_3)] = row
    elif yes_no == 'No':
        for _, player_info in new_player_info.iterrows():
            row = {
                'RANK': player_info['RANK'],
                'PLAYER': player_info['PLAYER'],
                'POS': player_info['POS'],
                'VAL': 0,
                'YESNO': 'Yes'
            }
            my_team_3.loc[len(my_team_3)] = row

    # Filter out players based on YESNO value
    my_team_3 = my_team_3[my_team_3.YESNO != 'No'].drop_duplicates(subset=['PLAYER'])
    tot_val.set(my_team_3['VAL'].sum())
    my_team_2.set(my_team_3)
