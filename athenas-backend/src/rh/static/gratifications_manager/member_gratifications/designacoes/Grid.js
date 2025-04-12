 Ext._define('rh.gratifications_manager.member_gratifications.designacoes.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.member_gratifications.designacoes.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        rh.gratifications_manager.member_gratifications.designacoes.Grid.superclass.constructor.call(this, cfg);

        this.setFilterProperty('pk', cfg.gratMembroId);
    },

    hideActions: ['add','edit','remove', 'copy', 'edit', 'search'],

    configOrderToolBar: [''],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true, id: 'autoExpandColumn'},
                    // {header: '', dataIndex: 'icons', width: 30, menuDisabled: true, renderer: toolkit.util.formatStatus },

                    { header: 'Descrição', dataIndex: 'unicode', width: 400, },
                    { header: 'De Substituição', dataIndex: 'from_substitution', width: 100, renderer: toolkit.util.formatIconYesNo},
                    {
                        header: 'Início',
                        dataIndex: 'data_vigencia_inicio',
                        width: 100,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y'),
                        sortable: true
                    },
                    {
                        header: 'Fim',
                        dataIndex: 'data_vigencia_fim',
                        width: 100,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y'),
                        sortable: true
                    },
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gratifications_manager.member_gratifications.designacoes.Restful',
    'rh.gratifications_manager.member_gratifications.designacoes.Grid'
);
