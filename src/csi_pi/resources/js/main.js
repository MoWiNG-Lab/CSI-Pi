var app = null;
window.onload = () => {
    app = new Vue({
        el: '#app',
        data() {
            return {
                device_loaded: "",
                devices: {},
                cameras: {},
                camera_images: {},
                camera_videos: {},
                video_timer_span: "",
                video_action_prompt: "Start Recording Video",
                video_timer_start: null,
                photo_burst_span: "",
                photo_burst_action_prompt: "Start Photo Burst",
                photo_burst_start_time: null,
                photo_file: "",
                video_file: "",
                is_video_to_download: false,
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

                function load_camera_images() {
                    axios.get("/photo/burst/newest")
                        .then(response => {
                            self.camera_images = response.data.most_recent
                        });
                }

                function load_camera_videos() {
                    axios.get("/video/newest")
                        .then(response => {
                            self.camera_videos = response.data.most_recent
                        });
                }

                function eval_video_timer() {
                    /* region: Video-timer */
                    if (self.video_timer_start == null) {
                        self.video_action_prompt = "Start Recording New Video";
                        if (self.video_file.length > 1) {
                            self.is_video_to_download = true;
                            self.video_timer_span = "Last Recorded Video: " + self.video_file.substring(self.video_file.lastIndexOf('/') + 1);
                        } else {
                            self.is_video_to_download = false;
                            self.video_timer_span = "";
                        }
                    } else {
                        self.video_action_prompt = "End Video Recording";
                        self.is_video_to_download = false;
                        const secs = (new Date().getTime() - self.video_timer_start.getTime()) / 1000;
                        self.video_timer_span = "Recording Duration = "
                            + Math.floor(secs / 60.0) + ":" + Math.floor(secs % 60);
                    }
                    /* endregion: Video-timer */

                    // region: Photo-Burst texts
                    if (self.photo_burst_start_time == null) {
                        self.photo_burst_action_prompt = "Start Photo Burst";
                        if (self.photo_file.length > 1)
                            self.photo_burst_span = "Last Photo-Burst Session's First Photo: " + self.photo_file;
                        else
                            self.photo_burst_span = "";
                    } else {
                        self.photo_burst_action_prompt = "End Photo Burst";
                        if (self.photo_file.length > 1)
                            self.photo_burst_span = "A new photo-burst started at " + self.photo_burst_start_time
                                + " with initial photo at " + self.photo_file + ".";
                        else
                            self.photo_burst_span = "A new photo-burst started at " + self.photo_burst_start_time;
                    }
                    // endregion: Photo-Burst texts
                }

                setInterval(load_device_metrics, 1000)
                setInterval(load_annotation_metrics, 1000)
                setInterval(load_server_stats, 1000)
                setInterval(load_camera_images, 1000)
                setInterval(load_camera_videos, 1000)
                setInterval(eval_video_timer, 1000)
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
                            has_error ? '#FFFFFF' : '#000000'
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
                                color: has_error ? '#FFFFFF' : '#000000',
                            }
                        },
                        labels: {
                            style: {
                                colors: [
                                    has_error ? '#FFFFFF' : '#000000'
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
            video_start_end() {
                function video_start() {
                    let cam_number = 0
                    axios.post("/video/start?camera_number=" + cam_number)
                        .then(response => {
                            if (response.data.status === 'OK') {
                                self.cameras[cam_number] = response.data;
                                self.video_file = response.data.file;
                                self.video_timer_start = new Date();
                            }
                        });
                }

                function video_end() {
                    let cam_number = 0
                    axios.post("/video/end?camera_number=" + cam_number)
                        .then(response => {
                            if (response.data.status === 'OK') {
                                self.cameras[cam_number] = response.data;
                                self.video_timer_start = null;
                            }
                        });
                }

                if (self.video_timer_start == null)
                    video_start();
                else video_end();
            },
            photo_burst_start_end() {
                function pb_start() {
                    let cam_number = 0
                    axios.post("/photo/burst/start?camera_number=" + cam_number)
                        .then(response => {
                            if (response.data.status === 'OK') {
                                self.cameras[cam_number] = response.data;
                                self.photo_burst_start_time = new Date();
                                self.photo_file = response.data.file;
                            }
                        });
                }

                function pb_end() {
                    let cam_number = 0
                    axios.post("/photo/burst/end?camera_number=" + cam_number)
                        .then(response => {
                            if (response.data.status === 'OK') {
                                self.cameras[cam_number] = response.data;
                                self.photo_burst_start_time = null;
                            }
                        });
                }

                if (self.photo_burst_start_time == null)
                    pb_start();
                else pb_end();
            },
            video_download() {
                let cam_number = 0;
                const host = window.location.protocol + "//" + window.location.host;
                window.open(host + '/video/download?camera_number=' + cam_number, '_blank');
            }
        },
        mounted() {
            this.reload()
        },
        watch: {
            notes: _.debounce(function (value) {
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