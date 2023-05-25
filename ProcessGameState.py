import pandas as pd
import json

class ProcessGameState:
    def __init__(self, filePath):
        # load data into data var
        self.data = self.load_data(filePath)

    # return dataframe of parquet file
    def load_data(self, filePath):
        # convert parquet into data frame
        dataframe = pd.read_parquet(filePath, engine='pyarrow')

        return dataframe;

    # Parameters:
    # round number (int)
    # seconds in round (int)
    # player name (string)
    # (xBound, yBound) x and y boundaries as tuples ((int, int), (int, int))
    # Returns True if player within x and y bounds, else False
    def valid_boundary(self, round, seconds, player, xBound, yBound):
        # query for player in round, second
        query_string = "round_num == {} and seconds == {} and player == '{}'".format(round, seconds, player)
        query_res = self.data.query(query_string)

        x_min, x_max = xBound[0], xBound[1]
        y_min, y_max = yBound[0], yBound[1]

        for _, row in query_res.iterrows():
            x, y = row['x'], row['y']
            print(type(x))
            # return True on first instance of player within bounds
            if (x_min <= x) & (x <= x_max) & (y_min <= y) & (y <= y_max):
                print('Within bounds!')
                return True
        print('Not in bounds')
        return False

    # Parameters:
    # round number (int)
    # seconds into round (int)
    # side (CT/T) (string)
    # return list of weapon classes per player
    def get_weapons(self, round, seconds, side):
        # query for all players on side at round, seconds
        query_string = "round_num == {} and seconds == {} and side == '{}'".format(round, seconds, side)
        query_res = self.data.query(query_string)

        weapon_classes = []
        for _, row in query_res.iterrows():
            inventory_data = row['inventory']


            weapon_classes.append([weapon['weapon_class'] for weapon in inventory_data])
        print(weapon_classes)
        return weapon_classes

game_state = ProcessGameState('game_state_frame_data.parquet')
game_state.valid_boundary(5, 10, 'Player0', (-2000, 0), (-4000, 0))
game_state.get_weapons(3, 20, 'T')