ckan.module("basiccharts_filters_form", function (jQuery) {
  "use strict";

  function initialize() {
    var templateFilterInputs = this.options.templateFilterInputs;
    console.log(this.options);

    $('.formFilters-addFilter').click(function (evt) {
      evt.preventDefault();
      $(".formFilters").append($(templateFilterInputs));
    });

    $(document).on('click', '.formFilters-removeFilter', function (evt) {
      evt.preventDefault();
      $(this).parent().remove();
    });
  }

  return {
    initialize: initialize
  };
});
