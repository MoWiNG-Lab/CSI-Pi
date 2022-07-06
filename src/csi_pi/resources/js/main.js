var app = null;
window.onload = () => {
    app = new Vue({
        el: '#app',
        data() {
            return {
                device_loaded: "",
                devices: {},
                cameras: {},
                data_rates: {},
                annotations_data: "",
                server_stats: {
                    data_directory: '',
                    is_csi_enabled: true,
                    tty_plugins: [],
                    storage: {
                        'used': 0,
                        'total': 0,
                    }
                },
                notes: "",
                device_list: [],
            }
        },
        methods: {
            reload() {
                self = this
                function load_device_metrics() {
                    self.device_list.forEach(device_name => {
                        axios.get("/device-metrics?device_name=" + device_name)
                            .then(response => {
                                if (response.data.status === 'OK') {
                                    self.devices[device_name] = response.data;
                                }
                            });
                    })
                }

                function load_annotation_metrics() {
                    axios.get("/annotation-metrics")
                        .then(response => {
                            self.annotations_data = response.data.data;
                        });
                }

                function load_server_stats() {
                    axios.get("/server-stats")
                        .then(response => {
                            if (self.server_stats.data_directory !== response.data.data_directory) {
                                self.notes = response.data.notes;
                            }
                            self.server_stats = response.data;
                            new_device_list = response.data.devices;

                            // Remove disconnected devices
                            Object.keys(self.devices).forEach(k => {
                                if (new_device_list.indexOf(k) === -1) {
                                    delete self.devices[k]
                                }
                            })

                            // Add newly connected devices
                            self.device_list = new_device_list;
                        });
                }

                setInterval(load_device_metrics, 1000)
                setInterval(load_annotation_metrics, 1000)
                setInterval(load_server_stats, 1000)
            },
            format_file_size(size) {
                if (size > 1e9) {
                    return (size / 1e9).toFixed(1) + " GBs"
                }
                if (size > 1e6) {
                    return (size / 1e6).toFixed(1) + " MBs"
                }
                return (size / 1e3).toFixed(1) + " kBs"
            },
            chart_options(has_error) {
                return {
                    chart: {
                        id: 'realtime',
                        fontFamily: 'monospace',
                        height: 150,
                        type: 'line',
                        animations: {
                            enabled: false,
                        },
                        toolbar: {
                            show: false
                        },
                        zoom: {
                            enabled: false
                        }
                    },
                    dataLabels: {
                        enabled: false
                    },
                    grid: {
                        borderColor: has_error ? '#333333' : '#eeeeee',
                    },
                    stroke: {
                        curve: 'smooth',
                        colors: [
                            has_error ? '#FFFFFF': '#000000'
                        ],
                        width: 1,
                    },
                    xaxis: {
                        axisBorder: {
                            show: false
                        },
                        axisTicks: {
                            show: false
                        },
                        labels: {
                            show: false
                        },
                        range: 60,
                    },
                    yaxis: {
                        title: {
                            text: 'Data Rate (Hz)',
                            style: {
                                color: has_error ? '#FFFFFF': '#000000',
                            }
                        },
                        labels: {
                            style: {
                                colors: [
                                    has_error ? '#FFFFFF': '#000000'
                                ],
                                fontWeight: 100
                            }
                        }
                    },
                    legend: {
                        show: false
                    },
                }
            },
            device_has_error(device) {
                return !this.server_stats.is_csi_enabled;
            },
            video_start(){
                let cam_number = 0
                axios.post("/cam/start?camera_number=" + cam_number)
                    .then(response => {
                        if (response.data.status === 'OK') {
                            self.cameras[cam_number] = response.data;
                        }
                    });
            },
            video_end(){
                let cam_number = 0
                axios.post("/cam/end?camera_number=" + cam_number)
                    .then(response => {
                        if (response.data.status === 'OK') {
                            self.cameras[cam_number] = response.data;
                        }
                    });
            },
        },
        mounted() {
            this.reload()
        },
        watch: {
            notes: _.debounce(function(value) {
                axios({
                    method: "post",
                    url: '/notes',
                    data: {
                        'note': value,
                    },
                })
            }, 500),
        }
    });

    Vue.component('apexchart', VueApexCharts)
}