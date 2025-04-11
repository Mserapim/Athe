Ext._define('planning.hiring.ride.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'planning.hiring.ride.Window',
    configOrderToolBar: ['add', 'edit', 'remove', '-', 'report', '-', 'search'],

    getColumnModel: function() {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel', [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Número', dataIndex: 'number', sortable: true, width: 120 },
                    { header: 'Ata', dataIndex: 'minute_unicode', sortable: true, width: 100 },
                    { header: 'Pessoa', dataIndex: 'person_unicode', sortable: true, width: 400 },
                    { header: 'Solicitação', dataIndex: 'asking', sortable: true, width: 100 },
                    { header: 'Data Solicitação', dataIndex: 'agreement_date', sortable: true, menuDisabled: true, width: 100 },
                    { header: 'Data da Autorização', dataIndex: 'authorization_date', sortable: true, menuDisabled: true, width: 120 },
                    { header: 'Número do Despacho', dataIndex: 'dispatch_number', sortable: true, menuDisabled: true, id: 'autoExpandColumn' },
                ]
            );

        return this._columnModel;
    },


    getReportAction: function () {
        if (!this._reportAction)
            this._reportAction = Ext._create('Ext.Button',{
                text: 'Relatórios',
                iconCls: 'icon-agree icon-agree-application-pdf',
                scope: this,
                menu: [
                    {
                        text: 'Adesão',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.ride.ReportAccession').show();
                        }
                    },
                    {
                        text: 'Saldo Adesões por Ata',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.ride.ReportMembershipBalanceMinute').show();
                        }
                    },
                    {
                        text: 'Listagem de Adesões por Ata',
                        scope: this,
                        iconCls: 'icon-agree icon-agree-application-pdf',
                        handler: function () {
                            Ext._create('planning.hiring.ride.ReportListMinuteAdhesion').show();
                        }
                    },
                ]
            });

        return this._reportAction;
    },


    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            columnAction: false,
        });

        planning.hiring.ride.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'planning.hiring.ride.Restful',
    'planning.hiring.ride.Grid'
);
