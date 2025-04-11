 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Grid.superclass.constructor.call(this, cfg);

        this.getStore().baseParams['exerc_cumul_perm_pk'] = cfg.exercCumulPermId;

        this.getStore().load();
    },

    hideActions: ['add','edit','remove', 'copy', 'edit'],

    configOrderToolBar: [],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: '', dataIndex: 'icons', width: 100, menuDisabled: true, renderer: toolkit.util.formatStatus },
                    {header: 'Servidor', dataIndex: 'servidor', id: 'autoExpandColumn'},
                    {header: 'Designação', dataIndex: 'designacao_unicode', width: 250},
                    {header: '%', dataIndex: 'pct', width: 50},
                    {header: 'De Substituição?', dataIndex: 'from_substitution', width: 100, renderer: toolkit.util.formatIconYesNo,},
                    {header: 'Base de Cálculo?', dataIndex: 'base_calculo', width: 100, renderer: toolkit.util.formatIconYesNo,},
                    {header: 'Data Vigência Início', dataIndex: 'data_vigencia_inicio', width: 110},
                    {header: 'Data Vigência Fim', dataIndex: 'data_vigencia_fim', width: 110},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Restful',
    'rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Grid'
);
