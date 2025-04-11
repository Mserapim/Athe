Ext._define('corregedoria.cirdir.health.healtharea.Restful', {
  extend: 'core.Restful',
  resource: 'CIRDIRHealthArea',

    getFields: function(cfg) {
        if(!this._fields) {
          this._fields = corregedoria.cirdir.health.healtharea.Restful.superclass.getFields.call(this, cfg).concat([
            {name: "icons"},
            {type: "int", name: "person_id" },
            {type: "string", name: "employee_unicode"},
            {type: "string", name: "employee_type" },
            {type: "int", name: "year"},
            {type: "int", name: "previous_year"},
            {type: "bool", name: "closed_address"},
            {type: "bool", name: "closed_teaching_1st_semestry"},
            {type: "bool", name: "closed_teaching_2nd_semestry"},
            {type: "bool", name: "closed_property"},
            {type: "bool", name: "closed_debits"},
            {type: "bool", name: "closed_health"},
            {type: "bool", name: "check_address"},
            {type: "bool", name: "check_teaching"},
            {type: "bool", name: "check_property"},
            {type: "bool", name: "check_debits"},
            {type: "bool", name: "check_health"},

          ]);
        }
        return this._fields;
    },

});
