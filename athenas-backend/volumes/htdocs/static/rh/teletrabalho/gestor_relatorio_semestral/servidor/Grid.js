/**
 *
 **/
Ext._define('rh.teletrabalho.gestor_relatorio_semestral.servidor.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.teletrabalho.gestor_relatorio_semestral.servidor.Window',

    keywordFieldMessage: 'Palavra-chave',

    hideItemsToolbar: ['add', 'edit', 'remove'],

    hideActions: ['copy', 'edit', 'remove'],

    configOrderToolBar: ['-', 'search', '->'],

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        var departament = cfg.departament;
        if (departament == undefined || departament == 'expediente')
            departament = 'rh';
        Ext.applyIf(cfg, {
            departament: departament,
            gridAutoLoad: true,

        });

        this.departament = cfg.departament;

        rh.teletrabalho.gestor_relatorio_semestral.servidor.Grid.superclass.constructor.call(this, cfg);

    },

   
    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Chave', dataIndex: 'servidor_pk', width: 55, hidden: true },
                    { header: 'Matrícula', dataIndex: 'matricula', width: 80, renderer: function (value) { return '<div style="text-align:right">' + value + '</div>'; } },
                    { header: 'Nome', dataIndex: 'nome', id: 'autoExpandColumn' },
                    { header: 'Tipo', dataIndex: 'tipo',width: 150, },
                    { header: 'Cod. Plano', dataIndex: 'pk',width: 150, },
                    { header: 'Data Inicio', dataIndex: 'data_inicio',width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    { header: 'Data Fim', dataIndex: 'data_fim',width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                ]
            );
        return this._columnModel;
    },


});

core.RestfulGrid.register(
    'rh.teletrabalho.gestor_relatorio_semestral.servidor.Restful',
    'rh.teletrabalho.gestor_relatorio_semestral.servidor.Grid'
);

