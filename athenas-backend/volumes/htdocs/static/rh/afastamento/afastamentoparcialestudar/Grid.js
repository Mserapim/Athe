Ext._define('rh.afastamento.afastamentoparcialestudar.Grid', {
    extend: 'rh.afastamento.afastamento.Grid',
    restWindow: 'rh.afastamento.afastamentoparcialestudar.Window',

    constructor: function(cfg) {
        rh.afastamento.afastamentoparcialestudar.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModelItems: function(){
        if(!this._columnModelItems){
            this._columnModelItems = rh.afastamento.afastamentoparcialestudar.Grid.superclass.getColumnModelItems.call(
                this, {});
            this._columnModelItems = this._columnModelItems.concat([
                {header: 'Instituição', dataIndex: 'instituicao_unicode', width: 120, hidden: false},
                {header: 'Curso', dataIndex: 'curso_unicode', width: 120, hidden: false},
                {header: 'Localidade', dataIndex: 'localidade_unicode', width: 120, hidden: false}]);
        }
        return this._columnModelItems;
    }
});

core.RestfulGrid.register(
    'rh.afastamento.afastamentoparcialestudar.Restful',
    'rh.afastamento.afastamentoparcialestudar.Grid'
);

