this.ckan = this.ckan || {};
this.ckan.views = this.ckan.views || {};
this.ckan.views.basiccharts = this.ckan.views.basiccharts || {};

(function(self, $) {
  var resource, resourceView;
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

  self.init = function init(elementId, _resource, _resourceView) {
    resource = _resource;
    resourceView = _resourceView;
    initPlot(elementId);
  }

  function initPlot(elementId) {
    var sql = generateSqlQuery();
    $.when(
      recline.Backend.Ckan.fetch(resource),
      recline.Backend.Ckan.search_sql(sql, resource)
    ).done(function(fetch, query) {
      var fields = groupByFieldType(fetch.fields),
          data = prepareDataForPlot(fields, query.hits),
          config = plotConfig(fields);
      $.plot(elementId, data, config);
    });
  }

  function generateSqlQuery() {
    var sql = "SELECT * FROM \""+resource.id+"\"",
        filterField = resourceView.filter_field,
        filterValue = resourceView.filter_value;

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

  function prepareDataForPlot(fields, records) {
    var grouppedData = convertAndGroupDataBySeries(fields, records),
        chartTypes = {
          lines: { show: true },
          bars: {
            show: true,
            barWidth: 60*60*24*30*1000 // 1 month
          }
        };

    return $.map(grouppedData, function(data, label) {
      var dataForPlot = {
        label: label,
        data: data,
      }
      dataForPlot[resourceView.chart_type] = chartTypes[resourceView.chart_type];

      return dataForPlot;
    });
  }

  function plotConfig(fields) {
    var config = {},
        xAxisType = fields[resourceView.x_axis],
        yAxisType = fields[resourceView.y_axis];

    if (xAxisType === "timestamp") {
      config.xaxis = { mode: "time" }
    }
    if (yAxisType === "timestamp") {
      config.yaxis = { mode: "time" }
    }
    return config;
  }

  function convertAndGroupDataBySeries(fields, records) {
    var result = {};
    $.each(records, function(i, record) {
      var x = parsers[fields[resourceView.x_axis]](record[resourceView.x_axis]),
          y = parsers[fields[resourceView.y_axis]](record[resourceView.y_axis]),
          series = record[resourceView.series];

      result[series] = result[series] || []
      result[series].push([x, y])
    });
    return result;
  }
})(this.ckan.views.basiccharts, this.jQuery);
