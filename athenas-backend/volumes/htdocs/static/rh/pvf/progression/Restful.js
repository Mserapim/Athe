Ext._define('rh.pvf.progression.Restful', {
    extend: 'core.Restful',

    resource: 'PVFRequestProgression',


    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.pvf.progression.Restful.superclass.getFields.call(this, cfg).concat([
                { name: "date",type: "date",dateFormat: "d/m/Y" },
                { name: "approver",type: "int",useNull: true },
                { name: "approver_unicode",type: "string" },
                { name: "status",type: "int",useNull: true },
                { name: "status_display", type: "string" },
                { name: "custom_approver_current",type:"string" },
                { name: "employee", type: "int", useNull: true },
                { name: "employee_unicode", type: "string" },
                { name: "type_of_request",type:"string" },
                { name: "type_of_usufruct_id",type:"int",useNull: true },
            ]);

        return this._fields;
    },

});
   