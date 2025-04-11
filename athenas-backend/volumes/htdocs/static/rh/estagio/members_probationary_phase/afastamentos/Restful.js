 Ext._define('estagio.members_probationary_phase.afastamentos.Restful', {
    extend: 'core.Restful',

    resource: 'MembroProbatorioAfastamentosRESTFUL',

    getFields: function(cfg) {

        if(!this._fields)
            this._fields = estagio.members_probationary_phase.afastamentos.Restful.superclass.getFields.call(this, cfg).concat([
                // { type: "auto", name: "icons" },
                { type: 'string', name: 'tipo' },
                { type: 'string', name: 'servidor_unicode' },
                { type: 'string', name: 'situation_unicode' },
                { type: 'date', name: 'data_inicio', dateFormat: 'd/m/Y' },
                { type: 'date', name: 'data_fim', dateFormat: 'd/m/Y' },
                { type: 'int', name: 'qtd_dias'},
            ]);

        return this._fields;
    }
});
