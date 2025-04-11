Ext._define('planning.hiring.minuteitem.MinuteItemGridValidator', {
    extend: 'core.RestfulGrid',

    rest: 'planning.hiring.minuteitem.MinuteItemValidatorRestful',
    // restWindow: 'planning.hiring.minuteitem.MinuteItemWindow',

    configOrderToolBar: [],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'ATA', dataIndex: 'minute_unicode', width: 70 },
                    { header: 'Grupo/Item', dataIndex: 'group', width: 80, sortable: true },
                    { header: 'Linha', dataIndex: 'line', width: 50, sortable: true },
                    { header: 'Descrição', dataIndex: 'description_without_tags', id: 'autoExpandColumn' },
                    { header: 'Marca/Modelo', dataIndex: 'brand', width: 100 },
                    { header: 'Unid. de Medida', dataIndex: 'unit_measure_display' },
                    { header: 'Quantidade', dataIndex: 'quantity', width: 70, align: 'center' },
                    { header: 'Valor Unitário', dataIndex: 'unitary_value', width: 80, 'renderer': toolkit.util.formatCurrency },
                    { header: 'Valor Total', dataIndex: 'total_value', width: 80, 'renderer': toolkit.util.formatCurrency },
                ]
            );

        return this._columnModel;
    },

    getToolbar: function (cfg) {

        if (!this._toolbar) {
            cfg = core.nullValue(cfg, {});

            this._toolbar = planning.hiring.minuteitem.MinuteItemGridValidator.superclass.getToolbar.call(this, cfg);
        }

        return this._toolbar;
    },

    getTotalValueImportedItems: function () {
        if (!this._totalValueImportedItems) {
            this._totalValueImportedItems = Ext._create('Ext.Toolbar.TextItem', {
                text: 'Total: Não disponível',
                width: 200,
                style: {
                    'color': '#15428B',
                    'font-weight': 'bold'
                },
            });
        }

        return this._totalValueImportedItems;
    },

    getFooterbar: function (cfg) {
        if (!this._footerbar)
            this._footerbar = Ext._create('Ext.PagingToolbar', {
                style: cfg.footerStyle,
                store: this.getStore(),
                pageSize: 30,
                displayInfo: true,
                items: [
                    '-',
                    '->',
                    '-',
                    this.getTotalValueImportedItems(),
                ]
            });

        return this._footerbar;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            viewConfig: {
                scope: this,
                getRowClass: function (record) {
                    if (record.get('unitary_value') == null && record.get('line') == "") {
                        return 'x-grid3-yellow-simple';
                    }
                }
            }
        });

        planning.hiring.minuteitem.MinuteItemGridValidator.superclass.constructor.call(this, cfg);
    }

});

core.RestfulGrid.register(
    'planning.hiring.minuteitem.MinuteItemValidatorRestful',
    'planning.hiring.minuteitem.MinuteItemGridValidator'
);
