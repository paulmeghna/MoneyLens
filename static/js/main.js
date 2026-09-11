// MoneyLens main JavaScript


/* ============================================================
   Expense Category Chart
   ============================================================ */

const expenseCategoryDataElement = document.getElementById(
    "expense-category-data"
);

const expenseCategoryCanvas = document.getElementById(
    "expenseCategoryChart"
);


if (
    expenseCategoryDataElement &&
    expenseCategoryCanvas
) {
    const categoryData = JSON.parse(
        expenseCategoryDataElement.textContent
    );

    if (categoryData.length > 0) {

        const categoryLabels = categoryData.map(
            item => item.label
        );

        const categoryAmounts = categoryData.map(
            item => item.amount
        );

        new Chart(
            expenseCategoryCanvas,
            {
                type: "doughnut",

                data: {
                    labels: categoryLabels,

                    datasets: [
                        {
                            label: "Expenses",
                            data: categoryAmounts
                        }
                    ]
                },

                options: {
                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            position: "bottom",

                            labels: {
                                usePointStyle: true,
                                padding: 16
                            }
                        },

                        tooltip: {
                            callbacks: {
                                label: function (context) {

                                    const label = context.label || "";
                                    const value = context.parsed || 0;

                                    return `${label}: ₹${value.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2
                                        }
                                    )}`;
                                }
                            }
                        }
                    }
                }
            }
        );
    }
}


/* ============================================================
   Income vs Expense Chart
   ============================================================ */

const incomeExpenseDataElement = document.getElementById(
    "income-expense-data"
);

const incomeExpenseCanvas = document.getElementById(
    "incomeExpenseChart"
);


if (
    incomeExpenseDataElement &&
    incomeExpenseCanvas
) {
    const chartData = JSON.parse(
        incomeExpenseDataElement.textContent
    );

    if (chartData.length > 0) {

        const monthNames = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ];

        const labels = chartData.map(
            item => monthNames[item.month - 1]
        );

        const incomeData = chartData.map(
            item => item.income
        );

        const expenseData = chartData.map(
            item => item.expense
        );

        new Chart(
            incomeExpenseCanvas,
            {
                type: "bar",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label: "Income",
                            data: incomeData
                        },

                        {
                            label: "Expense",
                            data: expenseData
                        }
                    ]
                },

                options: {
                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },

                    plugins: {
                        legend: {
                            position: "bottom"
                        },

                        tooltip: {
                            callbacks: {
                                label: function (context) {

                                    const label = context.dataset.label || "";
                                    const value = context.parsed.y || 0;

                                    return `${label}: ₹${value.toLocaleString(
                                        "en-IN",
                                        {
                                            minimumFractionDigits: 2,
                                            maximumFractionDigits: 2
                                        }
                                    )}`;
                                }
                            }
                        }
                    }
                }
            }
        );
    }
}


/* ============================================================
   Monthly Savings Rate Chart
   ============================================================ */

const savingsRateCanvas = document.getElementById(
    "savingsRateChart"
);

if (
    incomeExpenseDataElement &&
    savingsRateCanvas
) {
    const chartData = JSON.parse(
        incomeExpenseDataElement.textContent
    );

    if (chartData.length > 0) {

        const monthNames = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ];

        const labels = chartData.map(
            item => monthNames[item.month - 1]
        );

        const savingsRateData = chartData.map(
        item => item.savings_rate
    );

    console.table([...chartData]);

        new Chart(
            savingsRateCanvas,
            {
                type: "line",

                data: {
                    labels: labels,

                    datasets: [ 
                        {
                            label: "Savings Rate",
                            data: savingsRateData,

                            tension: 0.3,

                            fill: false
                        }
                    ]
                },

                options: {
                    responsive: true,

                    maintainAspectRatio: false,

                    scales: {
                        y: {
                            suggestedMin: -100,
                            suggestedMax: 100,

                            ticks: {
                                callback: function (value) {
                                    return value + "%";
                                }
                            }
                        }
                    },

                    plugins: {
                        legend: {
                            position: "bottom",

                            labels: {
                                color: "#222",
                                font: {
                                    size: 14,
                                    weight: "600"
                                },
                                padding: 16
                            }
                        },

                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return `Savings Rate: ${context.parsed.y.toFixed(2)}%`;
                                }
                            }
                        }
                    }
                }
            }
        );
    }
}