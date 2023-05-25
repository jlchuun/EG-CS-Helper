import pandas as pd

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
    # Returns if player was within given x and y boundaries at any point
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

    # def get_weapons(self):
    #     parse inventory json for weapon classes
    #     return list of weapons

game_state = ProcessGameState('game_state_frame_data.parquet')
game_state.valid_boundary(5, 10, 'Player0', (-2000, 0), (-4000, 0))