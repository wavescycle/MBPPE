import {CH_NAMES} from "../config/config.json";
import {getData, getPSD, getFrequency, getTimeFrequency} from "./api";

class myChart {
    // Constants
    containLabel = false;
    seriesType = "row";
    smooth = false;
    endValue = 800; //400
    fs = 200;
    custom_tooltips = {
        show: true,
        position: "inside",
        formatter: function (param) {
            return "<div>" + param.title + "</div>";
        },
        textStyle: {
            fontSize: 12,
        },
        extraCssText: "box-shadow: 0 0 3px rgba(0, 0, 0, 0.3);",
    };

    // init
    constructor(chart) {
        this.chart = chart;
        // this.filename = filename;
        // this.channels = channels;
        // this.data = data;
        // this.preData = preData;
        // this.gridHeight = chart.getHeight() * 0.15;
        this.gridHeight = 50;
    }

    _change_data(cutOff, diff) {
        const newChannels = this.channels.map((e) => {
            if (e === cutOff) return e;
            else return e + diff;
        });
        this.lineChart(this.filename, this.preData, newChannels);
    }

    _initChart(option, data) {
        this.chart.showLoading();
        if (data.status === 200) {
            option.dataset.source = data.data;
            this.chart.setOption(option, {
                notMerge: true,
            });
        } else {
            this.errorChart(data.data);
        }
        this.chart.hideLoading();
    }

    // save image to lcoal
    _toolbox_image_save() {
        return {
            show: true,
            showTitle: false,
            feature: {
                saveAsImage: {
                    title: "SAVE",
                },
            },
            tooltip: this.custom_tooltips,
            top: 30,
            itemGap: 30,
            itemSize: 20,
        };
    }

    // graph change, line, PSD
    _toolbox_graph_change() {
        const config = {
            show: true,
            showTitle: false,
            x: "center",
            top: 30,
            itemGap: 20,
            feature: {
                my_line: {
                    show: true,
                    title: "LINE",
                    icon: "path://M25.6 537.1392a25.6 25.6 0 1 1 0-51.2h141.1072a25.6 25.6 0 0 0 24.5248-18.2272l118.1184-393.7792a51.2 51.2 0 0 1 98.0992 0L665.6 934.4l118.1184-393.728a76.8 76.8 0 0 1 73.5744-54.784H998.4a25.6 25.6 0 1 1 0 51.2h-141.1072a25.6 25.6 0 0 0-24.5248 18.2272l-118.1184 393.7792a51.2 51.2 0 0 1-98.0992 0L358.4 88.6272 240.2816 482.4064a76.8 76.8 0 0 1-73.5744 54.784H25.6z",
                    onclick: () => {
                        this.lineChart(this.filename, this.preData, this.channels);
                    },
                },
                my_psd: {
                    show: true,
                    title: "PSD",
                    icon: "path://M901.3 357.4c-21.3-50.3-51.7-95.5-90.5-134.3-38.8-38.8-84-69.3-134.3-90.5C624.4 110.5 569 99.4 512 99.4s-112.4 11.2-164.5 33.2c-50.3 21.3-95.5 51.7-134.3 90.5-38.8 38.8-69.3 84-90.5 134.3-22 52.1-33.2 107.4-33.2 164.5s11.2 112.4 33.2 164.5c21.3 50.3 51.7 95.5 90.5 134.3 38.8 38.8 84 69.3 134.3 90.5 52.1 22 107.4 33.2 164.5 33.2s112.4-11.2 164.5-33.2c50.3-21.3 95.5-51.7 134.3-90.5 38.8-38.8 69.3-84 90.5-134.3 22-52.1 33.2-107.4 33.2-164.5s-11.2-112.4-33.2-164.5zM512 144.4c208.2 0 377.5 169.3 377.5 377.5 0 3.5-0.1 7-0.1 10.5h-58.9c-17.8 0-33.4-9.9-33.4-21.2v-106c0-14.3-7.4-28-20.2-37.6-11.7-8.8-27.1-13.6-43.2-13.6s-31.5 4.8-43.2 13.6c-12.8 9.6-20.2 23.3-20.2 37.6v242.9c0 11.3-15.6 21.2-33.4 21.2h-10.2c-17.8 0-33.4-9.9-33.4-21.2V284.2c0-14.3-7.4-28-20.2-37.6-11.7-8.8-27.1-13.6-43.2-13.6h-16.3c-16.2 0-31.5 4.8-43.2 13.6-12.8 9.6-20.2 23.3-20.2 37.6v434.3c0 11.3-15.6 21.2-33.4 21.2H397c-17.8 0-33.4-9.9-33.4-21.2V355.2c0-14.3-7.4-28-20.2-37.6-11.7-8.8-27.1-13.6-43.2-13.6h-9.7c-16.2 0-31.5 4.8-43.2 13.6-12.8 9.6-20.2 23.3-20.2 37.6v156c0 11.3-15.6 21.2-33.4 21.2h-58.9c-0.1-3.5-0.1-7-0.1-10.5-0.2-208.2 169.1-377.5 377.3-377.5z m0 755c-194.5 0-355-147.8-375.3-337h56.9c16.2 0 31.5-4.8 43.2-13.6 12.8-9.6 20.2-23.3 20.2-37.6v-156c0-11.3 15.6-21.2 33.4-21.2h9.7c17.8 0 33.4 9.9 33.4 21.2v363.4c0 14.3 7.4 28 20.2 37.6 11.7 8.8 27.1 13.6 43.2 13.6h19.4c16.2 0 31.5-4.8 43.2-13.6 12.8-9.6 20.2-23.3 20.2-37.6V284.2c0-11.3 15.6-21.2 33.4-21.2h16.3c17.8 0 33.4 9.9 33.4 21.2V648c0 14.3 7.4 28 20.2 37.6 11.7 8.8 27.1 13.6 43.2 13.6h10.2c16.2 0 31.5-4.8 43.2-13.6 12.8-9.6 20.2-23.3 20.2-37.6V405.2c0-11.3 15.6-21.2 33.4-21.2 17.8 0 33.4 9.9 33.4 21.2v106c0 14.3 7.4 28 20.2 37.6 11.7 8.8 27.1 13.6 43.2 13.6h56.9c-19.9 189.2-180.4 337-374.9 337z",
                    // iconStyle: { color: "red" },
                    onclick: () => {
                        this.psdChart(this.filename, this.preData);
                    },
                },
            },
            itemSize: 20,
            right: 10,
            tooltip: this.custom_tooltips,
        };
        return config;
    }

    // data change, up and down
    _toolbox_data_change() {
        return {
            show: true,
            showTitle: false,
            y: "center",
            orient: "vertical",
            itemGap: 30,
            itemSize: 20,
            feature: {
                my_up: {
                    show: true,
                    title: "Pre",
                    icon: "path://M573.056 272l308.8 404.608A76.8 76.8 0 0 1 820.736 800H203.232a76.8 76.8 0 0 1-61.056-123.392L450.976 272a76.8 76.8 0 0 1 122.08 0z",
                    onclick: () => {
                        this._change_data(0, -1);
                    },
                },
                my_down: {
                    show: true,
                    title: "Next",
                    icon: "path://M573.056 752l308.8-404.608A76.8 76.8 0 0 0 820.736 224H203.232a76.8 76.8 0 0 0-61.056 123.392l308.8 404.608a76.8 76.8 0 0 0 122.08 0z",
                    onclick: () => {
                        this._change_data(61, 1);
                    },
                },
            },
            tooltip: this.custom_tooltips,
        };
    }

    _toolbox_data_change_time_freq() {
        return {
            show: true,
            showTitle: false,
            y: "center",
            orient: "vertical",
            itemGap: 30,
            itemSize: 20,
            feature: {
                my_up: {
                    show: true,
                    title: "Pre",
                    icon: "path://M573.056 272l308.8 404.608A76.8 76.8 0 0 1 820.736 800H203.232a76.8 76.8 0 0 1-61.056-123.392L450.976 272a76.8 76.8 0 0 1 122.08 0z",
                    onclick: () => {
                        this.start -= 10;
                        this.end -= 10;
                        this.timeFreqChart(this.filename, this.preData, this.channels, this.start, this.end);
                    },
                },
                my_down: {
                    show: true,
                    title: "Next",
                    icon: "path://M573.056 752l308.8-404.608A76.8 76.8 0 0 0 820.736 224H203.232a76.8 76.8 0 0 0-61.056 123.392l308.8 404.608a76.8 76.8 0 0 0 122.08 0z",
                    onclick: () => {
                        this.start += 10;
                        this.end += 10;
                        this.timeFreqChart(this.filename, this.preData, this.channels, this.start, this.end);
                    },
                },
            },
            tooltip: this.custom_tooltips,
        };
    }

    // sample chart
    emptyChart(text = "No Data", color = "grey") {
        const op = {
            title: {
                show: true,
                textStyle: {
                    color: color,
                    fontSize: 20,
                },
                text: text,
                left: "center",
                top: "center",
            },
            xAxis: {
                show: false,
            },
            yAxis: {
                show: false,
            },
            series: [],
        };
        this.chart.setOption(op, {
            notMerge: true,
        });
        return true;
    }

    errorChart(text = "Unexpect Error") {
        this.emptyChart(text, "red");
    }

    // common line chart
    async lineChart(filename, preData, channels) {
        this.chart.showLoading();
        this.filename = filename;
        this.channels = channels;
        this.preData = preData;

        let data = await getData(filename, channels, preData, {need_axis: true});

        if (data.status === 200) {
            const op = {
                title: {
                    left: "center",
                    text: "EEG line figure",
                },
                grid: channels.map((e, i) => {
                    return {
                        top: this.gridHeight * (i + 1),
                        containLabel: this.containLabel,
                        height: this.gridHeight,
                    };
                }),
                // darkMode: true,
                // backgroundColor: "#000",
                // X axis
                xAxis: channels.map((e, i) => {
                    const isShow = i === channels.length - 1;
                    return {
                        show: isShow,
                        type: "category",
                        name: "Time [s]",
                        nameGap: 35,
                        nameLocation: "center",
                        gridIndex: i,
                        axisLine: {show: false},
                        axisLabel: {interval: this.fs - 1},
                    };
                }),
                // Y axis
                yAxis: channels.map((e, i) => {
                    return {
                        name: CH_NAMES[e],
                        nameLocation: "center",
                        nameGap: 10,
                        nameRotate: 0,
                        axisLine: {
                            show: false,
                        },
                        axisLabel: {
                            show: false,
                        },
                        gridIndex: i,
                    };
                }),
                // scaling
                dataZoom: [
                    {
                        type: "inside",
                        zoomOnMouseWheel: true,
                        endValue: this.endValue,
                        xAxisIndex: channels.map((e, i) => i),
                    },
                ],
                // tooltip: {
                //   trigger: "axis"
                // },
                axisPointer: {
                    link: {xAxisIndex: "all"},
                    label: {
                        backgroundColor: "#777",
                    },
                },
                tooltip: {
                    trigger: "axis",
                    position: function (pos, params, el, elRect, size) {
                        var obj = {top: 40};
                        obj[["left", "right"][+(pos[0] < size.viewSize[0] / 2)]] = 100;
                        return obj;
                    },
                    formatter: function (params) {
                        const info = params.map((e, i) => {
                            return {seriesName: e.seriesName, value: e.value[++i]};
                        });
                        info.sort((a, b) => b.value - a.value);
                        // console.log(info)
                        return `<div>Point ${params[0].dataIndex}<br/
            <p style="margin: 15px 0;padding: 0;">
            ${info
                            .map((e, i) => {
                                return `<span style="display:inline-block;width:50px">${e.seriesName}</span> <span>${e.value.toFixed(6)}</span>`;
                            })
                            .join("<br />")}
            <p/>
            </div>
            `;
                    },
                    order: 'valueDesc'
                },
                toolbox: [
                    // save image to local
                    this._toolbox_image_save(),
                    // button to change graph type
                    // this._toolbox_graph_change(),
                    // button to change data
                    this._toolbox_data_change(),
                ],
                dataset: {
                    source: data.data,
                    sourceHeader: false,
                },
                series: channels.map((e, i) => {
                    return {
                        type: "line",
                        name: CH_NAMES[e],
                        color: "black",
                        showSymbol: false,
                        smooth: this.smooth,
                        seriesLayoutBy: this.seriesType,
                        lineStyle: {width: 1},
                        xAxisIndex: i,
                        yAxisIndex: i,
                    };
                }),
            };
            this.chart.setOption(op, {
                notMerge: true,
            });
        } else {
            const errorData = data.data
            let error
            try {
                error = JSON.parse(errorData).message;
            } catch (e) {
                error = errorData
            }
            this.errorChart(error);
        }
        this.chart.hideLoading();
    }

    // PSD chart
    async psdChart(filename, preData) {
        this.chart.showLoading();
        const channels = CH_NAMES;
        const data = await getPSD(filename, preData, {need_axis: true});
        if (data.status === 200) {
            const op = {
                title: {
                    left: "center",
                    text: "EEG PSD figure",
                },
                legend: {
                    type: "scroll",
                    orient: "vertical",
                    right: 20,
                    top: 30,
                    bottom: 30,
                    data: channels,
                },
                // tooltip: {
                //   trigger: "axis",
                //   confine: true,
                // },
                // X axis
                xAxis: {
                    name: "Frequency [Hz]",
                    nameLocation: "center",
                    nameGap: 30,
                    type: "category",
                    axisLabel: {
                        interval: (index, value) => value % 1 === 0,
                    },
                },
                // Y axis
                yAxis: {
                    name: "PSD",
                    nameLocation: "center",
                    nameGap: 30,
                },
                toolbox: [
                    // save image to local
                    this._toolbox_image_save(),
                    // button to change graph type
                    // this._toolbox_graph_change(),
                ],
                dataset: {
                    source: data.data,
                    sourceHeader: false,
                },
                series: channels.map((e) => {
                    return {
                        type: "line",
                        name: e,
                        showSymbol: false,
                        smooth: this.smooth,
                        seriesLayoutBy: this.seriesType,
                        lineStyle: {width: 1},
                        emphasis: {focus: "series"},
                    };
                }),
            };
            this.chart.setOption(op, {
                notMerge: true,
            });
        } else {
            console.log(data.data)
            this.errorChart(data.data);
        }
        this.chart.hideLoading();
    }

    async freqChart(filename, preData, channels, start = 0, end = 10) {
        this.chart.showLoading();
        this.filename = filename;
        this.channels = channels;
        this.preData = preData;
        this.start = start;
        this.end = end;
        const colors = ["#83be82", "#e99c9d", "#6f6fe3", "#f18ef1", "#dc855f"]
        let data = await getFrequency(filename, channels, preData, {need_axis: true});
        const freqList = ["Delta", "Theta", "Alpha", "Beta", "Gamma"];
        if (data.status === 200) {
            const op = {
                tooltip: {
                    trigger: "axis",
                    position: function (point, params, dom, rect, size) {
                        // 返回 [x, y] 坐标的数组，这里你可以根据图表的大小返回一个固定的坐标值
                        return [size.viewSize[0] - 90, point[1]];
                    },
                    formatter: function (params) {
                        const info = params.map((e, i) => {
                            return {seriesName: e.seriesName, value: e.value[++i]};
                        });

                        return `<div>Point ${params[0].dataIndex}
                                <p style="margin: 15px 0;padding: 0;">
                                    ${info.map((e, i) => {
                            return `<span style="display:inline-block;width:60px;color:${colors[i]}">
                                        ${e.seriesName}
                                    </span>
                                    <span style="color:${colors[i]}">${e.value.toFixed(3)}</span>`;
                        })
                            .join("<br />")}
                                <p/>
                                </div>
                                `;
                    },
                },
                toolbox: [
                    // save image to local
                    this._toolbox_image_save(),
                    // button to change graph type
                    // this._toolbox_graph_change(),
                    // button to change data
                ],
                axisPointer: {
                    link: {xAxisIndex: "all"},
                },
                dataZoom: [
                    {
                        type: "inside",
                        zoomOnMouseWheel: true,
                        endValue: this.endValue,
                        xAxisIndex: freqList.map((e, i) => i),
                    },
                ],
                grid: freqList.map((e, i) => {
                    return {
                        top: this.gridHeight * (i + 1),
                        containLabel: this.containLabel,
                        height: this.gridHeight,
                    };
                }),
                xAxis: freqList.map((e, i) => {
                    const isShow = i === 4;
                    return {
                        type: "category",
                        show: isShow,
                        name: "Time [s]",
                        nameLocation: "center",
                        nameGap: 35,
                        gridIndex: i,
                        axisLine: {show: false},
                        axisLabel: {interval: this.fs - 1},
                    };
                }),
                yAxis: freqList.map((e, i) => {
                    return {
                        name: e,
                        gridIndex: i,
                        // name: "Frequency [Hz]",
                        nameLocation: "center",
                        nameRotate: 0,
                        nameGap: 15,
                        axisLine: {
                            show: false,
                        },
                        axisLabel: {
                            show: false,
                            interval: (index, value) => value % 1 === 0,
                        },
                        splitLine: {
                            show: false
                        },
                    };
                }),
                dataset: {
                    source: data.data,
                    sourceHeader: false,
                },
                series: freqList.map((e, i) => {
                    return {
                        type: "line",
                        name: e,
                        color: colors[i],
                        showSymbol: false,
                        smooth: this.smooth,
                        seriesLayoutBy: this.seriesType,
                        xAxisIndex: i,
                        yAxisIndex: i,
                    };
                }),
            };
            console.log(op);
            this.chart.setOption(op, {
                notMerge: true,
            });
        } else {
            this.errorChart(data.data);
        }
        this.chart.hideLoading();
    }

    async timeFreqChart(filename, preData, channels, start = 0, end = 10) {
        this.chart.showLoading();
        this.filename = filename;
        this.channels = channels;
        this.preData = preData;
        this.start = start;
        this.end = end;
        let data = await getTimeFrequency(filename, channels, preData, {start, end});
        if (data.status === 200) {
            const maxvalue = data.headers.maxvalue;
            const op = {
                tooltip: {
                    formatter: (params) => {
                        const value = params.value;
                        return `time: ${value[0].toFixed(1)} s<br/>
                    hz: ${value[1]}<br/>
                    data:${value[2].toFixed(2)}`;
                    },
                },
                toolbox: [
                    // save image to local
                    this._toolbox_image_save(),
                    // button to change graph type
                    // this._toolbox_graph_change(),
                    // button to change data
                    this._toolbox_data_change_time_freq(),
                ],
                xAxis: {
                    type: "category",
                    name: "Time [s]",
                    nameLocation: "center",
                    nameGap: 35,
                    axisLabel: {
                        interval: (index, value) => {
                            return value % 1 === 0;
                        },
                    },
                },
                yAxis: {
                    type: "category",
                    name: "Frequency [Hz]",
                    nameLocation: "center",
                    nameGap: 35,
                    // axisLabel: {
                    //   interval: (index, value) => {
                    //     console.log(value);
                    //     value % 10 === 0;
                    //   },
                    // },
                },
                visualMap: {
                    // type: "piecewise",
                    align: "left",
                    right: 45,
                    bottom: 65,
                    itemWidth: 14,
                    maxOpen: true,
                    max: Math.floor(maxvalue / 7) * 7,
                    // splitNumber: 7,
                    calculable: true,
                    // realtime: false,
                    // splitNumber: 10,
                    precision: 0,
                    inRange: {
                        color: [
                            "#313695",
                            "#4575b4",
                            "#74add1",
                            "#abd9e9",
                            "#e0f3f8",
                            "#ffffbf",
                            "#fee090",
                            "#fdae61",
                            "#f46d43",
                            "#d73027",
                            "#a50026",
                        ],
                    },
                },
                dataset: {
                    source: data.data,
                },
                series: [
                    {
                        type: "heatmap",
                        emphasis: {
                            itemStyle: {
                                borderColor: "#333",
                                borderWidth: 1,
                            },
                        },
                        smooth: true,
                        progressive: 0,
                        animation: false,
                    },
                ],
            };
            this.chart.setOption(op, {
                notMerge: true,
            });
        } else {
            this.errorChart(data.data);
        }
        this.chart.hideLoading();
    }
}

export default myChart;
