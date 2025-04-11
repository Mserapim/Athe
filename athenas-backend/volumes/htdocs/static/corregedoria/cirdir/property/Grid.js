Ext._define('corregedoria.cirdir.property.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.property.Window',
    rest: 'corregedoria.cirdir.property.Restful',

    configOrderToolBar: ['add', 'edit', 'remove', 'history', '->','emptySubmit','-', '-', 'submit', ],

    mixins: {'1': 'corregedoria.cirdir.ActionsMixin'},

    getHistoryAction: function(cfg) {
        if(!this._historyAction){
            this._historyAction = new Ext.Button({
                xtype: 'button',
                text: ' Histórico',
                iconCls: 'icon-crgmpe icon-crgmpe-list',
                handler: function() {
                    Ext._create('corregedoria.cirdir.HistoryWindow', {
                        params: {
                          controlinformation: cfg.params.controlinformation,
                          criteria_key: 3,
                        },
                    }).show();
                }
            });
        }
        return this._historyAction;
    },

    getEmptySubmitAction: function(cfg) {
        if(!this._emptySubmitAction) {
            this._emptySubmitAction = new Ext.Button({
                xtype: 'button',
                text: 'Não possuo Bens e Direitos',
                iconCls: 'icon-core icon-core-document-arrow',
                disabled: cfg.params.closed_property,
                scope: this,
                handler: function() {
                    this.execSubmit(cfg, true);
                }
            });
        }
        return this._emptySubmitAction;
    },

    getSubmitAction: function(cfg) {
        if(!this._submitAction){
            this._submitAction = new Ext.Button({
                xtype: 'button',
                text: ' Submeter Bens e Direitos',
                iconCls: 'icon-crgmpe icon-crgmpe-success',
                disabled: cfg.params.closed_property,
                scope: this,
                handler: function() {
                    this.execSubmit(cfg, false);
                }
            });
        }
        return this._submitAction;
    },

    execSubmit: function(cfg, empty) {
        this.submit({
            alertTitle: 'Submetendo dados de Bens e Direitos',
            params: {
                controlinformation: cfg.params.controlinformation,
                criteria: 'property',
                emptySubmit: empty
            }
        });
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 30, renderer: core.rendererIconGrid},
                    {header: 'Descrição', dataIndex: 'description', id: 'autoExpandColumn', },
                    {header: 'Valor', dataIndex: 'current_value', renderer: toolkit.util.formatCurrency, width: 100, },
                    {header:'Ações', dataIndex: 'actions', xtype: 'actioncolumn', scope: this, width: 60, items: this.columnActionAceptAndEdit() }
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.property.Restful',
    'corregedoria.cirdir.property.Grid'
);
