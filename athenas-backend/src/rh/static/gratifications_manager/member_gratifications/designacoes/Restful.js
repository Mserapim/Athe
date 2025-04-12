 Ext._define('rh.gratifications_manager.member_gratifications.designacoes.Restful', {
    extend: 'core.Restful',

    resource: 'GMDesignacoes',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.member_gratifications.designacoes.Restful.superclass.getFields.call(this, cfg).concat([
                { type: "auto", name: "icons" },
                { type: 'bool', name: 'from_substitution' },
                { type: 'date', name: 'data_vigencia_inicio', dateFormat: 'd/m/Y' },
                { type: 'date', name: 'data_vigencia_fim', dateFormat: 'd/m/Y' },
            ]);

        return this._fields;
    }
});
