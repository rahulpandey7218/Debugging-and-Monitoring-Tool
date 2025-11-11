import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

class PredictiveAnalysis:
    def __init__(self):
        self.model = None
        self.history = []
        self.forecast_steps = 5  # Number of steps to forecast
    
    def train_model(self, data, time_column='timestamp', value_column='value'):
        """Train ARIMA model on time series data"""
        if len(data) < 10:
            return {"error": "Not enough data for prediction (minimum 10 points required)"}
        
        # Convert to pandas series
        try:
            # If data is already a list of values, use it directly
            if isinstance(data[0], (int, float)):
                series = pd.Series(data)
            else:
                # Extract values from dictionaries
                series = pd.Series([item[value_column] for item in data])
            
            # Fit ARIMA model - using simple parameters for quick implementation
            self.model = ARIMA(series, order=(1, 1, 1))
            self.model_fit = self.model.fit()
            self.history = data
            
            return {"status": "success", "message": "Model trained successfully"}
        except Exception as e:
            return {"error": f"Error training model: {str(e)}"}
    
    def predict(self, steps=None):
        """Make predictions using the trained model"""
        if not self.model_fit:
            return {"error": "Model not trained yet"}
        
        steps = steps or self.forecast_steps
        
        try:
            # Get forecast
            forecast = self.model_fit.forecast(steps=steps)
            
            # Create timestamps for forecast
            last_timestamp = datetime.now()
            if self.history and isinstance(self.history[0], dict) and 'timestamp' in self.history[0]:
                try:
                    last_timestamp = datetime.fromisoformat(self.history[-1]['timestamp'])
                except:
                    pass
            
            # Format results
            results = []
            for i, value in enumerate(forecast):
                future_time = last_timestamp + timedelta(hours=i+1)
                results.append({
                    "timestamp": future_time.isoformat(),
                    "predicted_value": float(value),
                    "confidence_lower": float(value) - float(value) * 0.1,  # Simple 10% confidence interval
                    "confidence_upper": float(value) + float(value) * 0.1
                })
            
            return {
                "status": "success",
                "forecast": results
            }
        except Exception as e:
            return {"error": f"Error making prediction: {str(e)}"}
    
    def analyze_logs(self, logs, metric='error_count'):
        """Analyze logs and predict future trends"""
        if not logs:
            return {"error": "No logs provided for analysis"}
        
        try:
            # Group logs by hour and count errors
            hourly_data = []
            
            # Simple grouping by hour for demo
            hours = {}
            for log in logs:
                try:
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    hour_key = timestamp.strftime('%Y-%m-%d %H:00:00')
                    
                    if hour_key not in hours:
                        hours[hour_key] = 0
                    
                    # Count based on metric
                    if metric == 'error_count' and log['severity'] in ['ERROR', 'CRITICAL']:
                        hours[hour_key] += 1
                    elif metric == 'all_logs':
                        hours[hour_key] += 1
                except:
                    continue
            
            # Convert to time series
            for hour, count in hours.items():
                hourly_data.append({
                    "timestamp": hour,
                    "value": count
                })
            
            # Sort by timestamp
            hourly_data.sort(key=lambda x: x['timestamp'])
            
            # Train model on this data
            training_result = self.train_model(hourly_data)
            if 'error' in training_result:
                return training_result
            
            # Make prediction
            prediction = self.predict()
            
            return {
                "status": "success",
                "historical_data": hourly_data,
                "forecast": prediction.get('forecast', [])
            }
        except Exception as e:
            return {"error": f"Error analyzing logs: {str(e)}"}

# Create singleton instance
predictive_analyzer = PredictiveAnalysis()

def get_analyzer():
    return predictive_analyzer