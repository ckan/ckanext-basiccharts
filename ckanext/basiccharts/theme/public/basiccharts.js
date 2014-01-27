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

  self.init = function init(elementId, _resource, _params) {
    resource = _resource;
    params = _params;
    initPlot(elementId);
  }

  function initPlot(elementId) {
    var sql = generateSqlQuery();
    $.when(
      recline.Backend.Ckan.fetch(resource),
      recline.Backend.Ckan.search_sql(sql, resource)
    ).done(function(fetch, query) {
      var fields = groupByFieldType(fetch.fields),
          config = plotConfig(fields),
          data = prepareDataForPlot(fields, query.hits, config.xaxis.mode);
      $.plot(elementId, data, config);
    });
  }

  function generateSqlQuery() {
    var sql = "SELECT * FROM \""+resource.id+"\"",
        filterField = params.filter_field,
        filterValue = params.filter_value;

    if (filterField && filterValue) {
      sql += " WHERE "+filterField+" = '"+filterValue+"'";
    }

    return sql;
  }

  function groupByFieldType(fields) {
    var result = {};
    $.each(fields, function (i, field) {
      result[field.id] = field.type;
    });
    return result;
  }

  function prepareDataForPlot(fields, records, xAxisMode) {
    var grouppedData = convertAndGroupDataBySeries(fields, records),
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
        data: data,
      }
      dataForPlot[params.chart_type] = chartTypes[params.chart_type];

      return dataForPlot;
    });
  }

  function plotConfig(fields) {
    var config = {},
        xAxisType = fields[params.x_axis],
        yAxisType = fields[params.y_axis],
        axisConfigByType = {
          timestamp: { mode: "time" },
          text: { mode: "categories" },
          numeric: {},
          integer: {}
        };

    config.xaxis = axisConfigByType[xAxisType];
    config.yaxis = axisConfigByType[yAxisType];

    return config;
  }

  function convertAndGroupDataBySeries(fields, records) {
    var result = {};
    $.each(records, function(i, record) {
      var x = parsers[fields[params.x_axis]](record[params.x_axis]),
          y = parsers[fields[params.y_axis]](record[params.y_axis]),
          series = record[params.series];

      result[series] = result[series] || []
      result[series].push([x, y])
    });
    return result;
  }
})(this.ckan.views.basiccharts, this.jQuery);
