from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from scraper import fetch_data_for_all_companies_threaded
from technical_analysis import perform_technical_analysis

app = Flask(__name__)
UPLOAD_FOLDER = './data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'scrape':
            fetch_data_for_all_companies_threaded()
            return redirect(url_for('index'))

        company = request.form.get('company')
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        if company:
            file_path = os.path.join(UPLOAD_FOLDER, f"{company}.csv")
            if os.path.exists(file_path):
                data = preprocess_data(file_path)

                if date_from and date_to:
                    date_from = pd.to_datetime(date_from)
                    date_to = pd.to_datetime(date_to)
                    data = data[(data['Date'] >= date_from) & (data['Date'] <= date_to)]

                if data.empty:
                    return render_template(
                        'index.html',
                        error="No data available for the selected date range.",
                        companies=get_companies()
                    )

                if action == 'analyze_table':
                    table_html = data.to_html(index=False, classes='table table-striped')
                    return redirect(url_for(
                        'view_table',
                        company=company,
                        date_from=date_from,
                        date_to=date_to,
                        table=table_html
                    ))
                elif action == 'analyze_technical':
                    analysis_html = perform_technical_analysis(data, company)
                    return render_template(
                        'technical_analysis.html',
                        company=company,
                        analysis=analysis_html
                    )

            else:
                return render_template(
                    'index.html',
                    error=f"No data found for {company}.",
                    companies=get_companies()
                )

    return render_template('index.html', companies=get_companies())

def preprocess_data(file_path):
    data = pd.read_csv(file_path)
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y', errors='coerce')

    numeric_cols = ['Last trade price', 'Max', 'Min', 'Avg Price', '%chg.', 'Volume', 'TurnoverBEST_MKD', 'TotalTurnoverMKD']
    for col in numeric_cols:
        data[col] = data[col].replace({',': '', '"': ''}, regex=True).apply(pd.to_numeric, errors='coerce')

    return data

def get_companies():
    return [file.replace('.csv', '') for file in os.listdir(UPLOAD_FOLDER) if file.endswith('.csv')]

@app.route('/view_table', methods=['GET'])
def view_table():
    company = request.args.get('company')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    table_html = request.args.get('table')

    return render_template(
        'view_table.html',
        company=company,
        date_from=date_from,
        date_to=date_to,
        table=table_html
    )

if __name__ == '__main__':
    app.run(debug=True)
