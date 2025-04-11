Ext._define('rh.dayoff.mpmt.usufruct.ConflictsGrid', {
    extend: 'Ext.grid.GridPanel',

    constructor: function (cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            autoExpandColumn: 'autoExpandId',
            store: this.getStore(cfg),
            columns: [
                { header: 'Id', dataIndex: 'pk', width: 50, hidden: true },
                { header: 'Origem', dataIndex: 'label_origin', width: 70 },
                { header: 'Servidor', dataIndex: 'employee', id: 'autoExpandId' },
                { header: 'Conflito', dataIndex: 'info', hidden: true },
                { header: 'Período', dataIndex: 'period_conflict', width: 180 },
                { header: 'Dias', dataIndex: 'days', width: 30 },
                { header: 'Criado em', dataIndex: 'created_at', width: 50, hidden: true },
                { header: 'Criado por', dataIndex: 'created_by', width: 50, hidden: true },
                { header: 'Ordem', dataIndex: 'order', width: 50 },
                { header: 'Local', dataIndex: 'workplace', width: 180 },
            ],
            bbar: Ext._create('Ext.PagingToolbar', {
                displayInfo: true,
                store: this.getStore(cfg),
            })
        });
        rh.dayoff.mpmt.usufruct.ConflictsGrid.superclass.constructor.call(this, cfg);
    },

    getStore: function (cfg) {
        if (!this._store) {
            this._store = Ext._create('Ext.data.Store', {
                autoLoad: true,
                msg: 'Carregando informações',
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('DAYOFFUsufructMPMT', 'get_conflicts'),
                    method: 'GET',
                    disableCaching: false
                }),
                baseParams: {
                    start: 0,
                    limit: 20,
                    usufructPk: cfg.usufruct.pk,
                },
                reader: Ext._create('Ext.data.JsonReader', {
                    root: 'collection',
                    totalProperty: 'count',
                    fields: [
                        { name: 'pk', type: 'int' }, // 'pk do objeto de origem',
                        { name: 'label_origin', type: 'string' }, // 'label de identificação da origem Férias',
                        { name: 'employee', type: 'string' }, // 'str do servidor de que conflitou',
                        { name: 'info', type: 'string' }, // 'mensagem de erro que será mostrada',
                        { name: 'period_conflict', type: 'string' }, // 'str descrevendo o período que conflitou',
                        { name: 'days', type: 'int' }, // 'quantidade de dias que conflitou',
                        { name: 'created_at', type: 'date' }, // 'quando foi criado',
                        { name: 'created_by', type: 'string' }, // 'quando foi criado',
                        { name: 'order', type: 'int' }, // 'ordem de substituição quando existir',
                        { name: 'workplace', type: 'string' }, // 'nome do local onde ocorreu o conflito',
                    ]
                })
            });
        }

        return this._store;
    }
});
