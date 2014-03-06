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
    var sql = generateSqlQuery(resource, params);
    $.when(
      recline.Backend.Ckan.fetch(resource),
      recline.Backend.Ckan.search_sql(sql, resource)
    ).done(function(fetch, query) {
      var fields = groupByFieldType(fetch.fields),
          config = plotConfig(fields, params),
          data = prepareDataForPlot(fields, query.hits, config.xaxis, config.yaxis, params);

      if (sortData) {
        data = sortData(data);
      }

      $.plot(elementId, data, config);
    });
  }

  function generateSqlQuery(resource, params) {
    var sql = "SELECT * FROM \""+resource.id+"\"",
        filters = {};

    if (params.filters) {
      $.each(params.filters, function (field, values) {
        filters['"' + field + '"'] = values;
      });

      var filtersSQL = $.map(filters, function (values, field) {
        return field + " IN ('" + values.join("','") + "')";
      });

      if (filtersSQL.length > 0) {
        sql += " WHERE " + filtersSQL.join(" AND ");
      }
    }

    var orderBy = Object.keys(filters).sort().map(function (filter) {
      return filter + " ASC";
    });
    if (params.horizontal) {
      orderBy.push("\"" + params.x_axis + "\" ASC");
    } else {
      orderBy.push("\"" + params.y_axis + "\" DESC");
    }

    sql += " ORDER BY " + orderBy.join(",");

    return sql;
  }

  function groupByFieldType(fields) {
    var result = {};
    $.each(fields, function (i, field) {
      result[field.id] = field.type;
    });
    return result;
  }

  function prepareDataForPlot(fields, records, xAxis, yAxis, params) {
    var grouppedData = convertAndGroupDataBySeries(fields, records, params),
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
      yaxis: axisConfigByType[yAxisType]
    };

    if (params.chart_type == "pie") {
      config = $.extend(config, {
        series: {
          pie: {
            show: true
          }
        },
        legend: {
          show: false
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

  function convertAndGroupDataBySeries(fields, records, params) {
    var result = {},
        xAxisParser = parsers[fields[params.x_axis]],
        yAxisParser = parsers[fields[params.y_axis]];
    $.each(records, function(i, record) {
      var y = record[params.y_axis],
          yParsed = yAxisParser(y),
          series = record[params.series] || '';

      if (y === null) {
        return;
      }

      if (params.x_axis) {
        var x = record[params.x_axis],
            xParsed = xAxisParser(x);

        if (x === null) {
          return;
        }
        result[series] = result[series] || [];
        result[series].push([xParsed, yParsed]);
      } else {
        result[series] = result[series] || 0;
        result[series] = result[series] + yParsed;
      }
    });
    return result;
  }
})(this.ckan.views.basiccharts, this.jQuery);
