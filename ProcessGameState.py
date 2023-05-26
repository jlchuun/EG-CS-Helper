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
    def within_boundary(self, x, y, boundary_vertices):
        # query for player in round, second
        query_string = "round_num == {} and seconds == {} and player == '{}'".format(round, seconds, player)
        query_res = self.data.query(query_string)

        for _, row in query_res.iterrows():
            x, y = row['x'], row['y']
            point = Point(x, y)
            bound_shape = Polygon(boundary_vertices)

            if (bound_shape.contains(point)):
                print("Within Bounds")
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
# game_state.valid_boundary(10, 30, 'Player0', BOX_BOUNDS)
game_state.get_weapons(3, 20, 'T')