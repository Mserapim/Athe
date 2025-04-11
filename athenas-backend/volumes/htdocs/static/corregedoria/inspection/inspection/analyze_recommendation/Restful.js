Ext._define('corregedoria.inspection.inspection.analyze_recommendation.Restful', {
  extend: 'core.Restful',
  resource: 'INSPECTIONFollowRecommendationCorregedoria',

    getFields: function(cfg) {
        if(!this._fields) {
          this._fields = corregedoria.inspection.inspection.analyze_recommendation.Restful.superclass.getFields.call(this, cfg).concat([
              {name: "icons"},
              {type: "string", name: "recommendation"},
              {type: "string", name: "deadline_grid"},
              {type: "auto", name: "inspection"},
              {type: "bool", name: "delayoftime"},
              {type: "bool", name: "delayoftime_pending"},
              {type: "bool", name: "reportcompliance_pending"},
              {type: "bool", name: "delayoftime_editing"},
              {type: "bool", name: "reportcompliance_editing"},
          ]);
        }
        return this._fields;
    },

});
