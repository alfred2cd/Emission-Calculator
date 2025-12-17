<!-- templates/report.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emission Report - LAMATA</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .report-header { background: #0066cc; color: white; padding: 30px; border-radius: 10px; }
        .section-title { border-left: 4px solid #0066cc; padding-left: 15px; margin: 30px 0 20px 0; }
        .emission-table th { background-color: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container mt-5 mb-5">
        <!-- Report Header -->
        <div class="report-header">
            <div class="row">
                <div class="col-md-8">
                    <h1>Carbon Footprint Report</h1>
                    <h4>{{ report.organization.name }}</h4>
                    <p>{{ report.organization.address }}</p>
                </div>
                <div class="col-md-4 text-end">
                    <p>Reporting Period: {{ report.organization.reporting_period.start }} to {{ report.organization.reporting_period.end }}</p>
                    <p>Prepared by: {{ report.prepared_by }}</p>
                    <p>Date: {{ report.date }}</p>
                </div>
            </div>
        </div>

        <!-- Executive Summary -->
        <div class="mt-5">
            <h3 class="section-title">Executive Summary</h3>
            <div class="row">
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h2>{{ "{:,.0f}".format(report.emissions.totals.total) }}</h2>
                            <p class="text-muted">Total CO2e Emissions (kg)</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-body">
                            <h5>Key Findings</h5>
                            <ul>
                                <li>Scope 1 emissions contribute {{ "%.1f"|format(report.emissions.totals.scope1/report.emissions.totals.total*100) }}% of total emissions</li>
                                <li>Largest emission source: {{ "Transport Operations" if report.emissions.totals.scope1 > report.emissions.totals.scope2 else "Electricity Consumption" }}</li>
                                <li>Employee commuting contributes {{ "%.1f"|format(sum(report.emissions.scope3.employee_commuting.values())/report.emissions.totals.total*100) }}% to Scope 3</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Detailed Breakdown -->
        <div class="mt-5">
            <h3 class="section-title">Detailed Emission Breakdown</h3>
            
            <table class="table table-bordered emission-table">
                <thead>
                    <tr>
                        <th>Scope</th>
                        <th>Category</th>
                        <th>Sub-category</th>
                        <th>Emissions (kgCO2e)</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Scope 1 -->
                    <tr>
                        <td rowspan="5" class="table-danger">Scope 1</td>
                        <td>Stationary Combustion</td>
                        <td>Diesel</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope1.stationary_combustion.diesel) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope1.stationary_combustion.diesel/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr>
                        <td>Stationary Combustion</td>
                        <td>Petrol</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope1.stationary_combustion.petrol) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope1.stationary_combustion.petrol/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr>
                        <td>Mobile Combustion</td>
                        <td>Bus Fleet</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope1.mobile_combustion.bus_fleet) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope1.mobile_combustion.bus_fleet/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr>
                        <td>Fugitive Emissions</td>
                        <td>-</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope1.fugitive_emissions) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope1.fugitive_emissions/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr class="table-active">
                        <td colspan="3"><strong>Total Scope 1</strong></td>
                        <td><strong>{{ "{:,.0f}".format(report.emissions.totals.scope1) }}</strong></td>
                        <td><strong>{{ "%.1f"|format(report.emissions.totals.scope1/report.emissions.totals.total*100) }}%</strong></td>
                    </tr>
                    
                    <!-- Scope 2 -->
                    <tr>
                        <td rowspan="2" class="table-success">Scope 2</td>
                        <td>Purchased Electricity</td>
                        <td>Grid Power</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope2.purchased_electricity) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope2.purchased_electricity/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr class="table-active">
                        <td colspan="3"><strong>Total Scope 2</strong></td>
                        <td><strong>{{ "{:,.0f}".format(report.emissions.totals.scope2) }}</strong></td>
                        <td><strong>{{ "%.1f"|format(report.emissions.totals.scope2/report.emissions.totals.total*100) }}%</strong></td>
                    </tr>
                    
                    <!-- Scope 3 -->
                    <tr>
                        <td rowspan="5" class="table-info">Scope 3</td>
                        <td>Business Travel</td>
                        <td>Air Travel</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope3.business_travel.air) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope3.business_travel.air/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr>
                        <td>Employee Commuting</td>
                        <td>Bus</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope3.employee_commuting.bus) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope3.employee_commuting.bus/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr>
                        <td>Employee Commuting</td>
                        <td>Car</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope3.employee_commuting.car) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope3.employee_commuting.car/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr>
                        <td>Purchased Goods</td>
                        <td>-</td>
                        <td>{{ "{:,.0f}".format(report.emissions.scope3.purchased_goods) }}</td>
                        <td>{{ "%.1f"|format(report.emissions.scope3.purchased_goods/report.emissions.totals.total*100) }}%</td>
                    </tr>
                    <tr class="table-active">
                        <td colspan="3"><strong>Total Scope 3</strong></td>
                        <td><strong>{{ "{:,.0f}".format(report.emissions.totals.scope3) }}</strong></td>
                        <td><strong>{{ "%.1f"|format(report.emissions.totals.scope3/report.emissions.totals.total*100) }}%</strong></td>
                    </tr>
                    
                    <!-- Grand Total -->
                    <tr class="table-primary">
                        <td colspan="3"><h5>GRAND TOTAL</h5></td>
                        <td><h5>{{ "{:,.0f}".format(report.emissions.totals.total) }} kgCO2e</h5></td>
                        <td><h5>100%</h5></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Reduction Targets -->
        <div class="mt-5">
            <h3 class="section-title">Emission Reduction Targets</h3>
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5>Target Overview</h5>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item">
                                    Scope 1 Reduction: {{ report.reduction_targets.scope1*100 }}%
                                    <div class="progress mt-2">
                                        <div class="progress-bar bg-danger" style="width: 25%">Current Progress</div>
                                    </div>
                                </li>
                                <li class="list-group-item">
                                    Scope 2 Reduction: {{ report.reduction_targets.scope2*100 }}%
                                    <div class="progress mt-2">
                                        <div class="progress-bar bg-success" style="width: 40%">Current Progress</div>
                                    </div>
                                </li>
                                <li class="list-group-item">
                                    Scope 3 Reduction: {{ report.reduction_targets.scope3*100 }}%
                                    <div class="progress mt-2">
                                        <div class="progress-bar bg-info" style="width: 15%">Current Progress</div>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5>Recommended Actions</h5>
                            <ol>
                                <li>Transition bus fleet to CNG/LNG fuel</li>
                                <li>Install solar panels at depots and offices</li>
                                <li>Implement telecommuting policy for staff</li>
                                <li>Optimize route planning for fuel efficiency</li>
                                <li>Establish waste recycling program</li>
                            </ol>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-5 text-center">
            <hr>
            <p class="text-muted">This report was generated using LAMATA Carbon Emission Calculator Tool v1.0</p>
            <p>For questions or additional analysis, contact: sustainability@lamata.lagosstate.gov.ng</p>
            <button class="btn btn-primary" onclick="window.print()">Print Report</button>
            <button class="btn btn-success" onclick="downloadReport()">Download as PDF</button>
        </div>
    </div>

    <script>
        function downloadReport() {
            alert('Report download functionality would be implemented in production');
        }
    </script>
</body>
</html>
