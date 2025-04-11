Ext._define('corregedoria.cnmp.Manage', {
  extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('corregedoria.cnmp.Grid', {
                region: 'center',
                gridAutoLoad: true,
                hideActions: ['edit', 'copy', ],
                // height: Ext.getBody().getBox().height * 0.91,
                width: Ext.getBody().getBox().width * 0.55,
                detailView: this.getTilePanel(),
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
            });
            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selected = sel.getSelected();
                    if(selected){
                        this.observerCommunication(selected.get('pk'));
                    } else {
                        this.observerCommunication();
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

    communication: function(value, dispatch) {
        this._communication = value;
        return this._communication;
    },

    observerCommunication: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(pk) {
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
                pk: pk
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
                title: 'Gestor de Envio - SCMMP'
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
        corregedoria.cnmp.Manage.superclass.constructor.call(this, cfg);
    },
});
