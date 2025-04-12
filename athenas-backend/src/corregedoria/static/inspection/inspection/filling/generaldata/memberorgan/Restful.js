Ext._define('corregedoria.inspection.inspection.filling.generaldata.memberorgan.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONMemberOrgan',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.generaldata.memberorgan.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "employee"},
                {type: "string", name: "employee_unicode"},
                {type: "int", name: "member_role"},
                {type: "string", name: "member_role_display"},
                {type: "bool", name: "exclusive"},
                {type: "bool", name: "needs_exclusivity"},
                {type: "string", name: "justify"},
                {type: "string", name: "observation"},
            ]);

        return this._fields;
    }
});
