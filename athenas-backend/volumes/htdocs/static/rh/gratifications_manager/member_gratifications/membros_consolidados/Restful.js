 Ext._define('rh.gratifications_manager.member_gratifications.membros_consolidados.Restful', {
    extend: 'core.Restful',

    resource: 'GMGratMembros',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.member_gratifications.membros_consolidados.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons", type: "auto"},
                {name: 'servidor_unicode', type: 'string'},
                {name: 'data_posse', type: 'datetime'},
                {name: 'data_exercicio', type: 'datetime'},
                {name: 'data_desligamento', type: 'datetime'},
                {name: 'data_ultimo_calculo', type: 'datetime'},
                {name: 'afastamento', type: 'string'},
                {name: 'cargo_efetivo', type: 'string'},
                {name: 'cargo_comissao', type: 'string'},
                {name: 'cargo_eletivo', type: 'string'},
            ]);

        return this._fields;
    }
});
