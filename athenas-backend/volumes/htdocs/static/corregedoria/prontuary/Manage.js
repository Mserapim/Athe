Ext._define('corregedoria.prontuary.Manage', {
  extend: 'toolkit.widget.TabPanel',

    getProntuaryGrid: function() {
        if(!this._prontuaryGrid) {
            this._prontuaryGrid = Ext._create('corregedoria.prontuary.Grid', {
                region: 'center',
                gridAutoLoad: true,
                height: Ext.getBody().getBox().height * 0.90,
                width: Ext.getBody().getBox().width * 0.35,
                detailView: this.getTilePanel(),
                columnAction: false,
                hiddenFilter: true,
                hideItemsToolbar: ['add', 'edit', 'copy', 'remove', '-', 'download',],
                configOrderToolBar: ['menu', '-', '->', '-', 'search', ],
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });
            this._prontuaryGrid.getStore().on({
                scope: this,
                load: function(sel) {
                    this.observerProntuary();
                    this._prontuaryGrid.getSelectionModel().clearSelections();
                },
            });
            this._prontuaryGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();
                    if(selection.length == 1){
                        this.observerProntuary(selection[0].get('pk'));
                    }
                }
            });
        }

        return this._prontuaryGrid;
    },

    getBoxPanel: function(cfg) {
        if(!this._boxPanel)
            this._boxPanel = Ext._create('Ext.Panel', {
                region: 'center',
                border: false,
                autoHeight: true,
                items: [
                    this.getProntuaryGrid(),
                ]
            });
        return this._boxPanel;
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'east',
                split: true,
                width: Ext.getBody().getBox().width * 0.65,
                minWidth: Ext.getBody().getBox().width * 0.2,
                maxWidth: Ext.getBody().getBox().width * 0.8
            });
        return this._tilePanel;
    },

    prontuary: function(value, dispatch) {
        this._prontuary = value;
        return this._prontuary;
    },

    observerProntuary: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(prontuary) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = this.getProntuaryGrid().factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                prontuary: prontuary
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
                title: 'Gestor de Prontuários'
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
        corregedoria.prontuary.Manage.superclass.constructor.call(this, cfg);
        this.observerProntuary();
    },
});
