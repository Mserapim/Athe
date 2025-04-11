Ext._define('rh.gfp.conference.massmanagementfunds.folhaevento.Restful', {
    extend: 'core.Restful',

    resource: 'GFPConferenceFolhaEvento',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.conference.massmanagementfunds.folhaevento.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "folha", useNull: true},
                {type: "string", name: "folha_unicode"},
                {type: "int", name: "servidor", useNull: true},
                {type: "string", name: "servidor_unicode"},
                {type: "float",  name: "correct_valor",  useNull: true},
            ]);

        return this._fields;
    }
});
