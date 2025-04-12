Ext._define('adm.contabilidade.budgetaryindicator.Restful', {
    extend: 'core.Restful',

    resource: 'ContabBudgetaryIndicator',

    getFields: function (cfg) {
        if (!this._fields) {
            this._fields = adm.contabilidade.budgetaryindicator.Restful.superclass.getFields.call(this, cfg).concat([
                { type: "string", name: "year" },
                { type: "string", name: "name" },
                { type: "string", name: "object_name" },
                { type: "string", name: "action_unicode" },
                { type: "string", name: "source_unicode" },
                { type: "int",    name: "source", useNull: true }, 
                { type: "int",    name: "action", useNull: true },
            ]);
        }

        return this._fields;
    }
});
