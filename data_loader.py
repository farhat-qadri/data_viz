import pandas as pd
import plotly.graph_objects as go
import json
import plotly.utils
import os

class DataLoader:
    def __init__(self):
        self.base_path = os.path.join(os.getcwd(), 'data')

    def check_files(self):
        """Checks if files exist."""
        return os.path.exists(os.path.join(self.base_path, 'application_data.csv'))

    def get_placeholders(self):
        """
        Generates empty template charts. 
        This ensures the UI works even before you write the real analysis logic.
        """
        graphs = {}

        # Helper to create a stylish 'No Data Yet' chart
        def create_empty_plot(title, chart_type="Bar Chart"):
            fig = go.Figure()
            fig.update_layout(
                title=title,
                xaxis={"visible": False},
                yaxis={"visible": False},
                annotations=[{
                    "text": f"Waiting for Data Logic<br>({chart_type})",
                    "xref": "paper", "yref": "paper",
                    "showarrow": False, "font": {"size": 20, "color": "#95a5a6"}
                }],
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        # 1. Overview Tab Charts
        graphs['kpi_trend'] = create_empty_plot("Loan Application Volume", "Line Chart")
        graphs['risk_dist'] = create_empty_plot("Risk Distribution", "Pie Chart")
        
        # 2. Demographics Tab Charts
        graphs['edu_bar'] = create_empty_plot("Education Level Split", "Horizontal Bar")
        graphs['gender_pie'] = create_empty_plot("Gender Balance", "Donut Chart")
        
        # 3. Financials Tab Charts
        graphs['income_box'] = create_empty_plot("Income vs Loan Amount", "Scatter Plot")
        graphs['credit_hist'] = create_empty_plot("Credit Bureau History", "Stacked Bar")

        return graphs