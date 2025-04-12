 Ext._define('rh.gratifications_manager.member_gratifications.periodo.Restful', {
    extend: 'core.Restful',

    resource: 'GMPeriodoGratMembros',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.member_gratifications.periodo.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'ano', type: 'int'},
                {name: 'mes', type: 'string'},
                {name: 'periodo', type: 'string'},
                {name: 'data_ultimo_calculo', type: 'datetime'},
            ]);

        return this._fields;
    }
});
