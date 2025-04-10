import geopandas as gpd
import pandas as pd

# ============================================================================
# process_data.py
# This script processes spatial data for Hillsborough Safety Services 3D project.
# It reads GeoJSON files, performs spatial joins to count the number of service points
# within each census tract, computes a composite index, and exports the result as a new GeoJSON file.
# Detailed comments are provided to help you learn each step.
# ============================================================================

# STEP 1: Load the datasets from the 'data' folder
# We use GeoPandas to read our GeoJSON files containing point data for various services
# and polygon data for census tracts.

# Load point data for each service type
fire_stations = gpd.read_file('data/FireStations.geojson')
hospitals = gpd.read_file('data/Hospitals.geojson')
libraries = gpd.read_file('data/Libraries.geojson')
schools = gpd.read_file('data/Schools.geojson')

# Load polygon data for census tracts
census_tracts = gpd.read_file('data/Hills_census_tracts.geojson')

# STEP 2: Ensure all datasets use the same Coordinate Reference System (CRS)
# Converting all datasets to WGS84 (EPSG:4326) for consistency in spatial operations

datasets = [fire_stations, hospitals, libraries, schools, census_tracts]
for ds in datasets:
    ds.to_crs(epsg=4326, inplace=True)

# STEP 3: Define a helper function to count points within each census tract

def count_points_in_tracts(points, tracts, col_name):
    """
    Count the number of points (e.g., service locations) that fall within each census tract.

    Args:
        points (GeoDataFrame): GeoDataFrame with point data for a specific service type.
        tracts (GeoDataFrame): GeoDataFrame with polygon data (census tracts).
        col_name (str): Name of the new column to store the counts in the tracts GeoDataFrame.

    Returns:
        GeoDataFrame: Updated census tracts GeoDataFrame with a new column containing the counts.
    """
    # Perform a spatial join to find points that are contained within each tract
    join = gpd.sjoin(tracts, points, how='left', predicate='contains')
    
    # Group by the index of the tracts and count the number of points per tract
    counts = join.groupby(join.index).size()
    
    # Add the counts as a new column in the tracts GeoDataFrame
    tracts[col_name] = counts
    
    # Replace any missing values (tracts with no points) with 0
    tracts[col_name] = tracts[col_name].fillna(0).astype(int)
    
    return tracts

# Make a copy of census_tracts to preserve the original data
tracts = census_tracts.copy()

# STEP 4: Count the services for each type using the helper function
tracts = count_points_in_tracts(fire_stations, tracts, 'fire_count')
tracts = count_points_in_tracts(hospitals, tracts, 'hospital_count')
tracts = count_points_in_tracts(libraries, tracts, 'library_count')
tracts = count_points_in_tracts(schools, tracts, 'school_count')

# STEP 5: Compute the Composite Index for each census tract
# For this example, we simply sum the counts of all service types. You can adjust weights as needed.
tracts['composite_index'] = (
    tracts['fire_count'] +
    tracts['hospital_count'] +
    tracts['library_count'] +
    tracts['school_count']
)

# Optional: Print a summary of the computed values for verification
print(tracts[['fire_count', 'hospital_count', 'library_count', 'school_count', 'composite_index']].head())

# STEP 6: Save the resulting GeoDataFrame as a new GeoJSON file
# This file will be used in the interactive map to visualize the composite index.
output_path = 'data/services_index.geojson'
tracts.to_file(output_path, driver='GeoJSON')

print("GeoJSON with composite index saved to:", output_path)
