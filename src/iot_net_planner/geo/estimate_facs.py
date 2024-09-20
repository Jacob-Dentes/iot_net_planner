"""Provides a function for guessing some good potential gateway locations based on building corners
"""

import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
# from scipy.cluster.vq import kmeans2
from sklearn.cluster import MiniBatchKMeans
from shapely.geometry import Point

def generate_facs(area, n_facs=None, sampler=None):
    """Estimate potential gateway locations for an area. Estimated locations
    will be the corners of buildings.

    :param area: a loaded KML area loaded with geo.demand_grid.load_file
    :type area: gpd.GeoDataFrame
    :param n_facs: the target number of potential gateway locations to find.
        If it can't find enough it will return as many as it finds. If None, 
        returns all found facs, defaults to None.
    :type n_facs: int, optional
    :param sampler: if a sampler is provided then it will be used to fill
        the altitude column. Must be initialized with area's crs. If None,
        no altitude is given, defaults to None
    :type sampler: class: `iot_net_planner.geo.sampler.LinkSampler`, optional
    """
    all_buildings = []

    # Query buildings and build a dataframe
    for geom in area.to_crs("EPSG:4326").geometry:
        buildings = ox.features.features_from_polygon(geom, {'building': True})
        buildings = buildings.explode(index_parts=False).to_crs(area.crs)
        all_buildings.append(buildings[['geometry']])

    buildings = gpd.GeoDataFrame(pd.concat(all_buildings, ignore_index=True))
    
    buildings = buildings[buildings.geometry.apply(lambda geom: geom.geom_type).isin(['Point', 'Polygon'])]

    # Sample at centroids to fill altitude
    if sampler is not None:
        buildings['center'] = buildings.geometry.apply(lambda geom: geom if geom.geom_type == 'Point' else geom.centroid)
        samples = sampler.batched_sample(buildings['center'].x, buildings['center'].y)
        buildings['altitude'] = np.array(samples)
    else:
        buildings['altitude'] = None

    points_list = []

    # Break buildings into corner points
    for _, row in buildings.iterrows():
        if row.geometry.geom_type == 'Point':
            points_list.append({'geometry': row.geometry, 'altitude': row['altitude']})
        elif row.geometry.geom_type == 'Polygon':
            for point in row.geometry.exterior.coords:
                points_list.append({'geometry': gpd.points_from_xy([point[0]], [point[1]])[0], 'altitude': row['altitude']})    

    buildings = gpd.GeoDataFrame(points_list, crs=buildings.crs)    
    if sampler is None:
        buildings.drop('altitude', axis=1, inplace=True)

    buildings = buildings[buildings.geometry.apply(lambda point: any(area.contains(point)))]
    buildings.reset_index(inplace=True)

    if n_facs is None or len(buildings) <= n_facs:
        return buildings

    # Kmeans clustering to choose n_facs gateways
    means_array = np.empty((len(buildings), 2))
    means_array[:, 0] = buildings.geometry.x
    means_array[:, 1] = buildings.geometry.y

    # centroids, labels = kmeans2(means_array, n_facs, minit="++", missing="raise")        
    kmeans = MiniBatchKMeans(n_clusters=n_facs, init='k-means++')
    kmeans.fit(means_array)

    centroids = kmeans.cluster_centers_
    labels = kmeans.labels_

    indices = []
    if 'altitude' in buildings:
        for label in np.unique(labels):
            cluster = buildings[labels == label]

            if not cluster.empty:
                max_altitude_index = cluster['altitude'].idxmax()
                indices.append(max_altitude_index)

    else:
        for centroid in centroids:
            centroid = Point(centroid[0], centroid[1])
            indices.append(buildings.geometry.distance(centroid).argmin())
        
    return buildings.iloc[indices]
