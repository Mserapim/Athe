
Ext._define('planning.hiring.agreementaction.Restful', {
    extend: 'core.Restful',

    resource: 'PHAAgreementAction',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.agreementaction.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "unicode"
                },
                {
                    type: "string",
                    name: "data_acao"
                },
                {
                    type: "string",
                    name: "observacao"
                }
                // {
                //     type: "object",
                //     name: "actions_list"
                // },
            ]);

        return this._fields;
    }
});
