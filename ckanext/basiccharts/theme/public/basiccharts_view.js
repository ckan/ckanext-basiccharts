ckan.module("basiccharts_view", function (jQuery) {
  "use strict";

  function setupParams(defaultParams, chartType) {
    var routeParams = window.location.search.queryStringToJSON(),
        params = {
          chart_type: chartType,
          filters: setupFilters(defaultParams)
        };

    return $.extend({}, defaultParams, routeParams, params);
  }

  function setupFilters(defaultParams) {
    var defaultFilters = parseFilters(defaultParams),
        routeFilters = ckan.views.viewhelpers.filters.get();

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

  function initialize() {
    var endpoint = this.options.endpoint || this.sandbox.client.endpoint + "/api",
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
          orders,
          ordersLength;

      orders = Object.keys(params.filters).sort(function (a, b) {
        // The order is params.group_by -> params.x_axis -> params.y_axis ->
        // everything else, lexicographically sorted
        if (a === params.group_by) {
          return -1;
        } else if (a === params.x_axis) {
          return (b === params.group_by) ? 1 : -1;
        } else if (a === params.y_axis) {
          return (b === params.group_by || b === params.x_axis) ? 1 : -1;
        } else {
          return a.localeCompare(b);
        }
      });
      ordersLength = orders.length;

      data.sort(function (a, b) {
        for (var i = 0; i < ordersLength; i++) {
          var order = params.filters[orders[i]],
            result = order.indexOf(a[orders[i]]) - order.indexOf(b[orders[i]]);

          if (result !== 0) {
            return result;
          }
        }
        return 0;
      });

      return result;
    }

    ckan.views.basiccharts.init(elementId, resource, params, sortData);
  }

  return {
    initialize: initialize
  };
});
