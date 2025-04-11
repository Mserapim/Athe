Ext._define('corregedoria.inspection.inspection.Manage', {
  extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('corregedoria.inspection.inspection.Grid', {
                region: 'center',
                gridAutoLoad: true,
                hideActions: ['edit', 'copy', ],
                // height: Ext.getBody().getBox().height * 0.91,
                width: Ext.getBody().getBox().width * 0.55,
                detailView: this.getTilePanel(),
                // configOrderToolBar: ['add', 'remove', '-', 'filling', '-', '->', '-', 'search', ],
                configOrderToolBar: ['filling', '-', '->', '-', 'search', ],
                hideColumns: ['operability_score', 'promptness_score', 'final_score'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
            });
            this._grid.getStore().on({
                scope: this,
                load: function(sel) {
                    // this.observerInspection();
                    // this._grid.getSelectionModel().clearSelections();
                    var selection = this._grid.getSelectionModel().getSelected();
                    if(selection){
                        this.observerInspection(selection.get('pk'));
                    } else {
                        this.observerInspection();
                    }
                },
            });
            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();
                    if(selection.length == 1){
                        this.observerInspection(selection[0].get('pk'));
                    }
                }
            });
        }
        return this._grid;
    },

    getBoxPanel: function(cfg) {
        if(!this._boxPanel)
            this._boxPanel = Ext._create('Ext.Panel', {
                region: 'west',
                split: true,
                border: false,
                width: Ext.getBody().getBox().width * 0.55,
                minWidth: Ext.getBody().getBox().width * 0.3,
                maxWidth: Ext.getBody().getBox().width * 0.8,
                layout: 'border',
                items: [
                    this.getGrid(),
                ]
            });
        return this._boxPanel;
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
                split: true,
                width: Ext.getBody().getBox().width * 0.45,
                minWidth: Ext.getBody().getBox().width * 0.2,
                maxWidth: Ext.getBody().getBox().width * 0.8
            });
        return this._tilePanel;
    },

    inspection: function(value, dispatch) {
        this._inspection = value;
        return this._inspection;
    },

    observerInspection: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(inspection) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = this.getGrid().factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                inspection: inspection
            },
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    this.getTilePanel().setPageContent(rst.content);
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};
        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Inspeções/Correições'
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getBoxPanel(cfg),
                    this.getTilePanel(cfg)
                ],
            }
        );
        corregedoria.inspection.inspection.Manage.superclass.constructor.call(this, cfg);
        this.observerInspection();
    },
});
