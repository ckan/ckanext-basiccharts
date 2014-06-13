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
          filtersKeys = Object.keys(params.filters).sort(),
          filtersKeysLength = filtersKeys.length;

      data.sort(function (a, b) {
        // Sort by params' filters
        for (var i = 0; i < filtersKeysLength; i++) {
          var filtersValues = params.filters[filtersKeys[i]],
              aFilterIndex = filtersValues.indexOf(a[filtersKeys[i]]),
              bFilterIndex = filtersValues.indexOf(b[filtersKeys[i]]),
              result = aFilterIndex - bFilterIndex;

          if (result !== 0) {
            return result;
          }
        }

        // Sort by groupBy
        if (params.group_by) {
          var aGroupBy = a[params.group_by],
              bGroupBy = b[params.group_by],
              result = aGroupBy.localeCompare(bGroupBy);

          if (result !== 0) {
            return result;
          }
        }

        // Sort by xAxis or yAxis (depending if it's horizontal or vertical)
        var axis = (params.horizontal) ? params.x_axis : params.y_axis;
        var aValue = parseFloat(a[axis]),
            bValue = parseFloat(b[axis]);
        if (isNaN(aValue) || isNaN(bValue)) {
          return 0;
        } else {
          return aValue - bValue;
        }
      });

      return result;
    }

    ckan.views.basiccharts.init(elementId, resource, params, sortData);
  }

  return {
    initialize: initialize
  };
});
