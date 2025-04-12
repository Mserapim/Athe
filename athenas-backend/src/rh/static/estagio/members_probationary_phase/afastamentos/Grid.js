 Ext._define('estagio.members_probationary_phase.afastamentos.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'estagio.members_probationary_phase.afastamentos.Restful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        estagio.members_probationary_phase.afastamentos.Grid.superclass.constructor.call(this, cfg);
       
        this.getStore().baseParams['membroId'] = cfg.membroId;
        this.getStore().load();
        this.setParam('membroId', cfg.membroId);

    },

    hideActions: ['add','edit','remove', 'copy', 'edit', 'search'],

    configOrderToolBar: [''],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true, id: 'autoExpandColumn'},
                    // // {header: '', dataIndex: 'icons', width: 30, menuDisabled: true, renderer: toolkit.util.formatStatus },

                    { header: 'Descrição', dataIndex: 'unicode', width: 400, hidden: true },
                    { header: 'Membro', dataIndex: 'servidor_unicode', width: 300 },
                    { header: 'Afastamento', dataIndex: 'situation_unicode', width: 250 },
                    { header: 'tipo', dataIndex: 'tipo', width: 150 },
                    {
                        header: 'Início',
                        dataIndex: 'data_inicio',
                        width: 100,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y'),
                        sortable: true
                    },
                    {
                        header: 'Fim',
                        dataIndex: 'data_fim',
                        width: 100,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y'),
                        sortable: true
                    },
                    { header: 'Qtd. dias', dataIndex: 'qtd_dias', width: 100, },

                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'estagio.members_probationary_phase.afastamentos.Restful',
    'estagio.members_probationary_phase.afastamentos.Grid'
);
