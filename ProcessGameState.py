import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

    # Parameters:
    # Team 1 or 2
    # Side (CT or T)
    # Site area name (BombsiteA or BombsiteB)
    # Weapon classes
    def get_site_weapon_stats(self, team, side, site, weapons):
        # get team data for side and area
        team_data = self.data[(self.data['team'] == team) & (self.data['side'] == side) & (self.data['area_name'] == site)]
        # get only the first row where a player is in a site per round
        team_data = team_data.groupby(['round_num', 'player']).first().reset_index()
        # filter rows so only rounds with at least 2 or more rifles/smgs are included

        selected_cols = ['team', 'player', 'round_num', 'seconds', 'weapon_classes']

        # filter to get all rows with specified weapons
        team_data = team_data[team_data['weapon_classes'].apply(
            lambda x: any(weapon in x for weapon in weapons)
        )]

        # get rows that have at least 2 of the specified weapons in the round
        team_data = team_data[selected_cols].groupby('round_num').filter(
            lambda x: len(x) >= 2
        )
        print(team_data)
        print("Average time into round: {}".format(team_data['seconds'].mean()))

    # Parameters:
    # Team name
    # Side (CT or T)
    # Min_seconds into round (used for a min time threshold)
    # Site (area_name for site)
    # Generate heatmap for player coords on site
    def get_site_heatmap(self, team, side, min_seconds, site):
        # filter the data for relevant team data
        team_data = self.data[(self.data['team'] == team) & (self.data['side'] == side) & (self.data['area_name'] == site) & (self.data['seconds'] >= min_seconds)]
        # put all x and y coords into list
        x_coords = team_data['x'].tolist()
        y_coords = team_data['y'].tolist()

        heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=50)

        # Plot the heatmap
        plt.imshow(heatmap.T, origin='lower', cmap='hot', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
        plt.colorbar()
        plt.title("{} Player Positions on {} Side for {}".format(team, side, site))
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()


game_state = ProcessGameState('game_state_frame_data.parquet')
# game_state.get_bounds_stats('Team1', BOX_BOUNDS)
# game_state.get_bounds_stats('Team2', BOX_BOUNDS)
game_state.get_site_weapon_stats('Team2', 'T', 'BombsiteB', ['Rifle', 'SMG'])
game_state.get_site_heatmap('Team2', 'T', 30, 'BombsiteB')