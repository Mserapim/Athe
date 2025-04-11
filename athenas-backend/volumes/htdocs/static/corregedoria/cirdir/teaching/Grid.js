Ext._define('corregedoria.cirdir.teaching.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.teaching.Window',
    rest: 'corregedoria.cirdir.teaching.Restful',

    configOrderToolBar: ['add', 'edit', 'remove', 'history', '->', '-', 'emptySubmit', '-', 'submit', ],

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
                          criteria_key: 2,
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
                text: 'Não exerço Docência',
                iconCls: 'icon-core icon-core-document-arrow',
                disabled: cfg.params.closed_teaching,
                scope: this,
                handler: function() {
                    this.execSubmit(cfg, true);
                }
            });
        }
        return this._emptySubmitAction;
    },

    getSubmitAction: function(cfg) {
        if(!this._submitAction) {
            this._submitAction = new Ext.Button({
                xtype: 'button',
                text: ' Submeter Docência',
                iconCls: 'icon-crgmpe icon-crgmpe-success',
                disabled: cfg.params.closed_teaching,
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
            alertTitle: 'Submetendo dados de Docência',
            params: {
                controlinformation: cfg.params.controlinformation,
                criteria: 'teaching',
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
                    {header: 'Instituição de Ensino', dataIndex: 'institution_unicode', id: 'autoExpandColumn', },
                    {header: 'Disciplina', dataIndex: 'discipline_unicode', width: 300, },
                    {header:'Ações', dataIndex: 'actions', xtype: 'actioncolumn', scope: this, width: 60, items: this.columnActionAceptAndEdit() }
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.teaching.Restful',
    'corregedoria.cirdir.teaching.Grid'
);
