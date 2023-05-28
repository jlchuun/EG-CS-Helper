import pandas as pd
from shapely.geometry import Point, Polygon
import json

# Boundary vertices for light blue area
BOX_BOUNDS = ((-1735, 250), (-2806, 742), (-2472, 1233), (-1565, 580))


class ProcessGameState:
    def __init__(self, filePath):
        # load data into data var
        self.data = self.load_data(filePath)

    # return dataframe of parquet file
    def load_data(self, filePath):
        # convert parquet into data frame
        dataframe = pd.read_parquet(filePath, engine='pyarrow')

        # create new column for weapon classes
        dataframe['weapon_classes'] = dataframe['inventory'].apply(
            lambda inventory: [item['weapon_class'] for item in inventory] if inventory is not None else []
        )

        return dataframe;

    # Parameters:
    # (x, y) coordinates
    # boundary vertices (3 or more) to form boundary shape
    # Returns True if coordinates within boundaries, else False
    def within_boundary(self, x, y, bounds):
        point = Point(x, y)
        bound_shape = Polygon(bounds)

        if (bound_shape.contains(point)):
            return True
        return False

    # Parameters:
    # Team 1 or 2
    # boundary for analysis
    # Prints statistics for side statistics at specified boundary
    def get_bounds_stats(self, team, boundary):
        team_data = self.data[self.data['team'] == team]
        t_total_rounds = team_data[team_data['side'] == 'T']['round_num'].nunique()
        ct_total_rounds = team_data[team_data['side'] == 'CT']['round_num'].nunique()

        # Count rounds both teams entered boundary at least once
        ct_count = team_data[team_data['side'] == 'CT'].groupby('round_num').filter(
            lambda x: any(x[['x', 'y']].apply(lambda row: self.within_boundary(row['x'], row['y'], BOX_BOUNDS), axis=1)))[
            'round_num'].nunique()

        t_count = team_data[team_data['side'] == 'T'].groupby('round_num').filter(
            lambda x: any(x[['x', 'y']].apply(lambda row: self.within_boundary(row['x'], row['y'], BOX_BOUNDS), axis=1)))[
            'round_num'].nunique()

        print("'{}' Stats: ".format(team))
        print("T entered bounds {} / {} rounds".format(t_count, t_total_rounds))
        print("CT entered bounds {} / {} rounds".format(ct_count, ct_total_rounds))





game_state = ProcessGameState('game_state_frame_data.parquet')
# game_state.get_bounds_stats('Team1', BOX_BOUNDS)
# game_state.get_bounds_stats('Team2', BOX_BOUNDS)
game_state.get_site_stats('Team2', 'T', 'BombsiteB', ['Rifles', 'SMGs'])