/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export class SchoolDashboard extends Component {
    static template = "school_dashboard.Dashboard";

    setup() {
        this.state = useState({
            loading: true,
            kpis: {},
            studentStats: {
                gender: {},
                grade_distribution: [],
                new_admissions: 0
            },
            feeStats: {
                payment_status: {},
                overdue_amount: 0,
                overdue_count: 0
            },
            academicStats: {
                grade_distribution: {},
                average_percentage: 0,
                upcoming_exams: []
            },
            charts: {
                student_growth: [],
                fee_collection: [],
                attendance_trend: []
            },
            selectedPeriod: 'month',
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async loadDashboardData() {
        this.state.loading = true;
        try {
            const data = await rpc("/school/dashboard/data",{});
            this.state.kpis = data.kpis;
            this.state.studentStats = data.student_stats;
            this.state.feeStats = data.fee_stats;
            this.state.academicStats = data.academic_stats;
            this.state.charts = data.charts;
        } catch (error) {
            console.error("Error loading dashboard data:", error);
        } finally {
            this.state.loading = false;
        }
    }

    async refreshDashboard() {
        await this.loadDashboardData();
        this.renderCharts();
    }

    renderCharts() {
        // Render charts after data is loaded
        if (!this.state.loading && window.Chart) {
            // Small delay to ensure DOM is ready
            setTimeout(() => {
                this.renderStudentGrowthChart();
                this.renderGenderChart();
                this.renderGradeDistributionChart();
                this.renderFeeCollectionChart();
                this.renderPaymentStatusChart();
                this.renderAttendanceTrendChart();
                this.renderAcademicGradeChart();
            }, 100);
        }
    }

    renderStudentGrowthChart() {
        const canvas = document.getElementById('studentGrowthChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.charts.student_growth || [];

        // Destroy existing chart if any
        if (canvas.chart) {
            canvas.chart.destroy();
        }

        canvas.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.month),
                datasets: [{
                    label: 'Total Students',
                    data: data.map(d => d.count),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Student Growth Trend'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderGenderChart() {
        const canvas = document.getElementById('genderChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.studentStats.gender || {};

        if (canvas.chart) {
            canvas.chart.destroy();
        }

        canvas.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Male', 'Female'],
                datasets: [{
                    data: [data.male || 0, data.female || 0],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                    ],
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Gender Distribution'
                    }
                }
            }
        });
    }

    renderGradeDistributionChart() {
        const canvas = document.getElementById('gradeDistributionChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.studentStats.grade_distribution || [];

        if (canvas.chart) {
            canvas.chart.destroy();
        }

        canvas.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    label: 'Students',
                    data: data.map(d => d.count),
                    backgroundColor: 'rgba(153, 102, 255, 0.8)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Students by Grade'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderFeeCollectionChart() {
        const canvas = document.getElementById('feeCollectionChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.charts.fee_collection || [];

        if (canvas.chart) {
            canvas.chart.destroy();
        }

        canvas.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.grade),
                datasets: [
                    {
                        label: 'Collected',
                        data: data.map(d => d.collected),
                        backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    },
                    {
                        label: 'Pending',
                        data: data.map(d => d.pending),
                        backgroundColor: 'rgba(255, 159, 64, 0.8)',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Fee Collection by Grade'
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true
                    }
                }
            }
        });
    }

    renderPaymentStatusChart() {
        const canvas = document.getElementById('paymentStatusChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.feeStats.payment_status || {};

        if (canvas.chart) {
            canvas.chart.destroy();
        }

        canvas.chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Paid', 'Partial', 'Unpaid'],
                datasets: [{
                    data: [data.paid || 0, data.partial || 0, data.unpaid || 0],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Payment Status'
                    }
                }
            }
        });
    }

    renderAttendanceTrendChart() {
        const canvas = document.getElementById('attendanceTrendChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.charts.attendance_trend || [];

        if (canvas.chart) {
            canvas.chart.destroy();
        }

        canvas.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Attendance Rate %',
                    data: data.map(d => d.rate),
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.4,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Attendance Trend (Last 30 Days)'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    renderAcademicGradeChart() {
        const canvas = document.getElementById('academicGradeChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.academicStats.grade_distribution || {};

        if (canvas.chart) {
            canvas.chart.destroy();
        }

        canvas.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['A', 'B', 'C', 'D', 'F'],
                datasets: [{
                    label: 'Students',
                    data: [data.A || 0, data.B || 0, data.C || 0, data.D || 0, data.F || 0],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                    ],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Grade Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    openStudents() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Students',
            res_model: 'school.student',
            views: [[false, 'list'], [false, 'form']],
            domain: [['status', 'in', ['enrolled', 'active']]],
        });
    }

    openFees() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Student Fees',
            res_model: 'school.student.fee',
            views: [[false, 'list'], [false, 'form']],
        });
    }

    openOverdueFees() {
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Overdue Fees',
            res_model: 'school.student.fee',
            views: [[false, 'list'], [false, 'form']],
            domain: [['is_overdue', '=', true]],
        });
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(value || 0);
    }

    formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value || 0);
    }

    formatPercent(value) {
        return `${(value || 0).toFixed(1)}%`;
    }
}

registry.category("actions").add("school_dashboard.dashboard", SchoolDashboard);
