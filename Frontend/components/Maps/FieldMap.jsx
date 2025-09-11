import React from 'react';
import './FieldMap.css';

const FieldMap = () => {
  return (
    <div className="field-map">
      <h2>Field Mapping</h2>
      <div className="map-container">
        <div className="map-placeholder">
          <p>Interactive field map will be displayed here</p>
          <div className="map-controls">
            <button className="btn btn-primary">Add Field</button>
            <button className="btn btn-secondary">Satellite View</button>
            <button className="btn btn-secondary">Terrain View</button>
          </div>
        </div>
      </div>
      <div className="field-info">
        <h3>Field Information</h3>
        <p>Select a field on the map to view detailed information</p>
      </div>
    </div>
  );
};

export default FieldMap;
