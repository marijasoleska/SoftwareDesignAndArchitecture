from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from scraper import fetch_data_for_all_companies_threaded

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
                data = pd.read_csv(file_path)
                data = data.fillna('')


                if date_from and date_to:
                    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                    date_from = pd.to_datetime(date_from)
                    date_to = pd.to_datetime(date_to)
                    filtered_data = data[(data['Date'] >= date_from) & (data['Date'] <= date_to)]
                else:
                    filtered_data = data

                if filtered_data.empty:
                    return render_template(
                        'index.html',
                        error="No data available for the selected date range.",
                        companies=get_companies()
                    )


                filtered_data_html = filtered_data.to_html(index=False, classes='table table-striped')
                return redirect(url_for(
                    'view_table',
                    company=company,
                    date_from=date_from,
                    date_to=date_to,
                    table=filtered_data_html
                ))

            else:
                return render_template(
                    'index.html',
                    error=f"No data found for {company}.",
                    companies=get_companies()
                )

    return render_template('index.html', companies=get_companies())

# def generate_graph(data, company, column='Avg Price'):
#     import matplotlib.pyplot as plt
#
#
#     data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
#
#     data[column] = pd.to_numeric(data[column], errors='coerce')
#
#     data = data.dropna(subset=['Date', column])
#
#     if data.empty:
#         return None  # Return None if no valid data is left to plot
#
#     plt.figure(figsize=(10, 5))
#     plt.plot(data['Date'], data[column], label=column.capitalize(), color='blue')
#     plt.title(f"{column.capitalize()} Trend for {company}")
#     plt.xlabel("Date")
#     plt.ylabel(column.capitalize())
#     plt.grid(True)
#     plt.legend()
#
#
#     graph_path = f"./static/{company}_{column}_graph.png"
#     plt.savefig(graph_path)
#     plt.close()
#
#     return graph_path

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
