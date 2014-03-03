ckan.module("basiccharts_view", function (jQuery) {
  "use strict";

  function setupParams(defaultParams, chartType) {
    var routeParams = window.location.search.queryStringToJSON(),
        params = {
          chart_type: chartType,
          filters: setupFilters(defaultParams, routeParams)
        };

    return $.extend({}, defaultParams, routeParams, params);
  }

  function setupFilters(defaultParams, routeParams) {
    var defaultFilters = parseFilters(defaultParams),
        routeFilters = parseRouteFilters(routeParams);

    return $.extend({}, defaultFilters, routeFilters);
  }

  function parseFilters(params) {
    var filters = {};

    if (!params.filter_values) {
      return filters;
    }

    $.each(params.filter_values, function (i, value) {
      var field = params.filter_fields[i];
      if (value === "") {
        return;
      }
      filters[field] = filters[field] || [];
      filters[field].push(value);
    });

    return filters;
  }

  function parseRouteFilters(routeParams) {
    // The filters are in format "field:value|field:value|field:value"
    if (!routeParams || !routeParams.filters) {
      return {};
    }
    var filters = {},
        fieldValuesStr = routeParams.filters.split("|");

    $.each(fieldValuesStr, function (i, fieldValueStr) {
      var fieldValue = fieldValueStr.split(":"),
          field = fieldValue[0],
          value = fieldValue[1];

      filters[field] = filters[field] || [];
      filters[field].push(value);
    });

    return filters;
  }

  function initialize() {
    var endpoint = this.options.endpoint || window.location.origin + "/api",
        chartType = this.options.chartType,
        resourceView = this.options.resourceView,
        params = setupParams(resourceView, chartType),
        elementId = "#"+this.el.context.id,
        resource = {
          id: this.options.resourceId,
          endpoint: endpoint
        };

    function sortData(data) {
      var result = data,
          seriesOrder = params.filters[params.series],
          xAxisOrder = params.filters[params.x_axis];

      // Order legends
      if (seriesOrder) {
        result.sort(function (a, b) {
          return seriesOrder.indexOf(a.label) - seriesOrder.indexOf(b.label);
        });
      }

      // Order x axis
      if (params.x_axis) {
        if (xAxisOrder === undefined) {
          xAxisOrder = $.map(result[0].data, function (d) {
            return d[0];
          });
        }

        $.each(result, function (i, element) {
          element.data.sort(function (a, b) {
            return xAxisOrder.indexOf(a[0]) - xAxisOrder.indexOf(b[0]);
          });
        });
      }

      return result;
    }

    ckan.views.basiccharts.init(elementId, resource, params, sortData);
  }

  return {
    initialize: initialize
  };
});
