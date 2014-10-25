this.ckan = this.ckan || {};
this.ckan.views = this.ckan.views || {};
this.ckan.views.basiccharts = this.ckan.views.basiccharts || {};

(function(self, $) {
  "use strict";

  var parsers = {
        integer: parseInt,
        numeric: parseFloat,
        text: function (x) {
          return x;
        },
        timestamp: function (x) {
          return new Date(x).getTime();
        }
      };

  self.init = function init(elementId, _resource, _params, sortData) {
    initPlot(elementId, sortData, _resource, _params);
  };

  function initPlot(elementId, sortData, resource, params) {
    var queryParams = generateQueryParams(resource, params);

    $.when(
      recline.Backend.Ckan.fetch(resource),
      recline.Backend.Ckan.query(queryParams, resource)
    ).done(function(fetch, query) {
      var fields = groupByFieldType(fetch.fields),
          config = plotConfig(fields, params),
          hits = query.hits,
          data;

      if (sortData) {
        hits = sortData(hits);
        if (params.chart_type == "pie") {
          hits.reverse();
        }
      }

      data = prepareDataForPlot(fields, hits, config.xaxis, config.yaxis, params);

      $.plot(elementId, data, config);
    });
  }

  function generateQueryParams(resource, params) {
    var query = {
      filters: [],
      sort: [],
      size: 1000
    };

    if (params.filters) {
      query.filters = $.map(params.filters, function (values, field) {
        return {
          type: "term",
          field: field,
          term: values
        };
      });
    }

    if (params.horizontal) {
      query.sort = [{ field: params.x_axis, order: "ASC" }];
    } else {
      query.sort = [{ field: params.y_axis, order: "DESC" }];
    }

    return query;
  }

  function groupByFieldType(fields) {
    var result = {};
    $.each(fields, function (i, field) {
      result[field.id] = field.type;
    });
    return result;
  }

  function prepareDataForPlot(fields, records, xAxis, yAxis, params) {
    var grouppedData = convertAndGroup(fields, records, params),
        xAxisMode = xAxis && xAxis.mode,
        yAxisMode = yAxis.mode,
        areWePlottingTime = (yAxisMode === "time" || xAxisMode === "time"),
        barWidth = areWePlottingTime ? 60*60*24*30*1000 : 0.5,
        chartTypes = {
          lines: { show: true },
          bars: {
            show: true,
            horizontal: params.horizontal,
            align: "center",
            barWidth: barWidth
          }
        };

    return $.map(grouppedData, function(data, label) {
      var dataForPlot = {
        label: label,
        data: data
      };
      dataForPlot[params.chart_type] = chartTypes[params.chart_type];

      return dataForPlot;
    });
  }

  function plotConfig(fields, params) {
    var config,
        xAxisType = fields[params.x_axis],
        yAxisType = fields[params.y_axis],
        axisConfigByType = {
          timestamp: { mode: "time" },
          text: {
            mode: "categories",
            tickColor: "rgba(0, 0, 0, 0)",
            tickFormatter: function (value, axis) {
              return value;
            }
          },
          numeric: {},
          integer: {}
        };

    config = {
      yaxis: axisConfigByType[yAxisType],
      colors: ['#e41a1c', '#377eb8', '#4daf4a',
               '#984ea3', '#ff7f00', '#ffff33',
               '#a65628', '#f781bf', '#999999']
    };

    if (params.chart_type == "pie") {
      config = $.extend(config, {
        series: {
          pie: {
            show: true,
            label: {
              show: true,
              threshold: 0.05
            }
          }
        },
        legend: {
          show: params.show_legends
        },
        grid: {
          hoverable: true
        },
        tooltip: true,
        tooltipOpts: {
          content: "%p.0%, %s"
        }
      });
    } else {
      config = $.extend(config, {
        grid: {
          hoverable: true,
          borderWidth: 0
        },
        legend: {
          show: params.show_legends
        },
        tooltip: true,
        tooltipOpts: {
          content: "%s | "+params.x_axis+": %x | "+params.y_axis+": %y",
          xDateFormat: "%d/%m/%Y",
          yDateFormat: "%d/%m/%Y"
        }
      });
    }

    if (xAxisType) {
      config.xaxis = axisConfigByType[xAxisType];
    }

    return config;
  }

  function convertAndGroup(fields, records, params) {
    var result = {},
        xAxisParser = parsers[fields[params.x_axis]],
        yAxisParser = parsers[fields[params.y_axis]];
    $.each(records, function(i, record) {
      var y = record[params.y_axis],
          yParsed = yAxisParser(y),
          group_by = record[params.group_by] || '';

      if (y === null) {
        return;
      }

      if (params.x_axis) {
        var x = record[params.x_axis],
            xParsed = xAxisParser(x);

        if (x === null) {
          return;
        }
        result[group_by] = result[group_by] || [];
        result[group_by].push([xParsed, yParsed]);
      } else {
        result[group_by] = result[group_by] || 0;
        result[group_by] = result[group_by] + yParsed;
      }
    });
    return result;
  }
})(this.ckan.views.basiccharts, this.jQuery);
