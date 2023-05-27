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

    # Parameters:
    # boundary for analysis
    # Prints statistics for side statistics at specified boundary
    # Note: Uses both teams for side statistics
    def get_bounds_stats(self, boundary):
        total_rounds = self.data['round_num'].nunique()

        # Count rounds both teams entered boundary at least once
        ct_count = self.data[self.data['side'] == 'CT'].groupby('round_num').filter(
            lambda x: any(x[['x', 'y']].apply(lambda row: self.within_boundary(row['x'], row['y'], BOX_BOUNDS), axis=1)))[
            'round_num'].nunique()

        t_count = self.data[self.data['side'] == 'T'].groupby('round_num').filter(
            lambda x: any(x[['x', 'y']].apply(lambda row: self.within_boundary(row['x'], row['y'], BOX_BOUNDS), axis=1)))[
            'round_num'].nunique()

        print("T entered bounds {} / {} rounds".format(t_count, total_rounds))
        print("CT entered bounds {} / {} rounds".format(ct_count, total_rounds))


game_state = ProcessGameState('game_state_frame_data.parquet')
game_state.get_bounds_stats(BOX_BOUNDS)

game_state.get_weapons(3, 20, 'T')