import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
import os

class DataLoader:
    def __init__(self):
        self.base_path = os.path.join(os.getcwd(), 'data')
        self.df_app = None
        self.df_prev = None

    def load_data(self):
        """Loads specific columns with robust error handling."""
        app_path = os.path.join(self.base_path, 'application_data.csv')
        prev_path = os.path.join(self.base_path, 'previous_application.csv')

        # 1. Load Application Data
        if os.path.exists(app_path):
            print(f"Found {app_path}...")
            cols = ['TARGET', 'NAME_CONTRACT_TYPE', 'CODE_GENDER', 
                    'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'NAME_EDUCATION_TYPE']
            try:
                # Load 100k rows
                self.df_app = pd.read_csv(app_path, usecols=cols, nrows=100000)
                
                # FORCE NUMERIC: Coerce errors to NaN, then fill with 0
                self.df_app['AMT_INCOME_TOTAL'] = pd.to_numeric(self.df_app['AMT_INCOME_TOTAL'], errors='coerce').fillna(0)
                self.df_app['AMT_CREDIT'] = pd.to_numeric(self.df_app['AMT_CREDIT'], errors='coerce').fillna(0)
                
                print(f"  -> Loaded {len(self.df_app)} rows from Application Data.")
            except Exception as e:
                print(f"  -> Error reading Application Data: {e}")
        else:
            print(f"  -> WARNING: {app_path} not found.")

        # 2. Load Previous History
        if os.path.exists(prev_path):
            print(f"Found {prev_path}...")
            try:
                self.df_prev = pd.read_csv(prev_path, usecols=['DAYS_DECISION'], nrows=100000)
                
                # Clean DAYS_DECISION immediately
                self.df_prev['DAYS_DECISION'] = pd.to_numeric(self.df_prev['DAYS_DECISION'], errors='coerce')
                self.df_prev = self.df_prev.dropna(subset=['DAYS_DECISION'])
                
                print(f"  -> Loaded {len(self.df_prev)} rows from Previous Application Data.")
            except Exception as e:
                print(f"  -> Error reading Previous Application: {e}")
        else:
            print(f"  -> WARNING: {prev_path} not found.")
            
        return True

    def check_files(self):
        return self.df_app is not None

    # --- DEBUG VISUALIZATION LOGIC ---

    def plot_risk_distribution(self):
        if self.df_app is None: return "{}"
        
        counts = self.df_app['TARGET'].value_counts().reset_index()
        counts.columns = ['Status', 'Count']
        counts['Status'] = counts['Status'].map({0: 'Repayer', 1: 'Defaulter'})
        
        print(f"DEBUG Chart 1: Found {len(counts)} categories (Should be 2).")

        fig = px.pie(counts, names='Status', values='Count', 
                     title="Portfolio Risk Distribution",
                     color='Status',
                     color_discrete_map={'Repayer': '#00b894', 'Defaulter': '#d63031'},
                     hole=0.5)
        fig.update_layout(height=350, margin=dict(t=40, b=0, l=0, r=0))
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def plot_application_volume(self):
        # CHART 2 DEBUGGING
        if self.df_prev is None: return "{}"
        
        df = self.df_prev.copy()
        
        # 1. Convert to Months Ago
        df['Months_Ago'] = (df['DAYS_DECISION'].abs() / 30).astype(int)
        
        # REMOVED FILTER: Plotting ALL history to see if data exists
        trend = df.groupby('Months_Ago').size().reset_index(name='Count')
        trend = trend.sort_values('Months_Ago', ascending=False)

        print(f"DEBUG Chart 2: Plotting {len(trend)} months of history.")
        if len(trend) > 0:
            print(f"    -> Min Month: {trend['Months_Ago'].min()}, Max Month: {trend['Months_Ago'].max()}")

        fig = px.area(trend, x='Months_Ago', y='Count',
                      title="Application Volume History (All Time)",
                      color_discrete_sequence=['#0984e3'])
        
        fig.update_layout(xaxis=dict(autorange="reversed", title="Months Ago"),
                          yaxis=dict(title="Volume"),
                          height=350, margin=dict(t=40, b=0, l=0, r=0),
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def plot_education_risk(self):
        if self.df_app is None: return "{}"
        risk_edu = self.df_app.groupby('NAME_EDUCATION_TYPE')['TARGET'].mean().reset_index()
        risk_edu['TARGET'] = risk_edu['TARGET'] * 100
        risk_edu = risk_edu.sort_values('TARGET', ascending=True)

        fig = px.bar(risk_edu, x='TARGET', y='NAME_EDUCATION_TYPE', orientation='h',
                     title="Default Rate by Education",
                     labels={'TARGET': 'Default %', 'NAME_EDUCATION_TYPE': ''},
                     color='TARGET', color_continuous_scale='Reds')
        fig.update_layout(height=350, margin=dict(t=40, b=0, l=0, r=0), coloraxis_showscale=False)
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def plot_gender_split(self):
        if self.df_app is None: return "{}"
        fig = px.pie(self.df_app, names='CODE_GENDER', title="Gender Split",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(height=350, margin=dict(t=40, b=0, l=0, r=0))
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def plot_income_scatter(self):
        # CHART 5 DEBUGGING
        if self.df_app is None: return "{}"
        
        # Take a sample
        sample = self.df_app.sample(min(len(self.df_app), 2000)).copy()
        
        # FIX: Fill NaNs in TARGET before mapping
        sample['TARGET'] = sample['TARGET'].fillna(0).astype(int)
        sample['Risk_Status'] = sample['TARGET'].map({0: 'Repayer', 1: 'Defaulter'})
        
        # REMOVED FILTER: Plotting all incomes (even huge ones)
        # sample = sample[sample['AMT_INCOME_TOTAL'] < 1000000] 

        print(f"DEBUG Chart 5: Plotting {len(sample)} points.")
        print(f"    -> Income Range: {sample['AMT_INCOME_TOTAL'].min()} to {sample['AMT_INCOME_TOTAL'].max()}")

        fig = px.scatter(sample, x='AMT_INCOME_TOTAL', y='AMT_CREDIT', 
                         color='Risk_Status', 
                         title="Income vs Loan Amount",
                         labels={'AMT_INCOME_TOTAL': 'Income', 'AMT_CREDIT': 'Loan Amount'},
                         color_discrete_map={'Repayer': '#00b894', 'Defaulter': '#d63031'}, 
                         opacity=0.6)
        
        fig.update_layout(height=400, margin=dict(t=40, b=0, l=0, r=0))
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def get_visuals(self):
        return {
            'risk_dist': self.plot_risk_distribution(),
            'kpi_trend': self.plot_application_volume(),
            'edu_bar': self.plot_education_risk(),
            'gender_pie': self.plot_gender_split(),
            'income_box': self.plot_income_scatter(),
            'credit_hist': "{}"
        }

    def get_placeholders(self):
        return self.get_visuals()