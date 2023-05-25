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
    # def valid_boundary(self, round, seconds, player, xBound, yBound):


    # def get_weapons(self):
    #     parse inventory json for weapon classes
    #     return list of weapons

game_state = ProcessGameState('game_state_frame_data.parquet')
game_state.valid_boundary(5, 10, 'Player0', (-2000, 0), (-4000, 0))