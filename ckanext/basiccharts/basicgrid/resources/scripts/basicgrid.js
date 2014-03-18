ckan.module("basicgrid-multiselect", function (jQuery) {
  "use strict";

  function initialize() {
    var self = this;

    self.el.select2({"data":self.options.fields, multiple:true, width:"element"});

    self.el.select2("container").find("ul.select2-choices").sortable({
        containment: "parent",
        start: function() { self.el.select2("onSortStart"); },
        update: function() { self.el.select2("onSortEnd"); }
    });
  }

  return {
    initialize: initialize,
    options: {"fields": false},
  };
});
