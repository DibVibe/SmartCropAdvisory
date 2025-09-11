import React, { useState, useRef } from 'react';
import './DiseaseDetector.css';

const DiseaseDetector = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedImage(file);
        setImagePreview(URL.createObjectURL(file));
        setError(null);
        setAnalysisResult(null);
      } else {
        setError('Please select a valid image file');
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        setSelectedImage(file);
        setImagePreview(URL.createObjectURL(file));
        setError(null);
        setAnalysisResult(null);
      } else {
        setError('Please select a valid image file');
      }
    }
  };

  const simulateAnalysis = () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    // Simulate API call with mock data
    setTimeout(() => {
      const mockResult = {
        disease: 'Tomato Leaf Blight',
        confidence: 0.92,
        description: 'Early blight is a common fungal disease affecting tomato plants.',
        symptoms: [
          'Dark brown spots on leaves',
          'Yellow halos around spots',
          'Leaf wilting and dropping'
        ],
        treatment: [
          'Apply copper-based fungicide',
          'Remove affected leaves immediately',
          'Improve air circulation around plants',
          'Water at soil level, avoid wetting leaves'
        ],
        prevention: [
          'Use resistant varieties when possible',
          'Practice crop rotation',
          'Maintain proper plant spacing',
          'Apply preventive fungicide sprays'
        ]
      };
      setAnalysisResult(mockResult);
      setIsAnalyzing(false);
    }, 2000);
  };

  const resetAnalysis = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setAnalysisResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getSeverityColor = (confidence) => {
    if (confidence > 0.8) return '#e74c3c';
    if (confidence > 0.6) return '#f39c12';
    return '#27ae60';
  };

  return (
    <div className="disease-detector">
      <div className="detector-header">
        <h2>🌾 Plant Disease Detection</h2>
        <p>Upload an image of your plant leaf to detect diseases using AI</p>
      </div>

      <div className="detector-content">
        <div className="image-upload-section">
          <div
            className={`upload-area ${selectedImage ? 'has-image' : ''}`}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            {imagePreview ? (
              <div className="image-preview">
                <img src={imagePreview} alt="Selected crop" />
                <div className="image-overlay">
                  <button className="change-image-btn">📷 Change Image</button>
                </div>
              </div>
            ) : (
              <div className="upload-placeholder">
                <div className="upload-icon">📸</div>
                <h3>Upload Crop Image</h3>
                <p>Drag and drop an image here or click to browse</p>
                <p className="supported-formats">Supports: JPG, PNG, WEBP</p>
              </div>
            )}
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="file-input-hidden"
          />
        </div>

        <div className="analysis-section">
          <div className="analysis-controls">
            <button
              className={`analyze-btn ${!selectedImage || isAnalyzing ? 'disabled' : ''}`}
              onClick={simulateAnalysis}
              disabled={!selectedImage || isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <div className="spinner"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  🔍 Analyze Disease
                </>
              )}
            </button>
            
            {(selectedImage || analysisResult) && (
              <button className="reset-btn" onClick={resetAnalysis}>
                🔄 Reset
              </button>
            )}
          </div>

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {analysisResult && (
            <div className="analysis-results">
              <div className="result-header">
                <h3>🔬 Analysis Results</h3>
              </div>
              
              <div className="disease-info">
                <div className="disease-name">
                  <h4>{analysisResult.disease}</h4>
                  <div 
                    className="confidence-badge"
                    style={{ backgroundColor: getSeverityColor(analysisResult.confidence) }}
                  >
                    {Math.round(analysisResult.confidence * 100)}% Confidence
                  </div>
                </div>
                
                <div className="disease-description">
                  <h5>📋 Description:</h5>
                  <p>{analysisResult.description}</p>
                </div>

                <div className="disease-symptoms">
                  <h5>🌿 Symptoms:</h5>
                  <ul>
                    {analysisResult.symptoms.map((symptom, index) => (
                      <li key={index}>{symptom}</li>
                    ))}
                  </ul>
                </div>

                <div className="treatment-suggestions">
                  <h5>💊 Treatment Recommendations:</h5>
                  <div className="treatment-list">
                    {analysisResult.treatment.map((treatment, index) => (
                      <div key={index} className="treatment-item">
                        <span className="treatment-icon">✅</span>
                        <span>{treatment}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="prevention-tips">
                  <h5>🛡️ Prevention Tips:</h5>
                  <div className="prevention-list">
                    {analysisResult.prevention.map((tip, index) => (
                      <div key={index} className="prevention-item">
                        <span className="prevention-icon">🔒</span>
                        <span>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DiseaseDetector;
