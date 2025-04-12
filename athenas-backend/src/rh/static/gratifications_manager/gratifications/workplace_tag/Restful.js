
Ext._define('rh.gratifications_manager.gratifications.workplace_tag.Restful', {
    extend: 'core.Restful',

    resource: 'WorkplaceTag',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.workplace.WorkplaceConfigTagRestful.superclass.getFields.call(this, cfg).concat([
                {name: "icons", type: "auto" },
                {name: "start_validity",type: "date",dateFormat: "d/m/Y"},
                {name: "end_validity",type: "date",dateFormat: "d/m/Y"},
                {name: "deleted",type: "bool"},
                {name: "workplace",type: "int",useNull: true},
                {name: "workplace_unicode",type: "string"},
                {name: "tag",type: "string"},
                {name: "tag_display",type: "string"},
                {name: "unicode",type: "string"},
                {name: "evento_numero", type: "string"},
                {name: "servidor_id", type: "int"},
                {name: "periodo_ano", type: "string"},
                {name: "periodo_mes", type: "string"},
                {name: "calculate_days",type: "string",useNull: true},
            ]);

        return this._fields;
    }
});
