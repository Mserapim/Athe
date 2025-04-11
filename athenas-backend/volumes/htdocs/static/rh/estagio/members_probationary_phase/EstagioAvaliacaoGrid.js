Ext._define('estagio.members_probationary_phase.EstagioAvaliacaoGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'estagio.members_probationary_phase.EstagioAvaliacaoWindow',

    hideItemsToolbar: ['add','edit', 'remove'],

    configOrderToolBar: ['search', '-', '->', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Matricula', dataIndex: 'matricula',id: 'autoExpandColumn'},
                    {header: 'Nome', dataIndex: 'name', width: 200 },
                    {header: 'Cargo', dataIndex: 'job_role', width: 200},
                    {header: 'Primeira Posse', dataIndex: 'first_possession_date', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Data Exercício', dataIndex: 'exercise_date', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Dias Trabalhados', dataIndex: 'worked_days', width: 70},
                    {header: 'Dias Afastados', dataIndex: 'absence_days', width: 70},
                    {header: 'Data Final do Estágio Probatório', dataIndex: 'complete_phase_date', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Dias para o Estágio Probatório', dataIndex: 'days_for_complete_phase', width: 70},
                    {header: 'Lotacao', dataIndex: 'workplace', width: 150},
                ]
            );

        return this._columnModel;
    },

    getAfastamentosWindow: function() {
        var selected = this.getSelected();
        if(selected) {
            Ext._create('estagio.members_probationary_phase.WindowAfastamento', {
                values: {
                    membroId:selected.id
                },
            }).show();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                allowRemove: false,
                doubleClickHandler: function() { this.getAfastamentosWindow(); },
            }
        );

        estagio.members_probationary_phase.EstagioAvaliacaoGrid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'estagio.members_probationary_phase.EstagioAvaliacaoRestful',
    'estagio.members_probationary_phase.EstagioAvaliacaoGrid'
);


Ext._define('estagio.members_probationary_phase.WindowAfastamento', {
    extend: 'Ext.Window',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Afastamentos',
                closable: true,
                resizable: false,
                border: false,
                height: 630,
                items: [
                    new estagio.members_probationary_phase.AfastamentosTabPanel({}, cfg.values.membroId),
                ],
            }
        );

        estagio.members_probationary_phase.WindowAfastamento.superclass.constructor.call(this, cfg);
    },
});

Ext._define('estagio.members_probationary_phase.AfastamentosTabPanel', {
    extend: 'Ext.Panel',

    constructor: function (cfg, membroId) {
        cfg = core.nullValue(cfg, {});

        var afastamentosGridPanel = Ext._create(
            'estagio.members_probationary_phase.afastamentos.Grid',
            {
                height: 600,
                gridAutoLoad: true,
                border: false,
                membroId: membroId,
            }
        );

        Ext.applyIf(
            cfg,
            {
                items: [afastamentosGridPanel],

            }
        );
    
        estagio.members_probationary_phase.AfastamentosTabPanel.superclass.constructor.call(this, cfg);

    }
});