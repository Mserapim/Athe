Ext._define('standard.emailtemplate.Restful', {
    extend: 'core.Restful',

    resource: 'STDEmailTemplate',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = standard.emailtemplate.Restful.superclass.getFields.call(this, cfg).concat([
                { name: 'pk', type: "int" },
                { name: "code", type: "string" },
                { name: "subject", type: "string" },
                { name: "contents", type: "string" },
                { name: "description", type: "string" }
            ]);

        return this._fields;
    }
});
