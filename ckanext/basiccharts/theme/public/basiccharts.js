this.ckan = this.ckan || {};
this.ckan.views = this.ckan.views || {};
this.ckan.views.basiccharts = this.ckan.views.basiccharts || {};

(function(self, $) {
  "use strict";

  var resource, params;
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
    resource = _resource;
    params = _params;
    initPlot(elementId, sortData);
  }

  function initPlot(elementId, sortData) {
    var sql = generateSqlQuery();
    $.when(
      recline.Backend.Ckan.fetch(resource),
      recline.Backend.Ckan.search_sql(sql, resource)
    ).done(function(fetch, query) {
      var fields = groupByFieldType(fetch.fields),
          config = plotConfig(fields),
          data = prepareDataForPlot(fields, query.hits, config.xaxis);

      if (sortData) {
        data = sortData(data);
      }

      $.plot(elementId, data, config);
    });
  }

  function generateSqlQuery() {
    var sql = "SELECT * FROM \""+resource.id+"\"",
        filters = params.filters;

    if (filters) {
      var filtersSQL = $.map(filters, function (values, field) {
        return field + " IN ('" + values.join("','") + "')";
      })
      if (filtersSQL.length > 0) {
        sql += " WHERE " + filtersSQL.join(" AND ");
      }
    }

    console.log(sql);
    return sql;
  }

  function groupByFieldType(fields) {
    var result = {};
    $.each(fields, function (i, field) {
      result[field.id] = field.type;
    });
    return result;
  }

  function prepareDataForPlot(fields, records, xAxis) {
    var grouppedData = convertAndGroupDataBySeries(fields, records),
        xAxisMode = xAxis && xAxis.mode,
        barWidth = (xAxisMode === "time") ? 60*60*24*30*1000 : 0.5,
        chartTypes = {
          lines: { show: true },
          bars: {
            show: true,
            align: "center",
            barWidth: barWidth
          }
        };

    return $.map(grouppedData, function(data, label) {
      var dataForPlot = {
        label: label,
        data: data
      }
      dataForPlot[params.chart_type] = chartTypes[params.chart_type];

      return dataForPlot;
    });
  }

  function plotConfig(fields) {
    var config,
        xAxisType = fields[params.x_axis],
        yAxisType = fields[params.y_axis],
        axisConfigByType = {
          timestamp: { mode: "time" },
          text: { mode: "categories" },
          numeric: {},
          integer: {}
        };

    config = {
      yaxis: axisConfigByType[yAxisType],
    }

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
          hoverable: true
        },
        tooltip: true,
        tooltipOpts: {
          content: "%s | "+params.x_axis+": %x | "+params.y_axis+": %y"
        }
      });
    }

    if (xAxisType) {
      config.xaxis = axisConfigByType[xAxisType];
    }

    return config;
  }

  function convertAndGroupDataBySeries(fields, records) {
    var result = {},
        xAxisParser = parsers[fields[params.x_axis]],
        yAxisParser = parsers[fields[params.y_axis]];
    $.each(records, function(i, record) {
      var y = yAxisParser(record[params.y_axis]),
          series = record[params.series];

      if (params.x_axis) {
        var x = xAxisParser(record[params.x_axis]);

        result[series] = result[series] || [];
        result[series].push([x, y]);
      } else {
        result[series] = result[series] || 0;
        result[series] = result[series] + y;
      }
    });
    return result;
  }
})(this.ckan.views.basiccharts, this.jQuery);
