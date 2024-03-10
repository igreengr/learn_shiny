import pandas as pd
from shiny import reactive, req
from shiny.express import input, render, ui

avg_list = pd.read_excel('AVG_converted.xlsx')
dom_list = pd.read_excel('DOM_converted.xlsx')
roto_list = pd.read_excel('DFO_converted.xlsx')
avg_list.set_index('Index', inplace=True)
roto_list = roto_list.fillna('')
dom_list["PTS"] = dom_list["PTS"].round(1)
dom_list["VORP"] = dom_list["VORP"].round(1)
len_avg = len(avg_list)
# inj_list = roto_list[['PLAYER', 'INJ']]
roto_list = roto_list[['RANK', 'PLAYER', 'POS', 'PTS', 'VORP', 'ADP']]
dom_list = dom_list[['RANK', 'PLAYER', 'POS', 'PTS', 'VORP', 'AVG', 'SOG']]
dom_list = dom_list.rename(columns={'RANK': 'DRANK', 'PLAYER': 'DPLAYER', 'PTS': 'DPTS', 'VORP': 'DVORP', 'AVG': 'DAVG',
                                    'SOG': 'DSOG', 'POS': 'DPOS'})
roto_list = roto_list.rename(columns={'RANK': 'FRANK', 'PLAYER': 'FPLAYER', 'PTS': 'FPTS', 'VORP': 'FVORP', 'ADP': 'FADP',
                                    'POS': 'FPOS'})

dom_list = dom_list[:len_avg]
roto_list = roto_list[:len_avg]

avg_list = pd.concat([avg_list, dom_list], axis=1, sort=False)
avg_list = pd.concat([avg_list, roto_list], axis=1, sort=False)
avg_list = reactive.value(avg_list)
my_team = dom_list.copy()
my_team = my_team[0:0]
my_team['PICK_NO'] = 0
my_team['VALUE'] = 0

f = 0
d = 0
g = 0

f = reactive.value(f)
d = reactive.value(d)
g = reactive.value(g)


@render.data_frame()
def players():
    # ui.update_dark_mode("dark")
    return render.DataGrid(avg_list(), filters=True, row_selection_mode="single", width='fit-content', height='900px')

with ui.sidebar():
    ui.input_action_button("btn_remove", "Remove selected")
#    ui.input_action_button("my_team", "My Team?")

    ui.input_radio_buttons("my_team","My Team:",{"No": ui.HTML("<span style='color:red;'>No</span>"),
            "Yes": "Yes",},)

    @render.text
    def tot_picked():
        return f'Forwards: {f()} Defensemen: {d()} Goalies: {g()}'

@reactive.effect
@reactive.event(input.btn_remove)
def remove_selected():
    """
    When input.btn_remove() is clicked, remove the rows in
    input.players_selected_rows()
    """

    row_nums = list(req(input.players_selected_rows()))
    # print(row_nums, 'row nums')
    if len(row_nums) == 0:
        return
    new_df = avg_list().copy()
    player_info = 0
    player_info = new_df.iloc[row_nums]
    # print(player_info, 'player_info')
    pos = player_info.iloc[0, 2]
    pos = pos[0]
    player_name = player_info.iloc[0, 1]
    avg_list_2 = avg_list().copy()
    avg_list_2 = avg_list_2[['RANK', 'PLAYER', 'POS']]
    avg_list_2 = avg_list_2[avg_list_2.PLAYER != player_name]
    dom_list_2 = dom_list.copy()
    dom_list_2 = dom_list_2[['DRANK', 'DPLAYER', 'DPOS', 'DPTS', 'DVORP', 'DAVG', 'DSOG']]
    dom_list_2 = dom_list_2[dom_list_2.DPLAYER != player_name]
    roto_list_2 = roto_list.copy()
    roto_list_2 = roto_list_2[['FRANK', 'FPLAYER', 'FPOS', 'FPTS', 'FVORP', 'FADP']]
    roto_list_2 = roto_list_2[roto_list_2.FPLAYER != player_name]
    avg_list_2 = avg_list_2.sort_values(by=['RANK'])
    dom_list_2 = dom_list_2.sort_values(by=['DRANK'])
    roto_list_2 = roto_list_2.sort_values(by=['FRANK'])
    avg_list_2 = avg_list_2.reset_index(drop=True)
    dom_list_2 = dom_list_2.reset_index(drop=True)
    roto_list_2 = roto_list_2.reset_index(drop=True)
    result = pd.concat([avg_list_2, dom_list_2], axis=1, sort=False)
    new_df = pd.concat([result, roto_list_2], axis=1, sort=False)

    if pos == 'F':
        newpos = f.get() + 1
        f.set(newpos)
    if pos == 'D':
        newpos = d.get() + 1
        d.set(newpos)
    if pos == 'G':
        newpos = g.get() + 1
        g.set(newpos)
    # new_df = new_df.drop(new_df.index[row_nums])
    print(new_df)
    avg_list.set(new_df)

    @reactive.effect
    @reactive.event(input.my_team)
    # def my_team():
        #print('hello')
    def val():
        yes_no = input.my_team.get()
        print(player_name, yes_no)
        if yes_no == 'Yes':
            print(player_name, 'player')