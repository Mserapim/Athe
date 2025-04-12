 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Grid.superclass.constructor.call(this, cfg);
        this.setFilterProperty('substitutions_consolidated__pk', cfg.consolidatedId);
    },

    hideActions: ['add','edit','remove', 'copy', 'edit'],

    configOrderToolBar: ['search','-'],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Substituto', dataIndex: 'servidor_unicode', id: 'autoExpandColumn'},
                    {header: 'Titularidade', dataIndex: 'titularidade', width: 200},
                    {header: 'Substituído', dataIndex: 'servidor_substituido_unicode', width: 200},
                    {header: 'Cumulativa', dataIndex: 'cumulativa', width: 200},
                    {header: 'Data Início', dataIndex: 'data_inicio', width: 100},
                    {header: 'Data Fim', dataIndex: 'data_fim', width: 100},
                    {header: 'Qtd Dias', dataIndex: 'qtd_dias', width: 70},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Restful',
    'rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Grid'
);
